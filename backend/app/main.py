import logging
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from app.acquisitions.api import router as acquisitions_router
from app.clients.api import router as clients_router
from app.comparisons.api import router as comparisons_router
from app.config import Settings
from app.core.errors import ApplicationError
from app.db import create_database_engine, session_factory
from app.identity.api import router as identity_router
from app.identity.domain import AuthenticationFailed, RateLimited
from app.identity.rate_limit import LoginRateLimiter
from app.identity.service import IdentityService
from app.novelties.api import router as novelties_router
from app.trackings.api import router as trackings_router

logger = logging.getLogger("legaltech.api")


class LegalTechFastAPI(FastAPI):
    def openapi(self) -> dict[str, Any]:
        schema = super().openapi()
        problem_responses: dict[str, dict[str, tuple[str, ...]]] = {
            "/api/v1/auth/sessions": {"post": ("401", "422", "429")},
            "/api/v1/auth/sessions/current": {"delete": ("401",)},
            "/api/v1/auth/me": {"get": ("401",)},
            "/api/v1/internal/clients": {"post": ("401", "403", "409", "422")},
            "/api/v1/internal/clients/{client_id}": {"get": ("401", "403", "404", "409", "422")},
            "/api/v1/internal/processes": {"post": ("401", "403", "409", "422")},
            "/api/v1/internal/processes/{process_id}": {"get": ("401", "403", "404", "409", "422")},
            "/api/v1/internal/trackings": {"post": ("401", "403", "404", "409", "422")},
            "/api/v1/internal/trackings/{tracking_id}": {
                "get": ("401", "403", "404", "409", "422")
            },
            "/api/v1/internal/trackings/{tracking_id}/activate": {
                "post": ("401", "403", "404", "409", "422")
            },
            "/api/v1/internal/acquisition-runs": {"post": ("401", "403", "404", "409", "422")},
            "/api/v1/internal/acquisition-runs/{run_id}": {
                "get": ("401", "403", "404", "409", "422")
            },
            "/api/v1/internal/observations/{observation_id}": {
                "get": ("401", "403", "404", "409", "422")
            },
            "/api/v1/internal/trackings/{tracking_id}/adoptions": {
                "post": ("401", "403", "404", "409", "422")
            },
            "/api/v1/internal/comparisons": {"post": ("401", "403", "404", "409", "422")},
            "/api/v1/internal/comparisons/{comparison_id}": {
                "get": ("401", "403", "404", "409", "422")
            },
            "/api/v1/internal/trackings/{tracking_id}/evaluations": {
                "post": ("401", "403", "404", "409", "422")
            },
        }
        for path, operations in problem_responses.items():
            for method, status_codes in operations.items():
                responses = schema["paths"][path][method]["responses"]
                for status_code in status_codes:
                    content = responses[status_code].get("content", {})
                    json_schema = content.pop("application/json", None)
                    if json_schema is not None:
                        content["application/problem+json"] = json_schema

        schemas = schema.get("components", {}).get("schemas", {})
        for model in schemas.values():
            properties = model.get("properties", {})
            for property_schema in properties.values():
                const_value = property_schema.pop("const", None)
                if const_value is not None and "enum" not in property_schema:
                    property_schema["enum"] = [const_value]
                nullable_variants = property_schema.pop("anyOf", None)
                if nullable_variants is not None and any(
                    variant.get("type") == "null" for variant in nullable_variants
                ):
                    property_schema["oneOf"] = nullable_variants

        schema_constraints = {
            "Client": {"id": {"minLength": 1}, "status": {"minLength": 1}},
            "Process": {
                "id": {"minLength": 1},
                "label": {"minLength": 1, "maxLength": 180},
            },
            "ProcessCreate": {"label": {"minLength": 1, "maxLength": 180}},
            "TrackingCreate": {
                "client_id": {"minLength": 1},
                "process_id": {"minLength": 1},
            },
            "Tracking": {
                "id": {"minLength": 1},
                "client_id": {"minLength": 1},
                "process_id": {"minLength": 1},
                "status": {"minLength": 1},
                "baseline_observation_id": {"minLength": 1},
                "last_adopted_observation_id": {"minLength": 1},
            },
            "AcquisitionCreate": {
                "process_id": {"minLength": 1},
                "fixture_code": {"minLength": 1},
                "request_key": {"minLength": 8, "maxLength": 100},
            },
            "Acquisition": {
                "id": {"minLength": 1},
                "process_id": {"minLength": 1},
                "source_code": {"minLength": 1},
                "status": {"minLength": 1},
                "request_key": {"minLength": 1},
                "observation_id": {"minLength": 1},
                "error_code": {"minLength": 1},
                "coverage_note": {"minLength": 0},
            },
            "ObservedAction": {
                "action_key": {"minLength": 1},
                "description": {"minLength": 1},
                "occurred_on": {"minLength": 1},
            },
            "Observation": {
                "id": {"minLength": 1},
                "process_id": {"minLength": 1},
                "quality": {"minLength": 1},
                "observed_at": {"minLength": 1},
                "coverage_note": {"minLength": 0},
            },
            "AdoptObservationRequest": {"observation_id": {"minLength": 1}},
            "AdoptionResult": {"outcome": {"minLength": 1}},
            "ComparisonCreate": {
                "old_observation_id": {"minLength": 1},
                "new_observation_id": {"minLength": 1},
                "rule_version": {"minLength": 1, "maxLength": 32},
            },
            "TechnicalChange": {
                "id": {"minLength": 1},
                "action_key": {"minLength": 1},
                "change_kind": {"minLength": 1},
                "evidence": {"minLength": 1},
            },
            "Comparison": {
                "id": {"minLength": 1},
                "process_id": {"minLength": 1},
                "old_observation_id": {"minLength": 1},
                "new_observation_id": {"minLength": 1},
                "rule_version": {"minLength": 1},
                "result": {"minLength": 1},
            },
            "EvaluationCreate": {"comparison_id": {"minLength": 1}},
            "Evaluation": {
                "id": {"minLength": 1},
                "tracking_id": {"minLength": 1},
                "comparison_id": {"minLength": 1},
                "decision": {"minLength": 1},
                "reason": {"minLength": 1},
            },
        }
        for schema_name, constraints in schema_constraints.items():
            properties = schemas.get(schema_name, {}).get("properties", {})
            for property_name, property_constraints in constraints.items():
                property_schema = properties.get(property_name, {})
                variants = property_schema.get("oneOf")
                if variants is None:
                    property_schema.update(property_constraints)
                    continue
                for variant in variants:
                    if variant.get("type") == "string":
                        variant.update(property_constraints)

        evaluation_schema = schemas.get("Evaluation", {}).get("properties", {})
        novelty_items = evaluation_schema.get("novelty_ids", {}).get("items", {})
        if novelty_items.get("type") == "string":
            novelty_items["minLength"] = 1

        for path_item in schema.get("paths", {}).values():
            for operation in path_item.values():
                if not isinstance(operation, dict):
                    continue
                for parameter in operation.get("parameters", []):
                    parameter_schema = parameter.get("schema", {})
                    if parameter_schema.get("format") == "uuid":
                        parameter_schema.setdefault("minLength", 1)
        return schema


def _problem(
    request: Request,
    *,
    status: int,
    title: str,
    detail: str,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", uuid4())
    body = {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "request_id": str(request_id),
        "instance": request.url.path,
    }
    response_headers = {"X-Request-ID": str(request_id)}
    if headers:
        response_headers.update(headers)
    return JSONResponse(
        status_code=status,
        content=body,
        headers=response_headers,
        media_type="application/problem+json",
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    application_settings = settings or Settings()
    engine = create_database_engine(application_settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        engine.dispose()

    is_local = application_settings.app_env == "local"
    app = LegalTechFastAPI(
        title="LegalTech Vigilancia Judicial — Backend DEMO",
        version="0.1.0",
        docs_url="/docs" if is_local else None,
        redoc_url=None,
        openapi_url="/openapi.json" if is_local else None,
        lifespan=lifespan,
    )
    app.state.settings = application_settings
    app.state.engine = engine
    app.state.session_factory = session_factory(engine)
    app.state.identity_service = IdentityService()
    app.state.login_rate_limiter = LoginRateLimiter()
    app.include_router(identity_router)
    app.include_router(clients_router)
    app.include_router(trackings_router)
    app.include_router(acquisitions_router)
    app.include_router(comparisons_router)
    app.include_router(novelties_router)

    @app.middleware("http")
    async def attach_request_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = uuid4()
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = str(request_id)
        return response

    @app.get(
        "/healthz",
        tags=["Public"],
        operation_id="healthz",
        summary="Health of the API process",
        description="Reports HTTP process health only; it does not check database connectivity.",
        response_class=Response,
        response_model=None,
    )
    def healthz() -> Response:
        return Response(status_code=200)

    @app.exception_handler(AuthenticationFailed)
    async def authentication_failed(request: Request, _: AuthenticationFailed) -> JSONResponse:
        return _problem(
            request,
            status=401,
            title="Unauthorized",
            detail="Invalid credentials or bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(ApplicationError)
    async def application_error(request: Request, exc: ApplicationError) -> JSONResponse:
        return _problem(
            request,
            status=exc.status_code,
            title=exc.title,
            detail=exc.detail,
        )

    @app.exception_handler(RateLimited)
    async def rate_limited(request: Request, exc: RateLimited) -> JSONResponse:
        return _problem(
            request,
            status=429,
            title="Too Many Requests",
            detail="Login attempts are temporarily limited.",
            headers={"Retry-After": str(exc.retry_after)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_failed(request: Request, _: RequestValidationError) -> JSONResponse:
        return _problem(
            request,
            status=422,
            title="Unprocessable Content",
            detail="The request does not satisfy the API contract.",
        )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        titles = {404: "Not Found", 405: "Method Not Allowed"}
        details = {
            404: "The requested resource was not found.",
            405: "The request method is not allowed.",
        }
        return _problem(
            request,
            status=exc.status_code,
            title=titles.get(exc.status_code, "Request Failed"),
            detail=details.get(exc.status_code, "The request could not be completed."),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", uuid4())
        logger.error(
            "Unhandled request failure request_id=%s exception_type=%s",
            request_id,
            type(exc).__name__,
        )
        return _problem(
            request,
            status=500,
            title="Internal Server Error",
            detail="An unexpected error occurred.",
        )

    return app


app = create_app()
