from datetime import datetime
from typing import Any, cast
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Subquery

from app.acquisitions.models import AcquisitionRun, Observation
from app.clients.models import Client
from app.portal.domain import (
    PortalPublicationData,
    PortalPublicationResultData,
    PortalTrackingData,
    PortalTrackingPageData,
    decode_portal_cursor,
    encode_portal_cursor,
    portal_coverage_status,
)
from app.publications.models import Publication, PublicationVersion
from app.trackings.models import ExternalTrackingScope, JudicialProcess, Tracking


def _latest_acquisition_subquery() -> Subquery[Any]:
    run_rank = (
        func.row_number()
        .over(
            partition_by=AcquisitionRun.process_id,
            order_by=(AcquisitionRun.requested_at.desc(), AcquisitionRun.id.desc()),
        )
        .label("run_rank")
    )
    return select(
        AcquisitionRun.id.label("run_id"),
        AcquisitionRun.process_id.label("process_id"),
        AcquisitionRun.status.label("run_status"),
        run_rank,
    ).subquery("portal_latest_run_ranked")


def _latest_publication_subquery() -> Subquery[Any]:
    publication_rank = (
        func.row_number()
        .over(
            partition_by=Publication.tracking_id,
            order_by=(PublicationVersion.published_at.desc(), PublicationVersion.id.desc()),
        )
        .label("publication_rank")
    )
    ranked = (
        select(
            Publication.tracking_id.label("tracking_id"),
            PublicationVersion.id.label("version_id"),
            PublicationVersion.published_at.label("published_at"),
            PublicationVersion.content_text.label("content_text"),
            publication_rank,
        )
        .join(PublicationVersion, PublicationVersion.id == Publication.current_version_id)
        .where(
            PublicationVersion.status == "PUBLISHED",
            PublicationVersion.published_at.is_not(None),
        )
        .subquery("portal_published_ranked")
    )
    return (
        select(
            ranked.c.tracking_id,
            ranked.c.version_id,
            ranked.c.published_at,
            ranked.c.content_text,
        )
        .where(ranked.c.publication_rank == 1)
        .subquery("portal_current_publication")
    )


def visible_tracking_page(
    session: Session,
    *,
    account_id: UUID,
    client_id: UUID | None,
    limit: int,
    cursor: str | None,
) -> PortalTrackingPageData:
    cursor_id = decode_portal_cursor(cursor) if cursor is not None else None
    latest_run = _latest_acquisition_subquery()
    latest_publication = _latest_publication_subquery()
    statement = (
        select(
            Tracking.id,
            Tracking.tracking_code,
            JudicialProcess.radicado,
            latest_publication.c.version_id,
            latest_run.c.run_status,
            Observation.quality,
        )
        .select_from(Tracking)
        .join(Client, Client.id == Tracking.client_id)
        .join(JudicialProcess, JudicialProcess.id == Tracking.process_id)
        .join(
            ExternalTrackingScope,
            and_(
                ExternalTrackingScope.tracking_id == Tracking.id,
                ExternalTrackingScope.client_id == client_id,
                ExternalTrackingScope.account_id == account_id,
                ExternalTrackingScope.permission_code == "READ_PUBLICATIONS",
                ExternalTrackingScope.revoked_at.is_(None),
            ),
        )
        .outerjoin(latest_publication, latest_publication.c.tracking_id == Tracking.id)
        .outerjoin(
            latest_run,
            and_(latest_run.c.process_id == Tracking.process_id, latest_run.c.run_rank == 1),
        )
        .outerjoin(Observation, Observation.acquisition_run_id == latest_run.c.run_id)
        .where(
            Tracking.client_id == client_id,
            Tracking.status == "ACTIVE",
            Client.status == "ACTIVE",
        )
        .order_by(Tracking.id)
        .limit(limit + 1)
        .with_for_update(read=True, of=(Client, Tracking))
    )
    if cursor_id is not None:
        statement = statement.where(Tracking.id > cursor_id)

    rows = session.execute(statement).all()
    visible_rows = rows[:limit]
    items = tuple(
        PortalTrackingData(
            id=row[0],
            tracking_code=row[1],
            radicado=row[2],
            has_publication=row[3] is not None,
            coverage_status=portal_coverage_status(row[4], row[5]),
        )
        for row in visible_rows
    )
    next_cursor = encode_portal_cursor(items[-1].id) if len(rows) > limit else None
    return PortalTrackingPageData(items=items, next_cursor=next_cursor)


def current_publication_for_tracking(
    session: Session,
    *,
    account_id: UUID,
    client_id: UUID | None,
    tracking_id: UUID,
) -> PortalPublicationResultData | None:
    latest_run = _latest_acquisition_subquery()
    latest_publication = _latest_publication_subquery()
    row = session.execute(
        select(
            latest_publication.c.version_id,
            latest_publication.c.published_at,
            latest_publication.c.content_text,
            latest_run.c.run_status,
            Observation.quality,
        )
        .select_from(Tracking)
        .join(Client, Client.id == Tracking.client_id)
        .join(
            ExternalTrackingScope,
            and_(
                ExternalTrackingScope.tracking_id == Tracking.id,
                ExternalTrackingScope.client_id == client_id,
                ExternalTrackingScope.account_id == account_id,
                ExternalTrackingScope.permission_code == "READ_PUBLICATIONS",
                ExternalTrackingScope.revoked_at.is_(None),
            ),
        )
        .outerjoin(latest_publication, latest_publication.c.tracking_id == Tracking.id)
        .outerjoin(
            latest_run,
            and_(latest_run.c.process_id == Tracking.process_id, latest_run.c.run_rank == 1),
        )
        .outerjoin(Observation, Observation.acquisition_run_id == latest_run.c.run_id)
        .where(
            Tracking.id == tracking_id,
            Tracking.client_id == client_id,
            Tracking.status == "ACTIVE",
            Client.status == "ACTIVE",
        )
        .with_for_update(read=True, of=(Client, Tracking))
    ).one_or_none()
    if row is None:
        return None

    version_id = cast(UUID | None, row[0])
    published_at = cast(datetime | None, row[1])
    content_text = cast(str | None, row[2])
    run_status = cast(str | None, row[3])
    quality = cast(str | None, row[4])
    publication = (
        PortalPublicationData(
            version_id=version_id,
            published_at=published_at,
            content_text=content_text,
        )
        if version_id is not None and published_at is not None and content_text is not None
        else None
    )
    return PortalPublicationResultData(
        available=publication is not None,
        coverage_status=portal_coverage_status(run_status, quality),
        publication=publication,
    )
