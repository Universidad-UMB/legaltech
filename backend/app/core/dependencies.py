from collections.abc import Generator
from typing import Annotated, cast

from fastapi import Depends, Request
from sqlalchemy.orm import Session, sessionmaker

from app.identity.rate_limit import LoginRateLimiter
from app.identity.service import IdentityService


def get_db(request: Request) -> Generator[Session, None, None]:
    factory = cast(sessionmaker[Session], request.app.state.session_factory)
    with factory() as session:
        yield session


def get_identity_service(request: Request) -> IdentityService:
    return cast(IdentityService, request.app.state.identity_service)


def get_login_rate_limiter(request: Request) -> LoginRateLimiter:
    return cast(LoginRateLimiter, request.app.state.login_rate_limiter)


DatabaseSession = Annotated[Session, Depends(get_db)]
IdentityServiceDependency = Annotated[IdentityService, Depends(get_identity_service)]
LoginRateLimiterDependency = Annotated[LoginRateLimiter, Depends(get_login_rate_limiter)]
