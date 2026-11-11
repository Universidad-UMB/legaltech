from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request, Response

from app.core.dependencies import DatabaseSession
from app.identity.api import CurrentSession
from app.identity.schemas import Problem
from app.publications.domain import PublicationData, PublicationVersionData
from app.publications.schemas import (
    ApprovalRequest,
    Publication,
    PublicationCreate,
    PublicationVersion,
    VersionCreate,
)
from app.publications.service import PublicationService

router = APIRouter(prefix="/api/v1/internal", tags=["Internal"])
_problem_responses: dict[int | str, dict[str, Any]] = {
    401: {"model": Problem, "description": "Authentication required."},
    403: {"model": Problem, "description": "Permission denied."},
    404: {"model": Problem, "description": "Resource not available in the authorized scope."},
    409: {"model": Problem, "description": "Conflict."},
    422: {"model": Problem, "description": "Request validation failed."},
}


def _publication_schema(item: PublicationData) -> Publication:
    return Publication(
        id=item.id,
        tracking_id=item.tracking_id,
        client_id=item.client_id,
        current_version_id=item.current_version_id,
        versions=list(item.version_ids),
    )


def _version_schema(item: PublicationVersionData) -> PublicationVersion:
    return PublicationVersion(
        id=item.id,
        publication_id=item.publication_id,
        version_number=item.version_number,
        recipient_tracking_id=item.recipient_tracking_id,
        recipient_client_id=item.recipient_client_id,
        status=item.status,
        content_text=item.content_text,
        content_sha256=item.content_sha256,
        frozen_at=item.frozen_at,
        approved_at=item.approved_at,
        published_at=item.published_at,
    )


@router.post(
    "/publications",
    status_code=201,
    response_model=Publication,
    operation_id="createPublication",
    responses={
        201: {
            "description": "Publication and initial draft created.",
            "headers": {"Location": {"schema": {"type": "string", "minLength": 1}}},
        },
        **_problem_responses,
    },
)
def create_publication(
    payload: PublicationCreate,
    request: Request,
    response: Response,
    session: DatabaseSession,
    current: CurrentSession,
) -> Publication:
    item = PublicationService().create(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        tracking_id=payload.tracking_id,
        novelty_ids=payload.novelty_ids,
        content_text=payload.content_text,
    )
    response.headers["Location"] = f"/api/v1/internal/publications/{item.id}"
    return _publication_schema(item)


@router.get(
    "/publications/{publication_id}",
    response_model=Publication,
    operation_id="getPublication",
    responses=_problem_responses,
)
def get_publication(
    request: Request,
    publication_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Publication:
    item = PublicationService().get(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        publication_id=publication_id,
    )
    return _publication_schema(item)


@router.post(
    "/publications/{publication_id}/versions",
    status_code=201,
    response_model=PublicationVersion,
    operation_id="createPublicationVersion",
    responses={
        201: {
            "description": "New draft version created.",
            "headers": {"Location": {"schema": {"type": "string", "minLength": 1}}},
        },
        **_problem_responses,
    },
)
def create_publication_version(
    payload: VersionCreate,
    request: Request,
    response: Response,
    publication_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> PublicationVersion:
    item = PublicationService().create_version(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        publication_id=publication_id,
        novelty_ids=payload.novelty_ids,
        content_text=payload.content_text,
    )
    response.headers["Location"] = f"/api/v1/internal/publication-versions/{item.id}"
    return _version_schema(item)


@router.get(
    "/publication-versions/{version_id}",
    response_model=PublicationVersion,
    operation_id="getPublicationVersion",
    responses=_problem_responses,
)
def get_publication_version(
    request: Request,
    version_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> PublicationVersion:
    item = PublicationService().get_version(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        version_id=version_id,
    )
    return _version_schema(item)


@router.post(
    "/publication-versions/{version_id}/submit",
    response_model=PublicationVersion,
    operation_id="submitPublicationVersion",
    responses=_problem_responses,
)
def submit_publication_version(
    request: Request,
    version_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> PublicationVersion:
    item = PublicationService().submit(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        version_id=version_id,
    )
    return _version_schema(item)


@router.post(
    "/publication-versions/{version_id}/decision",
    response_model=PublicationVersion,
    operation_id="decidePublicationVersion",
    responses=_problem_responses,
)
def decide_publication_version(
    payload: ApprovalRequest,
    request: Request,
    version_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> PublicationVersion:
    item = PublicationService().decide(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        version_id=version_id,
        verdict=payload.verdict,
        justification=payload.justification,
    )
    return _version_schema(item)


@router.post(
    "/publication-versions/{version_id}/publish",
    response_model=PublicationVersion,
    operation_id="publishPublicationVersion",
    responses=_problem_responses,
)
def publish_publication_version(
    request: Request,
    version_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> PublicationVersion:
    item = PublicationService().publish(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        version_id=version_id,
    )
    return _version_schema(item)
