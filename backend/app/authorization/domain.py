from collections.abc import Collection

from app.core.errors import ForbiddenOperation
from app.identity.domain import Principal

INTERNAL_ROLES = frozenset({"ADMIN", "ANALYST", "LAWYER", "PREPARER", "COORDINATOR"})
ACTIVATION_ROLES = frozenset({"ADMIN", "ANALYST"})
EXTERNAL_READER_ROLES = frozenset({"EXTERNAL_READER"})


def require_internal_role(principal: Principal, allowed_roles: Collection[str]) -> None:
    if principal.account_kind != "INTERNAL" or not set(principal.roles).intersection(allowed_roles):
        raise ForbiddenOperation


def require_internal_account(principal: Principal) -> None:
    require_internal_role(principal, INTERNAL_ROLES)


def require_external_reader(principal: Principal) -> None:
    if principal.account_kind != "EXTERNAL" or not set(principal.roles).intersection(
        EXTERNAL_READER_ROLES
    ):
        raise ForbiddenOperation
