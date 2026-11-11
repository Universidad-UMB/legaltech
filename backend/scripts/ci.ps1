$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot/..
try {
    if (-not (Test-Path ".env")) {
        uv run python scripts/dev_setup.py
        if ($LASTEXITCODE -ne 0) { throw "Local environment setup failed." }
    }

    uv lock --check
    if ($LASTEXITCODE -ne 0) { throw "uv.lock is not synchronized with pyproject.toml." }

    docker compose --project-name legaltech-backend up -d db
    if ($LASTEXITCODE -ne 0) { throw "The isolated LegalTech PostgreSQL service did not start." }

    $databaseReady = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        docker compose --project-name legaltech-backend exec -T db `
            pg_isready -U legaltech_admin -d legaltech_test *> $null
        if ($LASTEXITCODE -eq 0) {
            $databaseReady = $true
            break
        }
        Start-Sleep -Seconds 2
    }
    if (-not $databaseReady) { throw "legaltech_test did not become ready." }

    uv run python -m scripts.alembic_test upgrade head
    if ($LASTEXITCODE -ne 0) { throw "Alembic upgrade failed on legaltech_test." }
    uv run python -m scripts.alembic_test current
    if ($LASTEXITCODE -ne 0) { throw "Could not read the legaltech_test Alembic revision." }
    uv run python -m scripts.alembic_test check
    if ($LASTEXITCODE -ne 0) { throw "Alembic found schema changes without a migration." }

    & "$PSScriptRoot/quality.ps1"
    if ($LASTEXITCODE -ne 0) { throw "The quality suite failed." }

    git diff --check
    if ($LASTEXITCODE -ne 0) { throw "git diff --check found whitespace errors." }

    Write-Output "LegalTech CI checks passed. PostgreSQL service remains running; no Docker cleanup was run."
} finally {
    Pop-Location
}
