from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class AuthenticationFailed(Exception):
    """Credentials or bearer session are not currently valid."""


class RateLimited(Exception):
    def __init__(self, retry_after: int) -> None:
        super().__init__("Login rate limit exceeded")
        self.retry_after = retry_after


@dataclass(frozen=True)
class Principal:
    account_id: UUID
    person_id: UUID
    account_kind: str
    client_id: UUID | None
    roles: tuple[str, ...]


@dataclass(frozen=True)
class AuthenticatedSession:
    session_id: UUID
    principal: Principal


@dataclass(frozen=True)
class LoginResult:
    access_token: str
    expires_at: datetime
