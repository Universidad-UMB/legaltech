from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request, Response

from app.comparisons.domain import ComparisonData
from app.comparisons.schemas import Comparison, ComparisonCreate, TechnicalChange
from app.comparisons.service import ComparisonService
from app.core.dependencies import DatabaseSession
from app.identity.api import CurrentSession
from app.identity.schemas import Problem

router = APIRouter(prefix="/api/v1/internal", tags=["Internal"])
_problem_responses: dict[int | str, dict[str, Any]] = {
    401: {"model": Problem, "description": "Authentication required."},
    403: {"model": Problem, "description": "Permission denied."},
    404: {"model": Problem, "description": "Resource not available in the authorized scope."},
    409: {"model": Problem, "description": "Conflict."},
    422: {"model": Problem, "description": "Request validation failed."},
}


def _schema(item: ComparisonData) -> Comparison:
    return Comparison(
        id=item.id,
        process_id=item.process_id,
        old_observation_id=item.old_observation_id,
        new_observation_id=item.new_observation_id,
        rule_version=item.rule_version,
        result=item.result,
        changes=[
            TechnicalChange(
                id=change.id,
                action_key=change.action_key,
                change_kind=change.change_kind,
                evidence=change.evidence,
            )
            for change in item.changes
        ],
    )


@router.post(
    "/comparisons",
    status_code=201,
    response_model=Comparison,
    operation_id="compareObservations",
    responses={
        200: {"model": Comparison, "description": "Existing comparison replayed."},
        201: {
            "description": "Comparison created.",
            "headers": {"Location": {"schema": {"type": "string", "minLength": 1}}},
        },
        **_problem_responses,
    },
)
def compare_observations(
    payload: ComparisonCreate,
    request: Request,
    response: Response,
    session: DatabaseSession,
    current: CurrentSession,
) -> Comparison:
    item, created = ComparisonService().compare(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        old_observation_id=payload.old_observation_id,
        new_observation_id=payload.new_observation_id,
        rule_version=payload.rule_version,
    )
    if created:
        response.headers["Location"] = f"/api/v1/internal/comparisons/{item.id}"
    else:
        response.status_code = 200
    return _schema(item)


@router.get(
    "/comparisons/{comparison_id}",
    response_model=Comparison,
    operation_id="getComparison",
    responses={200: {"description": "Comparison returned."}, **_problem_responses},
)
def get_comparison(
    request: Request,
    comparison_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Comparison:
    item = ComparisonService().get(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        comparison_id=comparison_id,
    )
    return _schema(item)
