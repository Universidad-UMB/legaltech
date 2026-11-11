import hashlib
import secrets
import unicodedata
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from uuid import UUID, uuid4

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error
from argon2.low_level import Type
from sqlalchemy.orm import Session

from app.identity import repository
from app.identity.domain import (
    AuthenticatedSession,
    AuthenticationFailed,
    LoginResult,
    Principal,
)
from app.identity.models import AuthSession

SESSION_TTL = timedelta(minutes=60)


def normalize_username(username: str) -> str:
    return unicodedata.normalize("NFKC", username).strip().lower()


@lru_cache(maxsize=1)
def _dummy_password_hash() -> str:
    hasher = PasswordHasher(type=Type.ID)
    return hasher.hash(secrets.token_urlsafe(32))


class IdentityService:
    def __init__(self) -> None:
        self._password_hasher = PasswordHasher(type=Type.ID)

    def hash_password(self, password: str) -> str:
        return self._password_hasher.hash(password)

    def login(
        self,
        session: Session,
        *,
        username: str,
        password: str,
        request_id: UUID,
    ) -> LoginResult:
        normalized_username = normalize_username(username)
        now = datetime.now(UTC)
        result: LoginResult | None = None

        with session.begin():
            account = repository.account_by_username(session, normalized_username)
            password_matches = self._verify_password(
                account.password_hash if account is not None else None, password
            )
            if account is None or account.status != "ACTIVE" or not password_matches:
                repository.record_audit_event(
                    session,
                    request_id=request_id,
                    event_code="AUTH_LOGIN",
                    result="DENIED",
                    sanitized_reason="invalid_credentials",
                )
            else:
                access_token = secrets.token_urlsafe(32)
                expires_at = now + SESSION_TTL
                session.add(
                    AuthSession(
                        id=uuid4(),
                        account_id=account.id,
                        token_digest=hashlib.sha256(access_token.encode("utf-8")).digest(),
                        issued_at=now,
                        expires_at=expires_at,
                    )
                )
                repository.record_audit_event(
                    session,
                    request_id=request_id,
                    event_code="AUTH_LOGIN",
                    result="SUCCESS",
                    actor_account_id=account.id,
                )
                result = LoginResult(access_token=access_token, expires_at=expires_at)

        if result is None:
            raise AuthenticationFailed
        return result

    def authenticate(
        self, session: Session, access_token: str | None, *, request_id: UUID
    ) -> AuthenticatedSession:
        now = datetime.now(UTC)
        authenticated_session: AuthenticatedSession | None = None

        with session.begin():
            match = None
            if access_token is not None:
                token_digest = hashlib.sha256(access_token.encode("utf-8")).digest()
                match = repository.active_session_by_digest(session, token_digest, now)
            if match is None:
                repository.record_audit_event(
                    session,
                    request_id=request_id,
                    event_code="AUTH_SESSION",
                    result="DENIED",
                    sanitized_reason="invalid_session",
                )
            else:
                auth_session, account = match
                principal = Principal(
                    account_id=account.id,
                    person_id=account.person_id,
                    account_kind=account.account_kind,
                    client_id=account.client_id,
                    roles=repository.roles_for_account(session, account.id),
                )
                authenticated_session = AuthenticatedSession(
                    session_id=auth_session.id,
                    principal=principal,
                )
        if authenticated_session is None:
            raise AuthenticationFailed
        return authenticated_session

    def logout(
        self,
        session: Session,
        *,
        authenticated_session: AuthenticatedSession,
        request_id: UUID,
    ) -> None:
        now = datetime.now(UTC)
        with session.begin():
            account_id = repository.revoke_active_session(
                session, authenticated_session.session_id, now
            )
            if account_id is None:
                raise AuthenticationFailed
            repository.record_audit_event(
                session,
                request_id=request_id,
                event_code="AUTH_LOGOUT",
                result="SUCCESS",
                actor_account_id=account_id,
            )

    def _verify_password(self, stored_hash: str | None, password: str) -> bool:
        encoded_hash = stored_hash if stored_hash is not None else _dummy_password_hash()
        try:
            verified: bool = self._password_hasher.verify(encoded_hash, password)
        except Argon2Error:
            verified = False
        return stored_hash is not None and verified
