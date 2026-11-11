from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request, Response

from app.core.dependencies import DatabaseSession
from app.identity.api import CurrentSession
from app.identity.schemas import Problem
from app.novelties.domain import EvaluationData
from app.novelties.schemas import Evaluation, EvaluationCreate
from app.novelties.service import EvaluationService

router = APIRouter(prefix="/api/v1/internal", tags=["Internal"])
_problem_responses: dict[int | str, dict[str, Any]] = {
    401: {"model": Problem, "description": "Authentication required."},
    403: {"model": Problem, "description": "Permission denied."},
    404: {"model": Problem, "description": "Resource not available in the authorized scope."},
    409: {"model": Problem, "description": "Conflict."},
    422: {"model": Problem, "description": "Request validation failed."},
}


def _schema(item: EvaluationData) -> Evaluation:
    return Evaluation(
        id=item.id,
        tracking_id=item.tracking_id,
        comparison_id=item.comparison_id,
        decision=item.decision,
        reason=item.reason,
        novelty_ids=list(item.novelty_ids),
    )


@router.post(
    "/trackings/{tracking_id}/evaluations",
    status_code=201,
    response_model=Evaluation,
    operation_id="evaluateComparison",
    responses={
        200: {"model": Evaluation, "description": "Existing evaluation replayed."},
        201: {
            "description": "Evaluation created.",
            "headers": {"Location": {"schema": {"type": "string", "minLength": 1}}},
        },
        **_problem_responses,
    },
)
def evaluate_comparison(
    payload: EvaluationCreate,
    request: Request,
    response: Response,
    tracking_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Evaluation:
    item, created = EvaluationService().evaluate(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        tracking_id=tracking_id,
        comparison_id=payload.comparison_id,
    )
    if created:
        response.headers["Location"] = (
            f"/api/v1/internal/trackings/{tracking_id}/evaluations/{item.id}"
        )
    else:
        response.status_code = 200
    return _schema(item)
