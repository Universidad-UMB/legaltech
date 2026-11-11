from datetime import UTC, datetime
from typing import cast
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.acquisitions import repository as acquisition_repository
from app.acquisitions.models import Observation
from app.authorization.service import (
    authorize_internal_account,
    authorize_internal_roles,
    record_denial,
)
from app.comparisons import repository as comparison_repository
from app.core.errors import InvalidInput, ResourceConflict, ResourceNotFound
from app.identity.domain import Principal
from app.identity.models import AuditEvent
from app.novelties import repository
from app.novelties.domain import (
    EvaluationData,
    EvaluationDecision,
    NoveltyData,
    NoveltyPageData,
    NoveltyStatus,
    evaluation_decision,
    novelty_status,
    transition_novelty_status,
)
from app.novelties.models import Novelty, TrackingEvaluation
from app.trackings.repository import tracking_for_assigned_account


class EvaluationService:
    def evaluate(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        tracking_id: UUID,
        comparison_id: UUID,
    ) -> tuple[EvaluationData, bool]:
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code="COMPARISON_EVALUATE",
            allowed_roles={"ANALYST"},
        )
        try:
            with session.begin():
                tracking = tracking_for_assigned_account(
                    session,
                    tracking_id=tracking_id,
                    account_id=principal.account_id,
                    lock=True,
                )
                if tracking is None:
                    raise ResourceNotFound
                if (
                    tracking.status != "ACTIVE"
                    or repository.active_client_for_tracking(session, tracking) is None
                ):
                    raise ResourceConflict

                comparison = comparison_repository.comparison_for_tracking(
                    session, comparison_id=comparison_id, tracking=tracking
                )
                if comparison is None:
                    raise ResourceNotFound

                existing = repository.evaluation_for_tracking(
                    session, tracking_id=tracking.id, comparison_id=comparison.id
                )
                if existing is not None:
                    return self._evaluation_data(session, existing), False

                if (
                    tracking.last_adopted_observation_id is None
                    or tracking.baseline_observation_id is None
                    or comparison.old_observation_id != tracking.last_adopted_observation_id
                    or comparison.result == "NOT_COMPARABLE"
                ):
                    raise ResourceConflict

                old_observation = session.get(Observation, comparison.old_observation_id)
                if old_observation is None:
                    raise ResourceConflict
                next_observation = acquisition_repository.next_comparable_observation(
                    session,
                    process_id=tracking.process_id,
                    after=old_observation.observed_at,
                )
                if next_observation is None or next_observation.id != comparison.new_observation_id:
                    raise ResourceConflict

                changes = comparison_repository.changes_for_comparison(session, comparison.id)
                try:
                    decision, reason = evaluation_decision(comparison.result, len(changes))
                except ValueError as exc:
                    raise ResourceConflict from exc

                evaluation = repository.add_evaluation(
                    session,
                    evaluation_id=uuid4(),
                    tracking=tracking,
                    comparison=comparison,
                    decision=decision,
                    reason=reason,
                )
                if decision == "ELIGIBLE":
                    client = repository.active_client_for_tracking(session, tracking)
                    if client is None:
                        raise ResourceConflict
                    for change in changes:
                        repository.add_novelty(
                            session,
                            novelty_id=uuid4(),
                            novelty_code=repository.next_novelty_code(
                                session, client_code=client.client_code
                            ),
                            tracking=tracking,
                            comparison=comparison,
                            change_id=change.id,
                            evaluation=evaluation,
                        )
                self._audit(
                    session,
                    request_id=request_id,
                    principal=principal,
                    tracking_id=tracking.id,
                    comparison_id=comparison.id,
                )
                return self._evaluation_data(session, evaluation), True
        except ResourceNotFound:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="COMPARISON_EVALUATE",
                reason="resource_not_in_scope",
            )
            raise
        except IntegrityError as exc:
            session.rollback()
            tracking = tracking_for_assigned_account(
                session,
                tracking_id=tracking_id,
                account_id=principal.account_id,
                lock=True,
            )
            if tracking is None:
                record_denial(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code="COMPARISON_EVALUATE",
                    reason="resource_not_in_scope",
                )
                raise ResourceNotFound from exc
            existing = repository.evaluation_for_tracking(
                session, tracking_id=tracking.id, comparison_id=comparison_id
            )
            if existing is None:
                raise ResourceConflict from exc
            return self._evaluation_data(session, existing), False

    @staticmethod
    def _evaluation_data(session: Session, evaluation: TrackingEvaluation) -> EvaluationData:
        return EvaluationData(
            id=evaluation.id,
            tracking_id=evaluation.tracking_id,
            comparison_id=evaluation.comparison_id,
            decision=cast(EvaluationDecision, evaluation.decision),
            reason=evaluation.reason,
            novelty_ids=tuple(
                novelty.id
                for novelty in repository.novelties_for_evaluation(session, evaluation.id)
            ),
        )

    @staticmethod
    def _audit(
        session: Session,
        *,
        request_id: UUID,
        principal: Principal,
        tracking_id: UUID,
        comparison_id: UUID,
    ) -> None:
        session.add(
            AuditEvent(
                id=uuid4(),
                request_id=request_id,
                event_code="COMPARISON_EVALUATE",
                result="SUCCESS",
                actor_account_id=principal.account_id,
                resource_kind="TRACKING",
                resource_id=tracking_id,
                sanitized_reason=f"comparison_id={comparison_id}",
            )
        )


class NoveltyReviewService:
    def list_for_tracking(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        tracking_id: UUID,
        limit: int,
        cursor: str | None,
    ) -> NoveltyPageData:
        event_code = "NOVELTY_LIST"
        authorize_internal_account(
            session, principal=principal, request_id=request_id, event_code=event_code
        )
        try:
            with session.begin():
                page = repository.novelties_for_assigned_tracking(
                    session,
                    tracking_id=tracking_id,
                    account_id=principal.account_id,
                    limit=limit,
                    cursor=cursor,
                )
                if page is None:
                    raise ResourceNotFound
                self._audit_access(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    resource_kind="TRACKING",
                    resource_id=tracking_id,
                )
        except ResourceNotFound:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code=event_code,
                reason="resource_not_in_scope",
            )
            raise
        except ValueError as exc:
            raise InvalidInput from exc
        items, next_cursor = page
        return NoveltyPageData(
            items=tuple(self._novelty_data(item) for item in items),
            next_cursor=next_cursor,
        )

    def get(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        novelty_id: UUID,
    ) -> NoveltyData:
        event_code = "NOVELTY_GET"
        authorize_internal_account(
            session, principal=principal, request_id=request_id, event_code=event_code
        )
        try:
            with session.begin():
                novelty = repository.novelty_for_assigned_account(
                    session, novelty_id=novelty_id, account_id=principal.account_id
                )
                if novelty is None:
                    raise ResourceNotFound
                self._audit_access(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    resource_kind="NOVELTY",
                    resource_id=novelty.id,
                )
        except ResourceNotFound:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code=event_code,
                reason="resource_not_in_scope",
            )
            raise
        return self._novelty_data(novelty)

    def start_operative_review(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        novelty_id: UUID,
    ) -> NoveltyData:
        return self._transition(
            session,
            principal=principal,
            request_id=request_id,
            novelty_id=novelty_id,
            event_code="NOVELTY_START_OPERATIVE_REVIEW",
            allowed_roles={"ANALYST"},
            target_status="IN_OPERATIVE_REVIEW",
            transition_reason="Operative review started by assigned analyst.",
        )

    def escalate(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        novelty_id: UUID,
        decision: str,
        evidence_note: str,
    ) -> NoveltyData:
        return self._transition(
            session,
            principal=principal,
            request_id=request_id,
            novelty_id=novelty_id,
            event_code="NOVELTY_ESCALATE",
            allowed_roles={"ANALYST"},
            target_status="PENDING_LEGAL",
            transition_reason="Operative review completed and escalated to legal review.",
            review_kind="OPERATIVE",
            decision=decision,
            evidence_note=evidence_note,
        )

    def record_legal_review(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        novelty_id: UUID,
        decision: str,
        evidence_note: str,
    ) -> NoveltyData:
        return self._transition(
            session,
            principal=principal,
            request_id=request_id,
            novelty_id=novelty_id,
            event_code="NOVELTY_LEGAL_REVIEW",
            allowed_roles={"LAWYER"},
            target_status="TREATMENT_DEFINED",
            transition_reason="Human legal review recorded by assigned lawyer.",
            review_kind="LEGAL",
            decision=decision,
            evidence_note=evidence_note,
        )

    def _transition(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        novelty_id: UUID,
        event_code: str,
        allowed_roles: set[str],
        target_status: NoveltyStatus,
        transition_reason: str,
        review_kind: str | None = None,
        decision: str | None = None,
        evidence_note: str | None = None,
    ) -> NoveltyData:
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
            allowed_roles=allowed_roles,
        )
        try:
            with session.begin():
                novelty = repository.novelty_for_assigned_account(
                    session,
                    novelty_id=novelty_id,
                    account_id=principal.account_id,
                    lock=True,
                )
                if novelty is None:
                    raise ResourceNotFound

                try:
                    transition_novelty_status(novelty.status, target_status)
                except ValueError as exc:
                    raise ResourceConflict from exc

                if review_kind == "LEGAL":
                    operative_review = repository.review_for_kind(
                        session, novelty_id=novelty.id, review_kind="OPERATIVE"
                    )
                    if (
                        operative_review is None
                        or operative_review.actor_person_id == principal.person_id
                    ):
                        raise ResourceConflict

                from_status = novelty.status
                novelty.status = target_status
                novelty.updated_at = datetime.now(UTC)
                repository.add_state_transition(
                    session,
                    transition_id=uuid4(),
                    novelty_id=novelty.id,
                    from_state=from_status,
                    to_state=target_status,
                    actor_account_id=principal.account_id,
                    actor_person_id=principal.person_id,
                    request_id=request_id,
                    reason=transition_reason,
                )
                if review_kind is not None:
                    if decision is None or evidence_note is None:
                        raise ResourceConflict
                    repository.add_review(
                        session,
                        review_id=uuid4(),
                        novelty_id=novelty.id,
                        review_kind=review_kind,
                        actor_account_id=principal.account_id,
                        actor_person_id=principal.person_id,
                        decision=decision,
                        evidence_note=evidence_note,
                    )
                self._audit_transition(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    novelty_id=novelty.id,
                    from_status=from_status,
                    to_status=target_status,
                )
                return self._novelty_data(novelty)
        except ResourceNotFound:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code=event_code,
                reason="resource_not_in_scope",
            )
            raise
        except IntegrityError as exc:
            session.rollback()
            raise ResourceConflict from exc

    @staticmethod
    def _novelty_data(novelty: Novelty) -> NoveltyData:
        return NoveltyData(
            id=novelty.id,
            novelty_code=novelty.novelty_code,
            tracking_id=novelty.tracking_id,
            status=novelty_status(novelty.status),
            change_id=novelty.change_id,
        )

    @staticmethod
    def _audit_transition(
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        event_code: str,
        novelty_id: UUID,
        from_status: str,
        to_status: str,
    ) -> None:
        session.add(
            AuditEvent(
                id=uuid4(),
                request_id=request_id,
                event_code=event_code,
                result="SUCCESS",
                actor_account_id=principal.account_id,
                resource_kind="NOVELTY",
                resource_id=novelty_id,
                sanitized_reason=f"{from_status}->{to_status}",
            )
        )

    @staticmethod
    def _audit_access(
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        event_code: str,
        resource_kind: str,
        resource_id: UUID,
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
                sanitized_reason="authorized_internal_read",
            )
        )
