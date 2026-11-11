from typing import cast
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.acquisitions import repository as acquisition_repository
from app.acquisitions.models import Observation
from app.authorization.service import authorize_internal_roles, record_denial
from app.comparisons import repository as comparison_repository
from app.core.errors import ResourceConflict, ResourceNotFound
from app.identity.domain import Principal
from app.identity.models import AuditEvent
from app.novelties import repository
from app.novelties.domain import EvaluationData, EvaluationDecision, evaluation_decision
from app.novelties.models import TrackingEvaluation
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
