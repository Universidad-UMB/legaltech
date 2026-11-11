from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from tests.traceability import TRACEABLE_REQUIREMENT_IDS


def _canonical_requirement_ids() -> set[str]:
    repository_root = Path(__file__).resolve().parents[2]
    acceptance_path = repository_root / "pruebas" / "PROTO-AT-001.json"
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    identifiers = {scenario["id"] for scenario in acceptance}

    for filename in ("API-NEG-001.csv", "DATA-TEST-001.csv"):
        manifest_path = repository_root / "pruebas" / filename
        with manifest_path.open(encoding="utf-8-sig", newline="") as stream:
            identifiers.update(row["id"] for row in csv.DictReader(stream))

    return identifiers


def test_canonical_requirements_are_visible_on_collected_behavior_tests(
    request: pytest.FixtureRequest,
) -> None:
    expected = _canonical_requirement_ids()
    collected_node_ids = "\n".join(item.nodeid for item in request.session.items)

    assert TRACEABLE_REQUIREMENT_IDS == expected
    missing = sorted(identifier for identifier in expected if identifier not in collected_node_ids)
    assert not missing, f"Canonical IDs missing from collected pytest items: {missing}"
