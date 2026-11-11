from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request, Response

from app.clients.schemas import ReasonRequest
from app.core.dependencies import DatabaseSession
from app.identity.api import CurrentSession
from app.identity.schemas import Problem
from app.trackings.schemas import Process, ProcessCreate, Tracking, TrackingCreate
from app.trackings.service import TrackingService

router = APIRouter(prefix="/api/v1/internal", tags=["Internal"])
_problem_responses: dict[int | str, dict[str, Any]] = {
    401: {"model": Problem, "description": "Authentication required."},
    403: {"model": Problem, "description": "Permission denied."},
    404: {"model": Problem, "description": "Resource not available in the authorized scope."},
    409: {"model": Problem, "description": "Conflict."},
    422: {"model": Problem, "description": "Request validation failed."},
}


@router.post(
    "/processes",
    status_code=201,
    response_model=Process,
    operation_id="createProcess",
    responses={
        201: {
            "description": "Process created.",
            "headers": {"Location": {"schema": {"type": "string", "minLength": 1}}},
        },
        **{key: value for key, value in _problem_responses.items() if key not in {404}},
    },
)
def create_process(
    payload: ProcessCreate,
    request: Request,
    response: Response,
    session: DatabaseSession,
    current: CurrentSession,
) -> Process:
    created = TrackingService().create_process(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        radicado=payload.radicado,
        label=payload.label,
    )
    response.headers["Location"] = f"/api/v1/internal/processes/{created.id}"
    return Process(id=created.id, radicado=created.radicado, label=created.label)


@router.get(
    "/processes/{process_id}",
    response_model=Process,
    operation_id="getProcess",
    responses={200: {"description": "Process returned."}, **_problem_responses},
)
def get_process(
    request: Request,
    process_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Process:
    found = TrackingService().get_process(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        process_id=process_id,
    )
    return Process(id=found.id, radicado=found.radicado, label=found.label)


@router.post(
    "/trackings",
    status_code=201,
    response_model=Tracking,
    operation_id="createTracking",
    responses={
        201: {
            "description": "Tracking created.",
            "headers": {"Location": {"schema": {"type": "string", "minLength": 1}}},
        },
        **_problem_responses,
    },
)
def create_tracking(
    payload: TrackingCreate,
    request: Request,
    response: Response,
    session: DatabaseSession,
    current: CurrentSession,
) -> Tracking:
    created = TrackingService().create_tracking(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        client_id=payload.client_id,
        process_id=payload.process_id,
    )
    response.headers["Location"] = f"/api/v1/internal/trackings/{created.id}"
    return Tracking(
        id=created.id,
        tracking_code=created.tracking_code,
        client_id=created.client_id,
        process_id=created.process_id,
        status=created.status,  # type: ignore[arg-type]
        baseline_observation_id=created.baseline_observation_id,
        last_adopted_observation_id=created.last_adopted_observation_id,
    )


@router.get(
    "/trackings/{tracking_id}",
    response_model=Tracking,
    operation_id="getTracking",
    responses={200: {"description": "Tracking returned."}, **_problem_responses},
)
def get_tracking(
    request: Request,
    tracking_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Tracking:
    found = TrackingService().get_tracking(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        tracking_id=tracking_id,
    )
    return Tracking(
        id=found.id,
        tracking_code=found.tracking_code,
        client_id=found.client_id,
        process_id=found.process_id,
        status=found.status,  # type: ignore[arg-type]
        baseline_observation_id=found.baseline_observation_id,
        last_adopted_observation_id=found.last_adopted_observation_id,
    )


@router.post(
    "/trackings/{tracking_id}/activate",
    response_model=Tracking,
    operation_id="activateTracking",
    responses={200: {"description": "Tracking activated."}, **_problem_responses},
)
def activate_tracking(
    tracking_id: UUID,
    request: Request,
    session: DatabaseSession,
    current: CurrentSession,
) -> Tracking:
    activated = TrackingService().activate_tracking(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        tracking_id=tracking_id,
    )
    return Tracking(
        id=activated.id,
        tracking_code=activated.tracking_code,
        client_id=activated.client_id,
        process_id=activated.process_id,
        status=activated.status,  # type: ignore[arg-type]
        baseline_observation_id=activated.baseline_observation_id,
        last_adopted_observation_id=activated.last_adopted_observation_id,
    )


@router.post(
    "/trackings/{tracking_id}/finish",
    response_model=Tracking,
    operation_id="finishTracking",
    responses={200: {"description": "Tracking finished."}, **_problem_responses},
)
def finish_tracking(
    tracking_id: UUID,
    payload: ReasonRequest,
    request: Request,
    session: DatabaseSession,
    current: CurrentSession,
) -> Tracking:
    finished = TrackingService().finish_tracking(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        tracking_id=tracking_id,
        reason=payload.reason,
    )
    return Tracking(
        id=finished.id,
        tracking_code=finished.tracking_code,
        client_id=finished.client_id,
        process_id=finished.process_id,
        status=finished.status,  # type: ignore[arg-type]
        baseline_observation_id=finished.baseline_observation_id,
        last_adopted_observation_id=finished.last_adopted_observation_id,
    )
