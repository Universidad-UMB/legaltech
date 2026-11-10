from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.identity.models import AuditEvent, AuthSession
from tests.conftest import TEST_PASSWORD
from tests.factories import create_account


def _login(client: TestClient, username: str = "admin.demo") -> dict[str, object]:
    response = client.post(
        "/api/v1/auth/sessions",
        json={"username": username, "password": TEST_PASSWORD},
    )
    assert response.status_code == 201
    assert response.headers["location"] == "/api/v1/auth/sessions/current"
    return response.json()


def _assert_problem(response: object, status: int) -> dict[str, object]:
    assert response.status_code == status  # type: ignore[attr-defined]
    assert response.headers["content-type"].startswith("application/problem+json")  # type: ignore[attr-defined]
    body = response.json()  # type: ignore[attr-defined]
    assert body["status"] == status
    assert body["request_id"] == response.headers["x-request-id"]  # type: ignore[attr-defined]
    assert body["instance"].startswith("/")
    return body


def test_login_persists_only_sha256_digest_and_returns_sixty_minute_token(
    client: TestClient, db_session: Session
) -> None:
    account = create_account(db_session, password=TEST_PASSWORD)

    response_body = _login(client, username="  ADMIN.DEMO  ")

    token = str(response_body["access_token"])
    assert len(token) >= 32
    assert response_body["token_type"] == "Bearer"
    stored_session = db_session.scalar(
        select(AuthSession).where(AuthSession.account_id == account.id)
    )
    assert stored_session is not None
    assert stored_session.token_digest == hashlib.sha256(token.encode("utf-8")).digest()
    assert stored_session.token_digest != token.encode("utf-8")
    assert stored_session.expires_at - stored_session.issued_at == timedelta(minutes=60)
    assert account.password_hash.startswith("$argon2id$")
    assert TEST_PASSWORD not in account.password_hash


def test_get_principal_returns_identity_roles_and_no_secret(
    client: TestClient, db_session: Session
) -> None:
    account = create_account(db_session, password=TEST_PASSWORD, roles=("ADMIN", "ANALYST"))
    body = _login(client)

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "account_id": str(account.id),
        "person_id": str(account.person_id),
        "account_kind": "INTERNAL",
        "client_id": None,
        "roles": ["ADMIN", "ANALYST"],
    }
    assert "password_hash" not in response.json()


def test_unknown_and_wrong_password_have_same_generic_401_and_sanitized_audit(
    client: TestClient, db_session: Session
) -> None:
    create_account(db_session, password=TEST_PASSWORD)
    wrong = client.post(
        "/api/v1/auth/sessions",
        json={"username": "admin.demo", "password": "wrong-password-value"},
    )
    missing = client.post(
        "/api/v1/auth/sessions",
        json={"username": "not-a-real-account", "password": "wrong-password-value"},
    )

    wrong_body = _assert_problem(wrong, 401)
    missing_body = _assert_problem(missing, 401)
    assert wrong_body["detail"] == missing_body["detail"]
    assert "admin.demo" not in wrong.text
    assert "not-a-real-account" not in missing.text
    assert "wrong-password-value" not in wrong.text
    events = list(db_session.scalars(select(AuditEvent).order_by(AuditEvent.created_at)))
    assert len(events) == 2
    assert all(event.event_code == "AUTH_LOGIN" and event.result == "DENIED" for event in events)
    assert all(event.actor_account_id is None for event in events)
    assert all(event.sanitized_reason == "invalid_credentials" for event in events)


def test_expired_and_revoked_sessions_return_401(client: TestClient, db_session: Session) -> None:
    account = create_account(db_session, password=TEST_PASSWORD)
    now = datetime.now(UTC)
    expired_token = secrets.token_urlsafe(32)
    revoked_token = secrets.token_urlsafe(32)
    db_session.add_all(
        [
            AuthSession(
                id=uuid4(),
                account_id=account.id,
                token_digest=hashlib.sha256(expired_token.encode()).digest(),
                issued_at=now - timedelta(hours=2),
                expires_at=now - timedelta(hours=1),
            ),
            AuthSession(
                id=uuid4(),
                account_id=account.id,
                token_digest=hashlib.sha256(revoked_token.encode()).digest(),
                issued_at=now - timedelta(minutes=2),
                expires_at=now + timedelta(minutes=58),
                revoked_at=now - timedelta(minutes=1),
            ),
        ]
    )
    db_session.commit()

    for token in (expired_token, revoked_token):
        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        _assert_problem(response, 401)
    audit_events = list(
        db_session.scalars(select(AuditEvent).where(AuditEvent.event_code == "AUTH_SESSION"))
    )
    assert len(audit_events) == 2
    assert all(event.result == "DENIED" for event in audit_events)
    assert all(event.sanitized_reason == "invalid_session" for event in audit_events)
    assert all(event.actor_account_id is None for event in audit_events)


def test_logout_returns_204_revokes_session_and_repeat_returns_401(
    client: TestClient, db_session: Session
) -> None:
    account = create_account(db_session, password=TEST_PASSWORD)
    body = _login(client)
    token = str(body["access_token"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/api/v1/auth/sessions/current", headers=headers)

    assert response.status_code == 204
    assert response.content == b""
    stored_session = db_session.scalar(
        select(AuthSession).where(AuthSession.account_id == account.id)
    )
    assert stored_session is not None and stored_session.revoked_at is not None
    _assert_problem(client.delete("/api/v1/auth/sessions/current", headers=headers), 401)


def test_disabled_account_cannot_login_or_reuse_an_existing_session(
    client: TestClient, db_session: Session
) -> None:
    account = create_account(db_session, password=TEST_PASSWORD)
    token = str(_login(client)["access_token"])
    account.status = "DISABLED"
    db_session.commit()

    _assert_problem(
        client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}), 401
    )
    _assert_problem(
        client.post(
            "/api/v1/auth/sessions",
            json={"username": "admin.demo", "password": TEST_PASSWORD},
        ),
        401,
    )


def test_validation_errors_are_problem_json_without_request_values(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/sessions",
        json={"username": "", "password": "never-echo-this-value", "extra": "bad"},
    )

    body = _assert_problem(response, 422)
    assert body["title"] == "Unprocessable Content"
    assert "never-echo-this-value" not in response.text
    assert "bad" not in response.text


def test_missing_invalid_bearer_and_login_rate_limit_are_problem_responses(
    client: TestClient, db_session: Session
) -> None:
    _assert_problem(client.get("/api/v1/auth/me"), 401)
    _assert_problem(client.get("/api/v1/auth/me", headers={"Authorization": "Basic abc"}), 401)

    client.app.state.login_rate_limiter.limit = 1
    invalid = client.post(
        "/api/v1/auth/sessions",
        json={"username": "unknown", "password": TEST_PASSWORD},
    )
    _assert_problem(invalid, 401)
    limited = client.post(
        "/api/v1/auth/sessions",
        json={"username": "unknown", "password": TEST_PASSWORD},
    )
    body = _assert_problem(limited, 429)
    assert int(limited.headers["retry-after"]) > 0
    assert body["detail"] == "Login attempts are temporarily limited."
    denied_events = list(db_session.scalars(select(AuditEvent)))
    assert sum(event.event_code == "AUTH_SESSION" for event in denied_events) == 2
    assert sum(event.event_code == "AUTH_LOGIN" for event in denied_events) == 1
