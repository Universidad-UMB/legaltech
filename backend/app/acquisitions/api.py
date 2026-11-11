from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request, Response

from app.acquisitions.schemas import (
    Acquisition,
    AcquisitionCreate,
    AdoptionResult,
    AdoptObservationRequest,
    Observation,
    ObservedAction,
)
from app.acquisitions.service import AcquisitionService
from app.core.dependencies import DatabaseSession
from app.identity.api import CurrentSession
from app.identity.schemas import Problem
from app.trackings.schemas import Tracking

router = APIRouter(prefix="/api/v1/internal", tags=["Internal"])
_problem_responses: dict[int | str, dict[str, Any]] = {
    401: {"model": Problem, "description": "Authentication required."},
    403: {"model": Problem, "description": "Permission denied."},
    404: {"model": Problem, "description": "Resource not available in the authorized scope."},
    409: {"model": Problem, "description": "Conflict."},
    422: {"model": Problem, "description": "Request validation failed."},
}


@router.post(
    "/acquisition-runs",
    status_code=201,
    response_model=Acquisition,
    operation_id="createAcquisition",
    responses={
        200: {"model": Acquisition, "description": "Existing acquisition replayed."},
        201: {
            "description": "Acquisition created.",
            "headers": {"Location": {"schema": {"type": "string", "minLength": 1}}},
        },
        **_problem_responses,
    },
)
def create_acquisition(
    payload: AcquisitionCreate,
    request: Request,
    response: Response,
    session: DatabaseSession,
    current: CurrentSession,
) -> Acquisition:
    result = AcquisitionService().create(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        process_id=payload.process_id,
        fixture_code=payload.fixture_code,
        request_key=payload.request_key,
    )
    if result.created:
        response.headers["Location"] = f"/api/v1/internal/acquisition-runs/{result.acquisition.id}"
    else:
        response.status_code = 200
    item = result.acquisition
    return Acquisition(
        id=item.id,
        process_id=item.process_id,
        source_code=item.source_code,
        status=item.status,
        request_key=item.request_key,
        observation_id=item.observation_id,
        error_code=item.error_code,
        coverage_note=item.coverage_note,
    )


@router.get(
    "/acquisition-runs/{run_id}",
    response_model=Acquisition,
    operation_id="getAcquisition",
    responses={200: {"description": "Acquisition returned."}, **_problem_responses},
)
def get_acquisition(
    request: Request,
    run_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Acquisition:
    found = AcquisitionService().get_acquisition(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        run_id=run_id,
    )
    return Acquisition(
        id=found.id,
        process_id=found.process_id,
        source_code=found.source_code,
        status=found.status,
        request_key=found.request_key,
        observation_id=found.observation_id,
        error_code=found.error_code,
        coverage_note=found.coverage_note,
    )


@router.get(
    "/observations/{observation_id}",
    response_model=Observation,
    operation_id="getObservation",
    responses={200: {"description": "Observation returned."}, **_problem_responses},
)
def get_observation(
    request: Request,
    observation_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Observation:
    found = AcquisitionService().get_observation(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        observation_id=observation_id,
    )
    return Observation(
        id=found.id,
        process_id=found.process_id,
        quality=found.quality,
        sealed=found.sealed,
        observed_at=found.observed_at,
        actions=[
            ObservedAction(
                action_key=action.action_key,
                description=action.description,
                occurred_on=action.occurred_on,
            )
            for action in found.actions
        ],
        coverage_note=found.coverage_note,
    )


@router.post(
    "/trackings/{tracking_id}/adoptions",
    response_model=AdoptionResult,
    operation_id="adoptObservation",
    responses={200: {"description": "Observation adopted."}, **_problem_responses},
)
def adopt_observation(
    payload: AdoptObservationRequest,
    request: Request,
    tracking_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> AdoptionResult:
    tracking, outcome = AcquisitionService().adopt_observation(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        tracking_id=tracking_id,
        observation_id=payload.observation_id,
    )
    return AdoptionResult(
        tracking=Tracking(
            id=tracking.id,
            tracking_code=tracking.tracking_code,
            client_id=tracking.client_id,
            process_id=tracking.process_id,
            status=tracking.status,  # type: ignore[arg-type]
            baseline_observation_id=tracking.baseline_observation_id,
            last_adopted_observation_id=tracking.last_adopted_observation_id,
        ),
        outcome=outcome,
    )
