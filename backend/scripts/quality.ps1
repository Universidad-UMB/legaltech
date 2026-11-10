$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot/..
try {
    uv sync --frozen
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    uv run ruff check app migrations scripts tests
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    uv run ruff format --check app migrations scripts tests
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    uv run mypy app
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    uv run pytest -q
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
    Pop-Location
}
