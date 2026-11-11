from collections.abc import Collection

from app.core.errors import ForbiddenOperation
from app.identity.domain import Principal

INTERNAL_ROLES = frozenset({"ADMIN", "ANALYST", "LAWYER", "PREPARER", "COORDINATOR"})
ACTIVATION_ROLES = frozenset({"ADMIN", "ANALYST"})


def require_internal_role(principal: Principal, allowed_roles: Collection[str]) -> None:
    if principal.account_kind != "INTERNAL" or not set(principal.roles).intersection(allowed_roles):
        raise ForbiddenOperation


def require_internal_account(principal: Principal) -> None:
    require_internal_role(principal, INTERNAL_ROLES)
