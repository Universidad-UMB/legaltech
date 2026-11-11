import hashlib
import json
from datetime import UTC, date, datetime
from functools import lru_cache
from pathlib import Path
from typing import cast

from app.acquisitions.domain import (
    AcquisitionFixture,
    AcquisitionStatus,
    FixtureAction,
    FixtureCode,
    ObservationQuality,
)

_FIXTURE_CODES: tuple[FixtureCode, ...] = ("OBS_001", "OBS_002", "FAILED", "INCOMPLETE")


class FixtureDataError(Exception):
    """Raised when the checked-in synthetic fixture bundle is invalid or unavailable."""


def _fixture_root() -> Path:
    candidates = (
        Path("/fixtures"),
        Path(__file__).resolve().parents[3] / "fixtures",
    )
    for candidate in candidates:
        if (candidate / "PROTO-DAT-001.json").is_file():
            return candidate
    raise FixtureDataError


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FixtureDataError from exc
    if not isinstance(value, dict):
        raise FixtureDataError
    return cast(dict[str, object], value)


def _text(value: object, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise FixtureDataError
    return value


def _process_radicados(root: Path) -> dict[str, str]:
    master = _read_json(root / "PROTO-DAT-001.json")
    records = master.get("processes")
    if not isinstance(records, list):
        raise FixtureDataError
    result: dict[str, str] = {}
    for record in records:
        if not isinstance(record, dict):
            raise FixtureDataError
        alias = _text(record.get("alias"))
        radicado = _text(record.get("radicado"))
        if len(radicado) != 23 or not radicado.isascii() or not radicado.isdigit():
            raise FixtureDataError
        result[alias] = radicado
    return result


def _parse_actions(value: object) -> tuple[FixtureAction, ...]:
    if not isinstance(value, list):
        raise FixtureDataError
    actions: list[FixtureAction] = []
    for item in value:
        if not isinstance(item, dict):
            raise FixtureDataError
        action_key = _text(item.get("action_key"))
        description = _text(item.get("description"))
        occurred_value = item.get("occurred_on")
        try:
            occurred_on = date.fromisoformat(_text(occurred_value))
        except ValueError as exc:
            raise FixtureDataError from exc
        actions.append(
            FixtureAction(
                action_key=action_key,
                description=description,
                occurred_on=occurred_on,
            )
        )
    if len({action.action_key for action in actions}) != len(actions):
        raise FixtureDataError
    return tuple(actions)


@lru_cache(maxsize=len(_FIXTURE_CODES))
def load_fixture(fixture_code: FixtureCode) -> AcquisitionFixture:
    root = _fixture_root()
    payload = _read_json(root / "adquisiciones" / f"{fixture_code}.json")
    if payload.get("fixture_code") != fixture_code:
        raise FixtureDataError

    process_alias = _text(payload.get("process_ref"))
    process_radicado = _process_radicados(root).get(process_alias)
    if process_radicado is None:
        raise FixtureDataError

    status_value = payload.get("run_status", "SUCCESS")
    if status_value not in {"SUCCESS", "INCOMPLETE", "FAILED"}:
        raise FixtureDataError
    status = cast(AcquisitionStatus, status_value)

    coverage_value = payload.get("coverage")
    coverage_note = _text(coverage_value, allow_empty=True) if coverage_value is not None else None
    reason = payload.get("reason")
    if reason is not None:
        coverage_note = _text(reason, allow_empty=True)

    error_value = payload.get("error_code")
    error_code = _text(error_value) if error_value is not None else None
    observation_value = payload.get("observation")
    observation_ref = payload.get("observation_ref")

    if status == "SUCCESS":
        observed_text = _text(payload.get("observed_at"))
        try:
            observed_at = datetime.fromisoformat(observed_text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise FixtureDataError from exc
        if observed_at.tzinfo is None:
            raise FixtureDataError
        quality_value = payload.get("quality")
        if quality_value not in {"COMPARABLE", "INCOMPLETE", "INDETERMINATE"}:
            raise FixtureDataError
        quality = cast(ObservationQuality, quality_value)
        actions = _parse_actions(payload.get("actions"))
        if observation_value is not None or not isinstance(observation_ref, str) or not actions:
            raise FixtureDataError
    else:
        observed_at = None
        quality = None
        actions = ()
        if observation_value is not None or observation_ref is not None:
            raise FixtureDataError
        if status == "FAILED" and error_code is None:
            raise FixtureDataError

    canonical_payload = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return AcquisitionFixture(
        fixture_code=fixture_code,
        process_alias=process_alias,
        process_radicado=process_radicado,
        status=status,
        error_code=error_code,
        coverage_note=coverage_note,
        observed_at=observed_at.astimezone(UTC) if observed_at is not None else None,
        quality=quality,
        actions=actions,
        payload_sha256=hashlib.sha256(canonical_payload).hexdigest(),
    )
