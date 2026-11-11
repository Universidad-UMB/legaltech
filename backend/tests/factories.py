from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.identity.models import Account, AccountRole, Client, Person
from app.identity.service import IdentityService

_identity_service = IdentityService()


def create_account(
    session: Session,
    *,
    username: str = "admin.demo",
    password: str,
    roles: tuple[str, ...] = ("ADMIN",),
    account_kind: str = "INTERNAL",
    client_id: UUID | None = None,
    status: str = "ACTIVE",
) -> Account:
    person_id = uuid4()
    person = Person(id=person_id, display_name="Synthetic test person")
    session.add(person)
    if account_kind == "EXTERNAL":
        if client_id is None:
            client_id = uuid4()
            session.add(
                Client(
                    id=client_id,
                    client_code=f"client-{person_id.hex[:12]}",
                    name="Synthetic test client",
                    status="ACTIVE",
                )
            )
    else:
        client_id = None
    session.flush()
    account = Account(
        id=uuid4(),
        person_id=person_id,
        username=username.lower(),
        password_hash=_identity_service.hash_password(password),
        account_kind=account_kind,
        client_id=client_id,
        status=status,
    )
    session.add(account)
    session.flush()
    for role in roles:
        session.add(AccountRole(account_id=account.id, account_kind=account_kind, role_code=role))
    session.commit()
    session.refresh(account)
    return account
