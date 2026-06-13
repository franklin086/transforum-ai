$ProjectRoot = "D:\transforum-ai"
$BackendDir = Join-Path $ProjectRoot "backend"

if (-not (Test-Path $BackendDir)) {
    Write-Host "Backend directory not found: $BackendDir" -ForegroundColor Red
    exit 1
}

Write-Host "Backend starting at http://localhost:8000" -ForegroundColor Green
Set-Location $BackendDir
python -m uvicorn main:app --reload
