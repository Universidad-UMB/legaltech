from typing import Literal, cast
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.acquisitions import repository as acquisition_repository
from app.authorization.service import (
    authorize_internal_account,
    authorize_internal_roles,
    record_denial,
)
from app.comparisons import repository
from app.comparisons.domain import (
    ComparisonData,
    ObservationSnapshot,
    TechnicalChangeData,
    compare_snapshots,
)
from app.comparisons.models import Comparison as ComparisonModel
from app.core.errors import InvalidInput, ResourceConflict, ResourceNotFound
from app.identity.domain import Principal
from app.identity.models import AuditEvent


class ComparisonService:
    def compare(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        old_observation_id: UUID,
        new_observation_id: UUID,
        rule_version: str,
    ) -> tuple[ComparisonData, bool]:
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code="COMPARISON_CREATE",
            allowed_roles={"ANALYST"},
        )
        if old_observation_id == new_observation_id:
            raise InvalidInput

        try:
            with session.begin():
                pair = repository.observation_pair_for_account(
                    session,
                    old_observation_id=old_observation_id,
                    new_observation_id=new_observation_id,
                    account_id=principal.account_id,
                )
                if pair is None:
                    raise ResourceNotFound
                old_observation, new_observation = pair
                if old_observation.process_id != new_observation.process_id:
                    raise InvalidInput

                existing = repository.comparison_by_key(
                    session,
                    old_observation_id=old_observation_id,
                    new_observation_id=new_observation_id,
                    rule_version=rule_version,
                )
                if existing is not None:
                    return self._comparison_data(session, existing), False

                old_snapshot = ObservationSnapshot(
                    id=old_observation.id,
                    process_id=old_observation.process_id,
                    quality=old_observation.quality,
                    sealed=old_observation.sealed_at is not None,
                    observed_at=old_observation.observed_at,
                    action_keys=tuple(
                        action.action_key
                        for action in acquisition_repository.actions_for_observation(
                            session, old_observation.id
                        )
                    ),
                )
                new_snapshot = ObservationSnapshot(
                    id=new_observation.id,
                    process_id=new_observation.process_id,
                    quality=new_observation.quality,
                    sealed=new_observation.sealed_at is not None,
                    observed_at=new_observation.observed_at,
                    action_keys=tuple(
                        action.action_key
                        for action in acquisition_repository.actions_for_observation(
                            session, new_observation.id
                        )
                    ),
                )
                draft = compare_snapshots(old_snapshot, new_snapshot)
                comparison = repository.add_comparison(
                    session,
                    comparison_id=uuid4(),
                    process_id=old_observation.process_id,
                    old_observation_id=old_observation.id,
                    new_observation_id=new_observation.id,
                    rule_version=rule_version,
                    result=draft.result,
                )
                for action_key in draft.added_action_keys:
                    repository.add_technical_change(
                        session,
                        change_id=uuid4(),
                        comparison=comparison,
                        action_key=action_key,
                    )
                self._audit(
                    session,
                    request_id=request_id,
                    principal=principal,
                    comparison_id=comparison.id,
                )
                return self._comparison_data(session, comparison), True
        except ResourceNotFound:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="COMPARISON_CREATE",
                reason="resource_not_in_scope",
            )
            raise
        except IntegrityError as exc:
            session.rollback()
            pair = repository.observation_pair_for_account(
                session,
                old_observation_id=old_observation_id,
                new_observation_id=new_observation_id,
                account_id=principal.account_id,
            )
            if pair is None:
                record_denial(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code="COMPARISON_CREATE",
                    reason="resource_not_in_scope",
                )
                raise ResourceNotFound from exc
            existing = repository.comparison_by_key(
                session,
                old_observation_id=old_observation_id,
                new_observation_id=new_observation_id,
                rule_version=rule_version,
            )
            if existing is None:
                raise ResourceConflict from exc
            return self._comparison_data(session, existing), False

    def get(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        comparison_id: UUID,
    ) -> ComparisonData:
        authorize_internal_account(
            session,
            principal=principal,
            request_id=request_id,
            event_code="COMPARISON_READ",
        )
        comparison = repository.comparison_for_assigned_account(
            session, comparison_id=comparison_id, account_id=principal.account_id
        )
        if comparison is None:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="COMPARISON_READ",
                reason="resource_not_in_scope",
            )
            raise ResourceNotFound
        return self._comparison_data(session, comparison)

    @staticmethod
    def _comparison_data(session: Session, comparison: ComparisonModel) -> ComparisonData:
        changes = tuple(
            TechnicalChangeData(
                id=change.id,
                action_key=change.action_key,
                change_kind=cast(Literal["ADDED"], change.change_kind),
                evidence=change.evidence,
            )
            for change in repository.changes_for_comparison(session, comparison.id)
        )
        return ComparisonData(
            id=comparison.id,
            process_id=comparison.process_id,
            old_observation_id=comparison.old_observation_id,
            new_observation_id=comparison.new_observation_id,
            rule_version=comparison.rule_version,
            result=cast(
                Literal["CHANGES_FOUND", "NO_CHANGES", "NOT_COMPARABLE"], comparison.result
            ),
            changes=changes,
        )

    @staticmethod
    def _audit(
        session: Session,
        *,
        request_id: UUID,
        principal: Principal,
        comparison_id: UUID,
    ) -> None:
        session.add(
            AuditEvent(
                id=uuid4(),
                request_id=request_id,
                event_code="COMPARISON_CREATE",
                result="SUCCESS",
                actor_account_id=principal.account_id,
                resource_kind="COMPARISON",
                resource_id=comparison_id,
            )
        )
