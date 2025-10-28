# Smart Clash Reporter - Quick Start Script (PowerShell)
# This script launches both backend and frontend in separate terminal windows

param(
    [switch]$UseLive
)

$line = "=" * 58

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host $line -ForegroundColor Cyan
Write-Host "  Smart Clash Reporter - Quick Start" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host $line -ForegroundColor Cyan
Write-Host ""

# Determine mode
$mode = if ($UseLive) { "LIVE" } else { "MOCK" }
    $mode = "LIVE"
$UseLive = $true
$modeColor = if ($UseLive) { "Green" } else { "Cyan" }
Write-Host "Mode: $mode" -ForegroundColor $modeColor
Write-Host ""

# Check if Python is installed
$pythonOk = $false
try { $pythonVersion = python --version 2>$null ; $pythonOk = $true } catch { }
if ($pythonOk) {
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check if dependencies are installed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow

$backendReq = ".\backend\requirements.txt"
$frontendReq = ".\frontend\requirements.txt"

if (!(Test-Path $backendReq)) {
    Write-Host "Backend requirements.txt not found" -ForegroundColor Red
    exit 1
}

if (!(Test-Path $frontendReq)) {
    Write-Host "Frontend requirements.txt not found" -ForegroundColor Red
    exit 1
}

Write-Host "Dependencies files found" -ForegroundColor Green
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow

# Install backend dependencies
Write-Host "Installing backend..." -ForegroundColor Gray
python -m pip install -r backend/requirements.txt

# Install frontend dependencies
Write-Host "Installing frontend..." -ForegroundColor Gray
python -m pip install -r frontend/requirements.txt

Write-Host "Dependencies installed" -ForegroundColor Green
Write-Host ""

# Set environment variable for mock mode
$useMockValue = if ($UseLive) { "false" } else { "true" }
if ($UseLive) {
    $env:USE_MOCK = "false"
} else {
    $env:USE_MOCK = "true"
}

# Create directories if they don't exist
if (!(Test-Path ".\exports")) {
    New-Item -ItemType Directory -Path ".\exports" | Out-Null
    Write-Host "Created exports directory" -ForegroundColor Green
}

if (!(Test-Path ".\captures")) {
    New-Item -ItemType Directory -Path ".\captures" | Out-Null
    Write-Host "Created captures directory" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
Write-Host ""

# Start Backend in new window
Write-Host "→ Launching Backend (port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @"
    -NoExit -NoProfile -Command `"
    Write-Host 'Backend API Starting...' -ForegroundColor Cyan;
    Write-Host '';
    & Set-Location \`"$PWD\backend\`";
    `$env:USE_MOCK = '$useMockValue';
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    `"
"@

# Wait a bit for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Start Frontend in new window
Write-Host "Launching Frontend (port 8501)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @"
    -NoExit -NoProfile -Command `"
    Write-Host 'Frontend UI Starting...' -ForegroundColor Cyan;
    Write-Host '';
    & Set-Location "\"$PWD\frontend\"";
    `$env:API_BASE_URL = 'http://localhost:8000';
    python -m streamlit run streamlit_app.py --server.port 8501
    `"
"@

# Wait for frontend to start
Write-Host "   Waiting for frontend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 8

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host $line -ForegroundColor Green
Write-Host "  Services are starting!" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host $line -ForegroundColor Green
Write-Host ""
Write-Host "Frontend UI:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8501" -ForegroundColor Cyan
Write-Host "Backend API:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs:     " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host $line -ForegroundColor Green
Write-Host ""

# Open browser
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Start-Process "http://localhost:8501"

Write-Host ""
Write-Host 'Smart Clash Reporter is ready!' -ForegroundColor Green
Write-Host ""
Write-Host 'Press any key to exit this window (services will continue running)...' -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey([System.Management.Automation.Host.ReadKeyOptions]::NoEcho)
