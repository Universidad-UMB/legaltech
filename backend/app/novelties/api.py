from typing import Any
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response

from app.core.dependencies import DatabaseSession
from app.identity.api import CurrentSession
from app.identity.schemas import Problem
from app.novelties.domain import EvaluationData, NoveltyData, NoveltyPageData
from app.novelties.schemas import (
    Evaluation,
    EvaluationCreate,
    LegalReview,
    Novelty,
    NoveltyList,
    OperativeEscalation,
)
from app.novelties.service import EvaluationService, NoveltyReviewService

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


def _novelty_schema(item: NoveltyData) -> Novelty:
    return Novelty(
        id=item.id,
        novelty_code=item.novelty_code,
        tracking_id=item.tracking_id,
        status=item.status,
        change_id=item.change_id,
    )


def _novelty_page_schema(page: NoveltyPageData) -> NoveltyList:
    return NoveltyList(
        items=[_novelty_schema(item) for item in page.items],
        next_cursor=page.next_cursor,
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


@router.get(
    "/trackings/{tracking_id}/novelties",
    response_model=NoveltyList,
    operation_id="listNovelties",
    responses={
        401: _problem_responses[401],
        403: _problem_responses[403],
        404: _problem_responses[404],
        422: _problem_responses[422],
    },
)
def list_novelties(
    request: Request,
    tracking_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
    limit: int = Query(default=25, ge=1, le=100),
    cursor: str | None = Query(default=None, min_length=1),
) -> NoveltyList:
    page = NoveltyReviewService().list_for_tracking(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        tracking_id=tracking_id,
        limit=limit,
        cursor=cursor,
    )
    return _novelty_page_schema(page)


@router.get(
    "/novelties/{novelty_id}",
    response_model=Novelty,
    operation_id="getNovelty",
    responses=_problem_responses,
)
def get_novelty(
    request: Request,
    novelty_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Novelty:
    item = NoveltyReviewService().get(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        novelty_id=novelty_id,
    )
    return _novelty_schema(item)


@router.post(
    "/novelties/{novelty_id}/start-operative-review",
    response_model=Novelty,
    operation_id="startOperativeReview",
    responses=_problem_responses,
)
def start_operative_review(
    request: Request,
    novelty_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Novelty:
    item = NoveltyReviewService().start_operative_review(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        novelty_id=novelty_id,
    )
    return _novelty_schema(item)


@router.post(
    "/novelties/{novelty_id}/escalate",
    response_model=Novelty,
    operation_id="escalateNovelty",
    responses=_problem_responses,
)
def escalate_novelty(
    payload: OperativeEscalation,
    request: Request,
    novelty_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Novelty:
    item = NoveltyReviewService().escalate(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        novelty_id=novelty_id,
        decision=payload.decision,
        evidence_note=payload.evidence_note,
    )
    return _novelty_schema(item)


@router.post(
    "/novelties/{novelty_id}/legal-review",
    response_model=Novelty,
    operation_id="recordLegalReview",
    responses=_problem_responses,
)
def record_legal_review(
    payload: LegalReview,
    request: Request,
    novelty_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Novelty:
    item = NoveltyReviewService().record_legal_review(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        novelty_id=novelty_id,
        decision=payload.decision,
        evidence_note=payload.evidence_note,
    )
    return _novelty_schema(item)
