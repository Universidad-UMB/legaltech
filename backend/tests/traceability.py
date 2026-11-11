from __future__ import annotations

import pytest

TRACEABLE_REQUIREMENT_IDS: set[str] = set()


def trace_cases(*requirement_ids: str) -> pytest.MarkDecorator:
    """Expose canonical IDs in pytest node IDs for the behavior test below."""
    if not requirement_ids:
        raise ValueError("At least one canonical requirement ID is required.")

    TRACEABLE_REQUIREMENT_IDS.update(requirement_ids)
    node_id = "__".join(requirement_ids)
    return pytest.mark.parametrize(
        "_requirement_ids",
        [pytest.param(requirement_ids, id=node_id)],
    )
