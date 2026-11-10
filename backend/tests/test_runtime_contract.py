from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.main import create_app
from tests.conftest import TEST_SETTINGS

EXPECTED_INC00_OPERATIONS = {
    "healthz": ("get", "/healthz"),
    "login": ("post", "/api/v1/auth/sessions"),
    "logout": ("delete", "/api/v1/auth/sessions/current"),
    "getPrincipal": ("get", "/api/v1/auth/me"),
}


def _operations(document: dict[str, Any]) -> dict[str, tuple[str, str]]:
    operations: dict[str, tuple[str, str]] = {}
    for path, path_item in document["paths"].items():
        for method, operation in path_item.items():
            if isinstance(operation, dict) and "operationId" in operation:
                operations[operation["operationId"]] = (method, path)
    return operations


def test_inc00_runtime_routes_match_the_canonical_openapi_subset() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    contract_path = repository_root / "contratos" / "API-001.openapi.yaml"
    canonical: Any = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    runtime = create_app(TEST_SETTINGS).openapi()

    canonical_operations = _operations(canonical)
    runtime_operations = _operations(runtime)

    assert len(canonical_operations) == 35
    assert all(
        canonical_operations[name] == path for name, path in EXPECTED_INC00_OPERATIONS.items()
    )
    assert runtime_operations == EXPECTED_INC00_OPERATIONS
    assert runtime["paths"]["/api/v1/auth/sessions"]["post"]["security"] == []
    assert runtime["paths"]["/api/v1/auth/me"]["get"]["security"] == [{"OpaqueBearer": []}]
    assert (
        "Location"
        in runtime["paths"]["/api/v1/auth/sessions"]["post"]["responses"]["201"]["headers"]
    )
    for path, method, status_codes in (
        ("/api/v1/auth/sessions", "post", ("401", "422", "429")),
        ("/api/v1/auth/sessions/current", "delete", ("401",)),
        ("/api/v1/auth/me", "get", ("401",)),
    ):
        for status_code in status_codes:
            assert set(runtime["paths"][path][method]["responses"][status_code]["content"]) == {
                "application/problem+json"
            }
    assert "Principal" in runtime["components"]["schemas"]
    assert "PrincipalResponse" not in runtime["components"]["schemas"]
    assert "oneOf" in runtime["components"]["schemas"]["Principal"]["properties"]["client_id"]


def test_swagger_and_openapi_routes_are_disabled_outside_local_environment(client: Any) -> None:
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404
