#!/bin/sh
set -eu

psql \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set ON_ERROR_STOP=1 \
  --set runtime_password="$POSTGRES_RUNTIME_PASSWORD" \
  --set migrator_password="$POSTGRES_MIGRATOR_PASSWORD" <<'SQL'
CREATE ROLE legaltech_runtime LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT
    PASSWORD :'runtime_password';
CREATE ROLE legaltech_migrator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT
    PASSWORD :'migrator_password';
GRANT CONNECT ON DATABASE legaltech_demo TO legaltech_runtime, legaltech_migrator;
GRANT CREATE ON DATABASE legaltech_demo TO legaltech_migrator;
GRANT USAGE ON SCHEMA public TO legaltech_runtime;
GRANT USAGE, CREATE ON SCHEMA public TO legaltech_migrator;
ALTER DEFAULT PRIVILEGES FOR ROLE legaltech_migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO legaltech_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE legaltech_migrator IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO legaltech_runtime;
CREATE DATABASE legaltech_test OWNER legaltech_migrator;
SQL

psql \
  --username "$POSTGRES_USER" \
  --dbname legaltech_test \
  --set ON_ERROR_STOP=1 <<'SQL'
GRANT CONNECT ON DATABASE legaltech_test TO legaltech_runtime, legaltech_migrator;
GRANT USAGE ON SCHEMA public TO legaltech_runtime;
GRANT USAGE, CREATE ON SCHEMA public TO legaltech_migrator;
ALTER DEFAULT PRIVILEGES FOR ROLE legaltech_migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO legaltech_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE legaltech_migrator IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO legaltech_runtime;
SQL
