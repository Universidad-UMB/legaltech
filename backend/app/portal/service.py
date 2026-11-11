from uuid import UUID

from sqlalchemy.orm import Session

from app.audit import repository as audit_repository
from app.authorization.service import authorize_external_reader, record_denial
from app.core.errors import InvalidInput, ResourceNotFound
from app.identity.domain import Principal
from app.portal import repository
from app.portal.domain import PortalPublicationResultData, PortalTrackingPageData


class PortalService:
    def list_trackings(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        limit: int,
        cursor: str | None,
    ) -> PortalTrackingPageData:
        event_code = "PORTAL_TRACKINGS_LIST"
        authorize_external_reader(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
        )
        try:
            with session.begin():
                page = repository.visible_tracking_page(
                    session,
                    account_id=principal.account_id,
                    client_id=principal.client_id,
                    limit=limit,
                    cursor=cursor,
                )
                if principal.client_id is not None:
                    audit_repository.add_portal_read_event(
                        session,
                        principal=principal,
                        request_id=request_id,
                        event_code=event_code,
                        resource_kind="CLIENT",
                        resource_id=principal.client_id,
                    )
                return page
        except ValueError as exc:
            raise InvalidInput from exc

    def current_publication(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        tracking_id: UUID,
    ) -> PortalPublicationResultData:
        event_code = "PORTAL_CURRENT_PUBLICATION"
        authorize_external_reader(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
        )
        try:
            with session.begin():
                result = repository.current_publication_for_tracking(
                    session,
                    account_id=principal.account_id,
                    client_id=principal.client_id,
                    tracking_id=tracking_id,
                )
                if result is None:
                    raise ResourceNotFound
                audit_repository.add_portal_read_event(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    resource_kind="TRACKING",
                    resource_id=tracking_id,
                )
                return result
        except ResourceNotFound:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code=event_code,
                reason="resource_not_in_scope",
            )
            raise
