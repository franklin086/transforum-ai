$ProjectRoot = "D:\transforum-ai"
$FrontendDir = Join-Path $ProjectRoot "frontend"

if (-not (Test-Path $FrontendDir)) {
    Write-Host "Frontend directory not found: $FrontendDir" -ForegroundColor Red
    exit 1
}

Write-Host "Frontend starting at http://localhost:3000 or fallback 3001" -ForegroundColor Green
Write-Host "Default command: npm run dev"
Write-Host "Fallback if needed: npm run build; npm run start -- -p 3001"
Set-Location $FrontendDir
npm run dev
