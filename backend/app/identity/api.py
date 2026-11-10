from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.dependencies import (
    DatabaseSession,
    IdentityServiceDependency,
    LoginRateLimiterDependency,
)
from app.identity.domain import (
    AuthenticatedSession,
    AuthenticationFailed,
)
from app.identity.schemas import (
    LoginRequest,
    Problem,
    SessionCreated,
)
from app.identity.schemas import (
    Principal as PrincipalResponse,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
opaque_bearer = HTTPBearer(
    auto_error=False,
    scheme_name="OpaqueBearer",
    bearerFormat="opaque",
    description="Opaque 256-bit bearer token; only its SHA-256 digest is stored.",
)


def _request_id(request: Request) -> UUID:
    return UUID(str(request.state.request_id))


def get_current_session(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(opaque_bearer)],
    session: DatabaseSession,
    identity: IdentityServiceDependency,
) -> AuthenticatedSession:
    access_token = (
        credentials.credentials
        if credentials is not None and credentials.scheme.lower() == "bearer"
        else None
    )
    return identity.authenticate(session, access_token, request_id=_request_id(request))


CurrentSession = Annotated[AuthenticatedSession, Depends(get_current_session)]


@router.post(
    "/sessions",
    status_code=201,
    response_model=SessionCreated,
    operation_id="login",
    openapi_extra={"security": []},
    responses={
        201: {
            "headers": {
                "Location": {
                    "schema": {"type": "string", "minLength": 1},
                    "description": "Resource created by the login operation.",
                }
            }
        },
        401: {"model": Problem, "description": "Authentication failed."},
        422: {"model": Problem, "description": "Request validation failed."},
        429: {"model": Problem, "description": "Too many login attempts."},
    },
)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    session: DatabaseSession,
    identity: IdentityServiceDependency,
    limiter: LoginRateLimiterDependency,
) -> SessionCreated:
    address = request.client.host if request.client is not None else "unknown"
    limiter.check(address)
    try:
        result = identity.login(
            session,
            username=payload.username,
            password=payload.password,
            request_id=_request_id(request),
        )
    except AuthenticationFailed:
        limiter.record_failure(address)
        raise
    limiter.clear(address)
    response.headers["Location"] = "/api/v1/auth/sessions/current"
    return SessionCreated(
        access_token=result.access_token,
        token_type="Bearer",
        expires_at=result.expires_at,
    )


@router.delete(
    "/sessions/current",
    status_code=204,
    operation_id="logout",
    responses={401: {"model": Problem, "description": "Authentication required."}},
)
def logout(
    request: Request,
    session: DatabaseSession,
    identity: IdentityServiceDependency,
    current: CurrentSession,
) -> Response:
    identity.logout(
        session,
        authenticated_session=current,
        request_id=_request_id(request),
    )
    return Response(status_code=204)


@router.get(
    "/me",
    response_model=PrincipalResponse,
    operation_id="getPrincipal",
    responses={401: {"model": Problem, "description": "Authentication required."}},
)
def get_principal(current: CurrentSession) -> PrincipalResponse:
    principal = current.principal
    return PrincipalResponse(
        account_id=principal.account_id,
        person_id=principal.person_id,
        account_kind=principal.account_kind,  # type: ignore[arg-type]
        client_id=principal.client_id,
        roles=list(principal.roles),  # type: ignore[arg-type]
    )
