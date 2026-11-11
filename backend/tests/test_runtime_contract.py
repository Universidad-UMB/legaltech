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
    "suspendClient": ("post", "/api/v1/internal/clients/{client_id}/suspend"),
    "reactivateClient": ("post", "/api/v1/internal/clients/{client_id}/reactivate"),
    "createProcess": ("post", "/api/v1/internal/processes"),
    "getProcess": ("get", "/api/v1/internal/processes/{process_id}"),
    "createTracking": ("post", "/api/v1/internal/trackings"),
    "getTracking": ("get", "/api/v1/internal/trackings/{tracking_id}"),
    "activateTracking": ("post", "/api/v1/internal/trackings/{tracking_id}/activate"),
    "finishTracking": ("post", "/api/v1/internal/trackings/{tracking_id}/finish"),
    "createAcquisition": ("post", "/api/v1/internal/acquisition-runs"),
    "getAcquisition": ("get", "/api/v1/internal/acquisition-runs/{run_id}"),
    "getObservation": ("get", "/api/v1/internal/observations/{observation_id}"),
    "adoptObservation": ("post", "/api/v1/internal/trackings/{tracking_id}/adoptions"),
    "compareObservations": ("post", "/api/v1/internal/comparisons"),
    "getComparison": ("get", "/api/v1/internal/comparisons/{comparison_id}"),
    "evaluateComparison": ("post", "/api/v1/internal/trackings/{tracking_id}/evaluations"),
    "listNovelties": ("get", "/api/v1/internal/trackings/{tracking_id}/novelties"),
    "getNovelty": ("get", "/api/v1/internal/novelties/{novelty_id}"),
    "startOperativeReview": (
        "post",
        "/api/v1/internal/novelties/{novelty_id}/start-operative-review",
    ),
    "escalateNovelty": ("post", "/api/v1/internal/novelties/{novelty_id}/escalate"),
    "recordLegalReview": ("post", "/api/v1/internal/novelties/{novelty_id}/legal-review"),
    "createPublication": ("post", "/api/v1/internal/publications"),
    "getPublication": ("get", "/api/v1/internal/publications/{publication_id}"),
    "createPublicationVersion": (
        "post",
        "/api/v1/internal/publications/{publication_id}/versions",
    ),
    "getPublicationVersion": (
        "get",
        "/api/v1/internal/publication-versions/{version_id}",
    ),
    "submitPublicationVersion": (
        "post",
        "/api/v1/internal/publication-versions/{version_id}/submit",
    ),
    "decidePublicationVersion": (
        "post",
        "/api/v1/internal/publication-versions/{version_id}/decision",
    ),
    "publishPublicationVersion": (
        "post",
        "/api/v1/internal/publication-versions/{version_id}/publish",
    ),
    "portalTrackings": ("get", "/api/v1/portal/trackings"),
    "portalCurrentPublication": (
        "get",
        "/api/v1/portal/trackings/{tracking_id}/current-publication",
    ),
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
        (
            "/api/v1/internal/clients/{client_id}/suspend",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/clients/{client_id}/reactivate",
            "post",
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
        (
            "/api/v1/internal/trackings/{tracking_id}/finish",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/acquisition-runs",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/acquisition-runs/{run_id}",
            "get",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/observations/{observation_id}",
            "get",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/trackings/{tracking_id}/adoptions",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        ("/api/v1/internal/comparisons", "post", ("401", "403", "404", "409", "422")),
        (
            "/api/v1/internal/comparisons/{comparison_id}",
            "get",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/trackings/{tracking_id}/evaluations",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/trackings/{tracking_id}/novelties",
            "get",
            ("401", "403", "404", "422"),
        ),
        ("/api/v1/internal/novelties/{novelty_id}", "get", ("401", "403", "404", "409", "422")),
        (
            "/api/v1/internal/novelties/{novelty_id}/start-operative-review",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/novelties/{novelty_id}/escalate",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/novelties/{novelty_id}/legal-review",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        ("/api/v1/internal/publications", "post", ("401", "403", "404", "409", "422")),
        (
            "/api/v1/internal/publications/{publication_id}",
            "get",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/publications/{publication_id}/versions",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/publication-versions/{version_id}",
            "get",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/publication-versions/{version_id}/submit",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/publication-versions/{version_id}/decision",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        (
            "/api/v1/internal/publication-versions/{version_id}/publish",
            "post",
            ("401", "403", "404", "409", "422"),
        ),
        ("/api/v1/portal/trackings", "get", ("401", "403", "422")),
        (
            "/api/v1/portal/trackings/{tracking_id}/current-publication",
            "get",
            ("401", "403", "404", "422"),
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
        "ReasonRequest",
        "ProcessCreate",
        "Process",
        "TrackingCreate",
        "Tracking",
        "AcquisitionCreate",
        "Acquisition",
        "Observation",
        "ObservedAction",
        "AdoptObservationRequest",
        "AdoptionResult",
        "ComparisonCreate",
        "TechnicalChange",
        "Comparison",
        "EvaluationCreate",
        "Evaluation",
        "Novelty",
        "NoveltyList",
        "OperativeEscalation",
        "LegalReview",
        "PublicationCreate",
        "VersionCreate",
        "Publication",
        "PublicationVersion",
        "ApprovalRequest",
        "PortalTracking",
        "PortalTrackingList",
        "PortalPublication",
        "PortalPublicationResult",
    ):
        assert _without_titles(runtime["components"]["schemas"][schema_name]) == _without_titles(
            canonical["components"]["schemas"][schema_name]
        )

    request_schemas = {
        "createClient": "ClientCreate",
        "suspendClient": "ReasonRequest",
        "reactivateClient": "ReasonRequest",
        "createProcess": "ProcessCreate",
        "createTracking": "TrackingCreate",
        "createAcquisition": "AcquisitionCreate",
        "adoptObservation": "AdoptObservationRequest",
        "compareObservations": "ComparisonCreate",
        "evaluateComparison": "EvaluationCreate",
        "escalateNovelty": "OperativeEscalation",
        "recordLegalReview": "LegalReview",
        "createPublication": "PublicationCreate",
        "createPublicationVersion": "VersionCreate",
        "decidePublicationVersion": "ApprovalRequest",
        "finishTracking": "ReasonRequest",
    }
    response_schemas = {
        "createClient": ("201", "Client"),
        "getClient": ("200", "Client"),
        "suspendClient": ("200", "Client"),
        "reactivateClient": ("200", "Client"),
        "createProcess": ("201", "Process"),
        "getProcess": ("200", "Process"),
        "createTracking": ("201", "Tracking"),
        "getTracking": ("200", "Tracking"),
        "activateTracking": ("200", "Tracking"),
        "finishTracking": ("200", "Tracking"),
        "createAcquisition": ("201", "Acquisition"),
        "getAcquisition": ("200", "Acquisition"),
        "getObservation": ("200", "Observation"),
        "adoptObservation": ("200", "AdoptionResult"),
        "compareObservations": ("201", "Comparison"),
        "getComparison": ("200", "Comparison"),
        "evaluateComparison": ("201", "Evaluation"),
        "listNovelties": ("200", "NoveltyList"),
        "getNovelty": ("200", "Novelty"),
        "startOperativeReview": ("200", "Novelty"),
        "escalateNovelty": ("200", "Novelty"),
        "recordLegalReview": ("200", "Novelty"),
        "createPublication": ("201", "Publication"),
        "getPublication": ("200", "Publication"),
        "createPublicationVersion": ("201", "PublicationVersion"),
        "getPublicationVersion": ("200", "PublicationVersion"),
        "submitPublicationVersion": ("200", "PublicationVersion"),
        "decidePublicationVersion": ("200", "PublicationVersion"),
        "publishPublicationVersion": ("200", "PublicationVersion"),
        "portalTrackings": ("200", "PortalTrackingList"),
        "portalCurrentPublication": ("200", "PortalPublicationResult"),
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
    assert (
        "requestBody"
        not in runtime["paths"]["/api/v1/internal/novelties/{novelty_id}/start-operative-review"][
            "post"
        ]
    )
    list_parameters = {
        parameter["name"]: _without_titles(parameter["schema"])
        for parameter in runtime["paths"]["/api/v1/internal/trackings/{tracking_id}/novelties"][
            "get"
        ]["parameters"]
    }
    assert list_parameters["limit"] == {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "default": 25,
    }
    assert list_parameters["cursor"] == {"type": "string", "minLength": 1}
    portal_list_parameters = {
        parameter["name"]: _without_titles(parameter["schema"])
        for parameter in runtime["paths"]["/api/v1/portal/trackings"]["get"]["parameters"]
    }
    assert portal_list_parameters == {
        "limit": list_parameters["limit"],
        "cursor": list_parameters["cursor"],
    }
    for operation_id in set(EXPECTED_IMPLEMENTED_OPERATIONS) - {"healthz", "login"}:
        method, path = EXPECTED_IMPLEMENTED_OPERATIONS[operation_id]
        assert runtime["paths"][path][method]["security"] == [{"OpaqueBearer": []}]
    assert (
        runtime["paths"]["/api/v1/internal/clients"]["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"]["$ref"]
        == "#/components/schemas/ClientCreate"
    )
    acquisition_replay = runtime["paths"]["/api/v1/internal/acquisition-runs"]["post"]
    assert (
        acquisition_replay["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/Acquisition"
    )
    assert "Location" in acquisition_replay["responses"]["201"]["headers"]
    for operation_id in ("compareObservations", "evaluateComparison"):
        method, path = EXPECTED_IMPLEMENTED_OPERATIONS[operation_id]
        operation = runtime["paths"][path][method]
        assert (
            operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
            == operation["responses"]["201"]["content"]["application/json"]["schema"]["$ref"]
        )
        assert "Location" in operation["responses"]["201"]["headers"]


def test_swagger_and_openapi_routes_are_disabled_outside_local_environment(client: Any) -> None:
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404
