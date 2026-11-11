from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.main import create_app
from tests.conftest import TEST_SETTINGS

EXPECTED_IMPLEMENTED_OPERATIONS = {
    "healthz": ("get", "/healthz"),
    "login": ("post", "/api/v1/auth/sessions"),
    "logout": ("delete", "/api/v1/auth/sessions/current"),
    "getPrincipal": ("get", "/api/v1/auth/me"),
    "createClient": ("post", "/api/v1/internal/clients"),
    "getClient": ("get", "/api/v1/internal/clients/{client_id}"),
    "createProcess": ("post", "/api/v1/internal/processes"),
    "getProcess": ("get", "/api/v1/internal/processes/{process_id}"),
    "createTracking": ("post", "/api/v1/internal/trackings"),
    "getTracking": ("get", "/api/v1/internal/trackings/{tracking_id}"),
    "activateTracking": ("post", "/api/v1/internal/trackings/{tracking_id}/activate"),
}


def _operations(document: dict[str, Any]) -> dict[str, tuple[str, str]]:
    operations: dict[str, tuple[str, str]] = {}
    for path, path_item in document["paths"].items():
        for method, operation in path_item.items():
            if isinstance(operation, dict) and "operationId" in operation:
                operations[operation["operationId"]] = (method, path)
    return operations


def _without_titles(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _without_titles(item) for key, item in value.items() if key != "title"}
    if isinstance(value, list):
        return [_without_titles(item) for item in value]
    return value


def test_inc00_runtime_routes_match_the_canonical_openapi_subset() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    contract_path = repository_root / "contratos" / "API-001.openapi.yaml"
    canonical: Any = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    runtime = create_app(TEST_SETTINGS).openapi()

    canonical_operations = _operations(canonical)
    runtime_operations = _operations(runtime)

    assert len(canonical_operations) == 35
    assert all(
        canonical_operations[name] == path for name, path in EXPECTED_IMPLEMENTED_OPERATIONS.items()
    )
    assert runtime_operations == EXPECTED_IMPLEMENTED_OPERATIONS
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
        ("/api/v1/internal/clients", "post", ("401", "403", "409", "422")),
        (
            "/api/v1/internal/clients/{client_id}",
            "get",
            ("401", "403", "404", "409", "422"),
        ),
        ("/api/v1/internal/processes", "post", ("401", "403", "409", "422")),
        (
            "/api/v1/internal/processes/{process_id}",
            "get",
            ("401", "403", "404", "409", "422"),
        ),
        ("/api/v1/internal/trackings", "post", ("401", "403", "404", "409", "422")),
        (
            "/api/v1/internal/trackings/{tracking_id}",
            "get",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/trackings/{tracking_id}/activate",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
    ):
        for status_code in status_codes:
            assert set(runtime["paths"][path][method]["responses"][status_code]["content"]) == {
                "application/problem+json"
            }
    assert "Principal" in runtime["components"]["schemas"]
    assert "PrincipalResponse" not in runtime["components"]["schemas"]
    assert "oneOf" in runtime["components"]["schemas"]["Principal"]["properties"]["client_id"]
    assert "ClientCreate" in runtime["components"]["schemas"]
    assert "ProcessCreate" in runtime["components"]["schemas"]
    assert "TrackingCreate" in runtime["components"]["schemas"]
    for schema_name in (
        "ClientCreate",
        "Client",
        "ProcessCreate",
        "Process",
        "TrackingCreate",
        "Tracking",
    ):
        assert _without_titles(runtime["components"]["schemas"][schema_name]) == _without_titles(
            canonical["components"]["schemas"][schema_name]
        )

    request_schemas = {
        "createClient": "ClientCreate",
        "createProcess": "ProcessCreate",
        "createTracking": "TrackingCreate",
    }
    response_schemas = {
        "createClient": ("201", "Client"),
        "getClient": ("200", "Client"),
        "createProcess": ("201", "Process"),
        "getProcess": ("200", "Process"),
        "createTracking": ("201", "Tracking"),
        "getTracking": ("200", "Tracking"),
        "activateTracking": ("200", "Tracking"),
    }
    for operation_id, schema_name in request_schemas.items():
        method, path = EXPECTED_IMPLEMENTED_OPERATIONS[operation_id]
        operation = runtime["paths"][path][method]
        assert (
            operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
            == f"#/components/schemas/{schema_name}"
        )
    for operation_id, (status_code, schema_name) in response_schemas.items():
        method, path = EXPECTED_IMPLEMENTED_OPERATIONS[operation_id]
        operation = runtime["paths"][path][method]
        assert (
            operation["responses"][status_code]["content"]["application/json"]["schema"]["$ref"]
            == f"#/components/schemas/{schema_name}"
        )
    for operation_id in set(EXPECTED_IMPLEMENTED_OPERATIONS) - {"healthz", "login"}:
        method, path = EXPECTED_IMPLEMENTED_OPERATIONS[operation_id]
        assert runtime["paths"][path][method]["security"] == [{"OpaqueBearer": []}]
    assert (
        runtime["paths"]["/api/v1/internal/clients"]["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"]["$ref"]
        == "#/components/schemas/ClientCreate"
    )


def test_swagger_and_openapi_routes_are_disabled_outside_local_environment(client: Any) -> None:
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404
