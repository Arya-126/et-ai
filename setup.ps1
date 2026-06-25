# One-command setup for Windows (PowerShell).
#   ./setup.ps1            # full bootstrap
#   ./setup.ps1 -SkipCNN   # skip the currency CNN training (uses features-only)
param([switch]$SkipCNN)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Write-Host "==> Fraud Shield setup" -ForegroundColor Cyan

# 1. Backend venv + deps
Set-Location "$root/backend"
if (-not (Test-Path ".venv")) { python -m venv .venv }
$py = ".venv/Scripts/python.exe"
& $py -m pip install --quiet --upgrade pip
Write-Host "==> Installing torch (CPU) + backend deps..." -ForegroundColor Cyan
& $py -m pip install --quiet torch==2.12.1 torchvision==0.27.1 --index-url https://download.pytorch.org/whl/cpu
& $py -m pip install --quiet -r requirements.txt
if (-not (Test-Path ".env")) { Copy-Item "../.env.example" ".env" }

# 2. Data + currency model
Write-Host "==> Generating synthetic data..." -ForegroundColor Cyan
& $py -m data.generate
if (-not $SkipCNN) {
    Write-Host "==> Training currency CNN (~2 min)..." -ForegroundColor Cyan
    & $py -m cv.generate_notes
    & $py -m cv.train
}

# 3. Build the unified platform
Write-Host "==> Building the platform UI..." -ForegroundColor Cyan
Set-Location "$root/platform"
npm install
npm run build

Set-Location $root
Write-Host "`n==> Done. Start the platform:" -ForegroundColor Green
Write-Host "    cd backend; .venv/Scripts/activate; uvicorn app.main:app --port 8000"
Write-Host "    open http://localhost:8000"
