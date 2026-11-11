from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request, Response

from app.clients.schemas import Client, ClientCreate
from app.clients.service import ClientService
from app.core.dependencies import DatabaseSession
from app.identity.api import CurrentSession
from app.identity.schemas import Problem

router = APIRouter(prefix="/api/v1/internal/clients", tags=["Internal"])
_problem_responses: dict[int | str, dict[str, Any]] = {
    401: {"model": Problem, "description": "Authentication required."},
    403: {"model": Problem, "description": "Permission denied."},
    404: {"model": Problem, "description": "Resource not available in the authorized scope."},
    409: {"model": Problem, "description": "Conflict."},
    422: {"model": Problem, "description": "Request validation failed."},
}


@router.post(
    "",
    status_code=201,
    response_model=Client,
    operation_id="createClient",
    responses={
        201: {
            "description": "Client created.",
            "headers": {"Location": {"schema": {"type": "string", "minLength": 1}}},
        },
        **{key: value for key, value in _problem_responses.items() if key != 404},
    },
)
def create_client(
    payload: ClientCreate,
    request: Request,
    response: Response,
    session: DatabaseSession,
    current: CurrentSession,
) -> Client:
    created = ClientService().create(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        client_code=payload.client_code,
        name=payload.name,
    )
    response.headers["Location"] = f"/api/v1/internal/clients/{created.id}"
    return Client(
        id=created.id,
        client_code=created.client_code,
        name=created.name,
        status=created.status,  # type: ignore[arg-type]
    )


@router.get(
    "/{client_id}",
    response_model=Client,
    operation_id="getClient",
    responses={200: {"description": "Client returned."}, **_problem_responses},
)
def get_client(
    request: Request,
    client_id: UUID,
    session: DatabaseSession,
    current: CurrentSession,
) -> Client:
    found = ClientService().get(
        session,
        principal=current.principal,
        request_id=request.state.request_id,
        client_id=client_id,
    )
    return Client(
        id=found.id,
        client_code=found.client_code,
        name=found.name,
        status=found.status,  # type: ignore[arg-type]
    )
