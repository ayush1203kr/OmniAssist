$ErrorActionPreference = "Stop"
Write-Host "OmniAssist setup" -ForegroundColor Cyan
Write-Host "Project: $PWD"
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    python -m pip install --user uv
}
uv python install 3.12
uv python pin 3.12
if (Test-Path .venv) { Remove-Item -Recurse -Force .venv }
uv sync
Write-Host "Environment ready." -ForegroundColor Green
Write-Host "Next: copy .env.example to .env, add GOOGLE_API_KEY, then run:"
Write-Host "  uv run uvicorn app.main:app --reload"
Write-Host "  uv run streamlit run streamlit_app.py"
