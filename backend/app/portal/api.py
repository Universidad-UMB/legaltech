from typing import Any
from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.core.dependencies import DatabaseSession
from app.core.errors import InvalidInput
from app.identity.api import CurrentSession
from app.identity.schemas import Problem
from app.portal.domain import PortalPublicationResultData
from app.portal.schemas import (
    PortalPublication,
    PortalPublicationResult,
    PortalTracking,
    PortalTrackingList,
)
from app.portal.service import PortalService

router = APIRouter(prefix="/api/v1/portal", tags=["Portal"])
_problem_responses: dict[int | str, dict[str, Any]] = {
    401: {"model": Problem, "description": "Authentication required."},
    403: {"model": Problem, "description": "Permission denied."},
    404: {"model": Problem, "description": "Resource not available in the authorized scope."},
    422: {"model": Problem, "description": "Request validation failed."},
}


@router.get(
    "/trackings",
    response_model=PortalTrackingList,
    operation_id="portalTrackings",
    responses={
        200: {"description": "Authorized trackings returned."},
        **{key: value for key, value in _problem_responses.items() if key != 404},
    },
)
def portal_trackings(
    request: Request,
    session: DatabaseSession,
    current: CurrentSession,
    limit: int = Query(default=25, ge=1, le=100),
    cursor: str | None = Query(default=None, min_length=1),
) -> PortalTrackingList:
    if set(request.query_params.keys()) - {"limit", "cursor"}:
        raise InvalidInput
    page = PortalService().list_trackings(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        limit=limit,
        cursor=cursor,
    )
    return PortalTrackingList(
        items=[
            PortalTracking(
                id=item.id,
                tracking_code=item.tracking_code,
                radicado=item.radicado,
                has_publication=item.has_publication,
                coverage_status=item.coverage_status,
            )
            for item in page.items
        ],
        next_cursor=page.next_cursor,
    )


@router.get(
    "/trackings/{tracking_id}/current-publication",
    response_model=PortalPublicationResult,
    operation_id="portalCurrentPublication",
    responses={
        200: {"description": "Current publication or authorized absence returned."},
        **_problem_responses,
    },
)
def portal_current_publication(
    tracking_id: UUID,
    request: Request,
    session: DatabaseSession,
    current: CurrentSession,
) -> PortalPublicationResult:
    result = PortalService().current_publication(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        tracking_id=tracking_id,
    )
    return _publication_result(result)


def _publication_result(data: PortalPublicationResultData) -> PortalPublicationResult:
    publication = (
        PortalPublication(
            version_id=data.publication.version_id,
            published_at=data.publication.published_at,
            content_text=data.publication.content_text,
        )
        if data.publication is not None
        else None
    )
    return PortalPublicationResult(
        available=data.available,
        coverage_status=data.coverage_status,
        publication=publication,
    )
