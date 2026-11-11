from dataclasses import dataclass
from uuid import UUID

from app.core.errors import InvalidInput


@dataclass(frozen=True, slots=True)
class ClientData:
    id: UUID
    client_code: str
    name: str
    status: str


def normalize_client_values(client_code: str, name: str) -> tuple[str, str]:
    normalized_code = client_code.strip()
    normalized_name = name.strip()
    if not normalized_code or not normalized_name:
        raise InvalidInput
    if len(normalized_code) > 32 or len(normalized_name) > 180:
        raise InvalidInput
    return normalized_code, normalized_name
