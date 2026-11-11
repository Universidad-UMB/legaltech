from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.authorization.service import (
    authorize_internal_account,
    authorize_internal_roles,
    record_denial,
)
from app.clients.models import Client
from app.core.errors import (
    ForbiddenOperation,
    InvalidInput,
    ResourceConflict,
    ResourceNotFound,
)
from app.identity.domain import Principal
from app.identity.models import AuditEvent
from app.novelties.models import Novelty
from app.publications import repository
from app.publications.domain import (
    PublicationData,
    PublicationVersionData,
    content_sha256,
    publication_status,
)
from app.publications.models import (
    Publication,
    PublicationVersion,
    PublicationVersionNovelty,
)


class PublicationService:
    def create(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        tracking_id: UUID,
        novelty_ids: list[UUID],
        content_text: str,
    ) -> PublicationData:
        event_code = "PUBLICATION_CREATE"
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
            allowed_roles={"PREPARER"},
        )
        selected_novelties = self._validated_ids(novelty_ids)
        try:
            with session.begin():
                tracking = repository.tracking_for_assigned_account(
                    session,
                    tracking_id=tracking_id,
                    account_id=principal.account_id,
                    lock=True,
                )
                if tracking is None:
                    raise ResourceNotFound
                self._require_active_tracking(
                    session, status=tracking.status, client_id=tracking.client_id
                )
                novelties = self._ready_novelties(
                    session, tracking_id=tracking.id, novelty_ids=selected_novelties
                )

                publication = Publication(
                    id=uuid4(),
                    tracking_id=tracking.id,
                    client_id=tracking.client_id,
                )
                session.add(publication)
                session.flush()
                version = self._new_version(
                    publication=publication,
                    version_number=1,
                    tracking_id=tracking.id,
                    client_id=tracking.client_id,
                    novelty_ids=selected_novelties,
                    content_text=content_text,
                )
                session.add(version)
                session.flush()
                self._add_version_components(
                    session,
                    version=version,
                    tracking_id=tracking.id,
                    novelties=novelties,
                    principal=principal,
                )
                self._transition(
                    session,
                    version_id=version.id,
                    from_state=None,
                    to_state="DRAFT",
                    principal=principal,
                    request_id=request_id,
                    reason="Initial publication draft created.",
                )
                self._audit(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    resource_kind="PUBLICATION",
                    resource_id=publication.id,
                    reason="DRAFT_CREATED",
                )
                return self._publication_data(session, publication)
        except ResourceNotFound:
            self._record_not_found(session, principal, request_id, event_code)
            raise
        except IntegrityError as exc:
            session.rollback()
            raise ResourceConflict from exc

    def get(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        publication_id: UUID,
    ) -> PublicationData:
        event_code = "PUBLICATION_GET"
        authorize_internal_account(
            session, principal=principal, request_id=request_id, event_code=event_code
        )
        try:
            with session.begin():
                publication = repository.publication_for_assigned_account(
                    session, publication_id=publication_id, account_id=principal.account_id
                )
                if publication is None:
                    raise ResourceNotFound
                data = self._publication_data(session, publication)
                self._audit(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    resource_kind="PUBLICATION",
                    resource_id=publication.id,
                    reason="authorized_internal_read",
                )
                return data
        except ResourceNotFound:
            self._record_not_found(session, principal, request_id, event_code)
            raise

    def create_version(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        publication_id: UUID,
        novelty_ids: list[UUID],
        content_text: str,
    ) -> PublicationVersionData:
        event_code = "PUBLICATION_VERSION_CREATE"
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
            allowed_roles={"PREPARER"},
        )
        selected_novelties = self._validated_ids(novelty_ids)
        try:
            with session.begin():
                publication = repository.publication_for_assigned_account(
                    session,
                    publication_id=publication_id,
                    account_id=principal.account_id,
                    lock=True,
                )
                if publication is None:
                    raise ResourceNotFound
                tracking = repository.tracking_for_assigned_account(
                    session,
                    tracking_id=publication.tracking_id,
                    account_id=principal.account_id,
                    lock=True,
                )
                if tracking is None:
                    raise ResourceNotFound
                self._require_active_tracking(
                    session,
                    status=tracking.status,
                    client_id=tracking.client_id,
                )
                if repository.has_nonterminal_version(session, publication_id=publication.id):
                    raise ResourceConflict
                novelties = self._ready_novelties(
                    session, tracking_id=tracking.id, novelty_ids=selected_novelties
                )
                version = self._new_version(
                    publication=publication,
                    version_number=repository.next_version_number(
                        session, publication_id=publication.id
                    ),
                    tracking_id=tracking.id,
                    client_id=tracking.client_id,
                    novelty_ids=selected_novelties,
                    content_text=content_text,
                )
                session.add(version)
                session.flush()
                self._add_version_components(
                    session,
                    version=version,
                    tracking_id=tracking.id,
                    novelties=novelties,
                    principal=principal,
                )
                self._transition(
                    session,
                    version_id=version.id,
                    from_state=None,
                    to_state="DRAFT",
                    principal=principal,
                    request_id=request_id,
                    reason="New publication version drafted; prior authorization was not copied.",
                )
                self._audit(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    resource_kind="PUBLICATION_VERSION",
                    resource_id=version.id,
                    reason="DRAFT_CREATED",
                )
                return self._version_data(version)
        except ResourceNotFound:
            self._record_not_found(session, principal, request_id, event_code)
            raise
        except IntegrityError as exc:
            session.rollback()
            raise ResourceConflict from exc

    def get_version(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        version_id: UUID,
    ) -> PublicationVersionData:
        event_code = "PUBLICATION_VERSION_GET"
        authorize_internal_account(
            session, principal=principal, request_id=request_id, event_code=event_code
        )
        try:
            with session.begin():
                result = repository.version_for_assigned_account(
                    session, version_id=version_id, account_id=principal.account_id
                )
                if result is None:
                    raise ResourceNotFound
                version, _ = result
                data = self._version_data(version)
                self._audit(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    resource_kind="PUBLICATION_VERSION",
                    resource_id=version.id,
                    reason="authorized_internal_read",
                )
                return data
        except ResourceNotFound:
            self._record_not_found(session, principal, request_id, event_code)
            raise

    def submit(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        version_id: UUID,
    ) -> PublicationVersionData:
        event_code = "PUBLICATION_VERSION_SUBMIT"
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
            allowed_roles={"PREPARER"},
        )
        try:
            with session.begin():
                result = repository.version_for_assigned_account(
                    session,
                    version_id=version_id,
                    account_id=principal.account_id,
                    lock=True,
                )
                if result is None:
                    raise ResourceNotFound
                version, publication = result
                self._require_active_tracking(
                    session,
                    status=self._tracking_status(session, publication.tracking_id),
                    client_id=publication.client_id,
                )
                if version.status != "DRAFT":
                    raise ResourceConflict
                if principal.person_id not in repository.preparer_person_ids(
                    session, version_id=version.id
                ):
                    raise ForbiddenOperation
                self._require_frozen_hash(version)
                novelty_rows = tuple(
                    session.scalars(
                        select(PublicationVersionNovelty).where(
                            PublicationVersionNovelty.version_id == version.id
                        )
                    )
                )
                if not novelty_rows:
                    raise ResourceConflict
                for link in novelty_rows:
                    self._require_ready_novelty(
                        session, tracking_id=link.tracking_id, novelty_id=link.novelty_id
                    )
                version.status = "PENDING_APPROVAL"
                version.frozen_at = datetime.now(UTC)
                self._transition(
                    session,
                    version_id=version.id,
                    from_state="DRAFT",
                    to_state="PENDING_APPROVAL",
                    principal=principal,
                    request_id=request_id,
                    reason="Exact content and recipients submitted for independent authorization.",
                )
                self._audit(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    resource_kind="PUBLICATION_VERSION",
                    resource_id=version.id,
                    reason="DRAFT_SUBMITTED",
                )
                return self._version_data(version)
        except ResourceNotFound:
            self._record_not_found(session, principal, request_id, event_code)
            raise
        except ForbiddenOperation:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code=event_code,
                reason="permission_denied",
            )
            raise
        except IntegrityError as exc:
            session.rollback()
            raise ResourceConflict from exc

    def decide(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        version_id: UUID,
        verdict: str,
        justification: str,
    ) -> PublicationVersionData:
        event_code = "PUBLICATION_VERSION_DECIDE"
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
            allowed_roles={"COORDINATOR"},
        )
        try:
            with session.begin():
                result = repository.version_for_assigned_account(
                    session,
                    version_id=version_id,
                    account_id=principal.account_id,
                    lock=True,
                )
                if result is None:
                    raise ResourceNotFound
                version, publication = result
                self._require_active_tracking(
                    session,
                    status=self._tracking_status(session, publication.tracking_id),
                    client_id=publication.client_id,
                )
                if version.status != "PENDING_APPROVAL":
                    raise ResourceConflict
                if principal.person_id in repository.preparer_person_ids(
                    session, version_id=version.id
                ):
                    raise ForbiddenOperation
                self._require_frozen_hash(version)
                repository.add_approval(
                    session,
                    approval_id=uuid4(),
                    version_id=version.id,
                    approver_account_id=principal.account_id,
                    approver_person_id=principal.person_id,
                    verdict=verdict,
                    snapshot_sha256=version.content_sha256,
                    justification=justification,
                )
                from_state = version.status
                version.status = "APPROVED" if verdict == "APPROVE" else "REJECTED"
                version.approved_at = datetime.now(UTC) if verdict == "APPROVE" else None
                self._transition(
                    session,
                    version_id=version.id,
                    from_state=from_state,
                    to_state=version.status,
                    principal=principal,
                    request_id=request_id,
                    reason=f"Independent coordinator recorded {verdict.lower()} decision.",
                )
                self._audit(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    resource_kind="PUBLICATION_VERSION",
                    resource_id=version.id,
                    reason=verdict,
                )
                return self._version_data(version)
        except ResourceNotFound:
            self._record_not_found(session, principal, request_id, event_code)
            raise
        except ForbiddenOperation:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code=event_code,
                reason="permission_denied",
            )
            raise
        except IntegrityError as exc:
            session.rollback()
            raise ResourceConflict from exc

    def publish(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        version_id: UUID,
    ) -> PublicationVersionData:
        event_code = "PUBLICATION_VERSION_PUBLISH"
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
            allowed_roles={"COORDINATOR"},
        )
        try:
            with session.begin():
                result = repository.version_for_assigned_account(
                    session,
                    version_id=version_id,
                    account_id=principal.account_id,
                    lock=True,
                )
                if result is None:
                    raise ResourceNotFound
                version, publication = result
                self._require_active_tracking(
                    session,
                    status=self._tracking_status(session, publication.tracking_id),
                    client_id=publication.client_id,
                )
                if version.status != "APPROVED":
                    raise ResourceConflict
                approval = repository.approval_for_version(session, version_id=version.id)
                if (
                    approval is None
                    or approval.verdict != "APPROVE"
                    or approval.snapshot_sha256 != version.content_sha256
                ):
                    raise ResourceConflict
                self._require_frozen_hash(version)
                from_state = version.status
                version.status = "PUBLISHED"
                version.published_at = datetime.now(UTC)
                session.flush()
                repository.update_current_version(
                    session, publication=publication, version_id=version.id
                )
                self._transition(
                    session,
                    version_id=version.id,
                    from_state=from_state,
                    to_state="PUBLISHED",
                    principal=principal,
                    request_id=request_id,
                    reason="Approved version selected as the local current publication.",
                )
                self._audit(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    resource_kind="PUBLICATION_VERSION",
                    resource_id=version.id,
                    reason="PUBLISHED_CURRENT",
                )
                return self._version_data(version)
        except ResourceNotFound:
            self._record_not_found(session, principal, request_id, event_code)
            raise
        except IntegrityError as exc:
            session.rollback()
            raise ResourceConflict from exc

    @staticmethod
    def _validated_ids(novelty_ids: list[UUID]) -> tuple[UUID, ...]:
        if not novelty_ids or len(set(novelty_ids)) != len(novelty_ids):
            raise InvalidInput
        return tuple(novelty_ids)

    @staticmethod
    def _new_version(
        *,
        publication: Publication,
        version_number: int,
        tracking_id: UUID,
        client_id: UUID,
        novelty_ids: tuple[UUID, ...],
        content_text: str,
    ) -> PublicationVersion:
        if not novelty_ids:
            raise InvalidInput
        return PublicationVersion(
            id=uuid4(),
            publication_id=publication.id,
            version_number=version_number,
            recipient_tracking_id=tracking_id,
            recipient_client_id=client_id,
            status="DRAFT",
            content_text=content_text,
            content_sha256=content_sha256(content_text),
        )

    @staticmethod
    def _add_version_components(
        session: Session,
        *,
        version: PublicationVersion,
        tracking_id: UUID,
        novelties: tuple[Novelty, ...],
        principal: Principal,
    ) -> None:
        repository.add_preparer(
            session,
            version_id=version.id,
            person_id=principal.person_id,
            account_id=principal.account_id,
        )
        for novelty in novelties:
            repository.add_version_novelty(
                session,
                version_id=version.id,
                tracking_id=tracking_id,
                novelty_id=novelty.id,
            )
        session.flush()

    @staticmethod
    def _ready_novelties(
        session: Session, *, tracking_id: UUID, novelty_ids: tuple[UUID, ...]
    ) -> tuple[Novelty, ...]:
        novelties = repository.novelties_for_tracking(
            session, tracking_id=tracking_id, novelty_ids=novelty_ids
        )
        if len(novelties) != len(novelty_ids):
            raise ResourceNotFound
        for novelty in novelties:
            PublicationService._require_ready_novelty(
                session, tracking_id=tracking_id, novelty_id=novelty.id
            )
        return novelties

    @staticmethod
    def _require_ready_novelty(session: Session, *, tracking_id: UUID, novelty_id: UUID) -> None:
        novelty = session.scalar(
            select(Novelty).where(
                Novelty.id == novelty_id,
                Novelty.tracking_id == tracking_id,
            )
        )
        if novelty is None:
            raise ResourceNotFound
        if novelty.status != "TREATMENT_DEFINED" or not repository.has_legal_review(
            session, novelty_id=novelty.id
        ):
            raise ResourceConflict

    @staticmethod
    def _require_active_tracking(session: Session, *, status: str, client_id: UUID) -> None:
        client = session.scalar(select(Client).where(Client.id == client_id))
        if status != "ACTIVE" or client is None or client.status != "ACTIVE":
            raise ResourceConflict

    @staticmethod
    def _tracking_status(session: Session, tracking_id: UUID) -> str:
        from app.trackings.models import Tracking

        status = session.scalar(select(Tracking.status).where(Tracking.id == tracking_id))
        if status is None:
            raise ResourceNotFound
        return status

    @staticmethod
    def _require_frozen_hash(version: PublicationVersion) -> None:
        if content_sha256(version.content_text) != version.content_sha256:
            raise ResourceConflict

    @staticmethod
    def _publication_data(session: Session, publication: Publication) -> PublicationData:
        return PublicationData(
            id=publication.id,
            tracking_id=publication.tracking_id,
            client_id=publication.client_id,
            current_version_id=publication.current_version_id,
            version_ids=repository.version_ids(session, publication_id=publication.id),
        )

    @staticmethod
    def _version_data(version: PublicationVersion) -> PublicationVersionData:
        return PublicationVersionData(
            id=version.id,
            publication_id=version.publication_id,
            version_number=version.version_number,
            recipient_tracking_id=version.recipient_tracking_id,
            recipient_client_id=version.recipient_client_id,
            status=publication_status(version.status),
            content_text=version.content_text,
            content_sha256=version.content_sha256,
            frozen_at=version.frozen_at,
            approved_at=version.approved_at,
            published_at=version.published_at,
        )

    @staticmethod
    def _transition(
        session: Session,
        *,
        version_id: UUID,
        from_state: str | None,
        to_state: str,
        principal: Principal,
        request_id: UUID,
        reason: str,
    ) -> None:
        repository.add_state_transition(
            session,
            transition_id=uuid4(),
            version_id=version_id,
            from_state=from_state,
            to_state=to_state,
            actor_account_id=principal.account_id,
            actor_person_id=principal.person_id,
            request_id=request_id,
            reason=reason,
        )

    @staticmethod
    def _audit(
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        event_code: str,
        resource_kind: str,
        resource_id: UUID,
        reason: str,
    ) -> None:
        session.add(
            AuditEvent(
                id=uuid4(),
                request_id=request_id,
                event_code=event_code,
                result="SUCCESS",
                actor_account_id=principal.account_id,
                resource_kind=resource_kind,
                resource_id=resource_id,
                sanitized_reason=reason,
            )
        )

    @staticmethod
    def _record_not_found(
        session: Session, principal: Principal, request_id: UUID, event_code: str
    ) -> None:
        record_denial(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
            reason="resource_not_in_scope",
        )
