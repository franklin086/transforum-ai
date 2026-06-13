$ExpectedRoot = "D:\transforum-ai"
$ErrorCount = 0

function Write-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Fix
    )

    if ($Passed) {
        Write-Host "[PASS] $Name" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $Name" -ForegroundColor Red
        Write-Host "       Fix: $Fix" -ForegroundColor Yellow
        $script:ErrorCount += 1
    }
}

Write-Host "TransForum AI Alpha 1.1.1 Environment Check"
Write-Host "Project root expected: $ExpectedRoot"
Write-Host ""

$CurrentPath = (Get-Location).Path
Write-Check "Current directory is D:\transforum-ai" ($CurrentPath -ieq $ExpectedRoot) "Run: cd /d D:\transforum-ai"

Write-Check "backend directory exists" (Test-Path "$ExpectedRoot\backend") "Restore the backend directory from the repository."
Write-Check "frontend directory exists" (Test-Path "$ExpectedRoot\frontend") "Restore the frontend directory from the repository."
Write-Check "Whisper tiny model exists" (Test-Path "$ExpectedRoot\models\whisper\tiny") "Install or copy the model to D:\transforum-ai\models\whisper\tiny."
Write-Check "data\audio directory exists" (Test-Path "$ExpectedRoot\data\audio") "Create it with: New-Item -ItemType Directory -Force D:\transforum-ai\data\audio"
Write-Check "data\chunks directory exists" (Test-Path "$ExpectedRoot\data\chunks") "Create it with: New-Item -ItemType Directory -Force D:\transforum-ai\data\chunks"
Write-Check "data\transcripts directory exists" (Test-Path "$ExpectedRoot\data\transcripts") "Create it with: New-Item -ItemType Directory -Force D:\transforum-ai\data\transcripts"

$Python = Get-Command python -ErrorAction SilentlyContinue
Write-Check "Python is available" ($null -ne $Python) "Install Python and ensure python is available in PATH."

$Node = Get-Command node -ErrorAction SilentlyContinue
Write-Check "Node is available" ($null -ne $Node) "Install Node.js and ensure node is available in PATH."

$Npm = Get-Command npm -ErrorAction SilentlyContinue
Write-Check "npm is available" ($null -ne $Npm) "Install Node.js/npm and ensure npm is available in PATH."

Write-Host ""
if ($ErrorCount -eq 0) {
    Write-Host "Environment check completed: PASS" -ForegroundColor Green
    exit 0
}

Write-Host "Environment check completed: FAIL ($ErrorCount issue(s))" -ForegroundColor Red
exit 1
