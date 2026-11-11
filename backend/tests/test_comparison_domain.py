from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.comparisons.domain import ObservationSnapshot, compare_snapshots
from app.novelties.domain import evaluation_decision


def test_comparator_uses_action_keys_and_returns_stable_order() -> None:
    process_id = uuid4()
    old = ObservationSnapshot(
        id=uuid4(),
        process_id=process_id,
        quality="COMPARABLE",
        sealed=True,
        observed_at=datetime(2026, 10, 15, tzinfo=UTC),
        action_keys=("ACT-02", "ACT-01"),
    )
    new = ObservationSnapshot(
        id=uuid4(),
        process_id=process_id,
        quality="COMPARABLE",
        sealed=True,
        observed_at=old.observed_at + timedelta(days=1),
        action_keys=("ACT-03", "ACT-01", "ACT-02"),
    )

    result = compare_snapshots(old, new)

    assert result.result == "CHANGES_FOUND"
    assert result.added_action_keys == ("ACT-03",)


def test_comparator_marks_ambiguous_or_incomplete_pairs_non_comparable() -> None:
    process_id = uuid4()
    observed_at = datetime(2026, 10, 15, tzinfo=UTC)
    old = ObservationSnapshot(
        id=uuid4(),
        process_id=process_id,
        quality="COMPARABLE",
        sealed=True,
        observed_at=observed_at,
        action_keys=("ACT-01",),
    )
    same_time = ObservationSnapshot(
        id=uuid4(),
        process_id=process_id,
        quality="COMPARABLE",
        sealed=True,
        observed_at=observed_at,
        action_keys=("ACT-02",),
    )
    incomplete = ObservationSnapshot(
        id=uuid4(),
        process_id=process_id,
        quality="INCOMPLETE",
        sealed=True,
        observed_at=observed_at + timedelta(days=1),
        action_keys=("ACT-02",),
    )

    assert compare_snapshots(old, same_time).result == "NOT_COMPARABLE"
    assert compare_snapshots(old, incomplete).result == "NOT_COMPARABLE"
    assert compare_snapshots(old, incomplete).added_action_keys == ()


def test_evaluation_skips_comparable_pairs_without_new_actions() -> None:
    assert evaluation_decision("NO_CHANGES", 0) == (
        "SKIPPED",
        "The comparable fixture snapshots contain no new action keys.",
    )
