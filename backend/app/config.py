from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_env: Literal["local", "test"] = "local"
    database_url: SecretStr | None = None
    migration_database_url: SecretStr | None = None
    test_database_url: SecretStr | None = None
    test_migration_database_url: SecretStr | None = None

    def database(self, migration: bool = False) -> str:
        secret = self.migration_database_url if migration else self.database_url
        if secret is None:
            credential_name = "MIGRATION_DATABASE_URL" if migration else "DATABASE_URL"
            raise ValueError(f"{credential_name} is required")
        url = self._validated_url(secret)
        if url.database not in {"legaltech_demo", "legaltech_test"}:
            raise ValueError("Only isolated LegalTech PostgreSQL databases are permitted")
        return secret.get_secret_value()

    def test_database(self, migration: bool = False) -> str:
        secret = self.test_migration_database_url if migration else self.test_database_url
        if secret is None:
            credential_name = "TEST_MIGRATION_DATABASE_URL" if migration else "TEST_DATABASE_URL"
            raise ValueError(f"{credential_name} is required to run database tests")
        url = self._validated_url(secret)
        if url.database != "legaltech_test":
            raise ValueError("Tests are restricted to the legaltech_test database")
        return secret.get_secret_value()

    @staticmethod
    def _validated_url(secret: SecretStr) -> URL:
        url = make_url(secret.get_secret_value())
        if url.get_backend_name() != "postgresql" or url.host not in {
            "db",
            "localhost",
            "127.0.0.1",
        }:
            raise ValueError("Only local PostgreSQL connections are permitted")
        if url.database is None:
            raise ValueError("A database name is required")
        return url
