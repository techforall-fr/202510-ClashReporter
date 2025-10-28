# Force LIVE MODE - Manual Backend and Frontend Start

$line = "=" * 58

Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host $line -ForegroundColor Green
Write-Host "  Smart Clash Reporter - LIVE MODE" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host $line -ForegroundColor Green
Write-Host ""

# Force environment variables
$env:USE_MOCK = "false"

Write-Host "Starting Backend in LIVE mode..." -ForegroundColor Cyan
Write-Host ""

# Navigate to backend
Set-Location -Path "backend"

# Start backend
Write-Host "Backend starting at http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs at http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "To start frontend, open a new terminal and run:" -ForegroundColor Yellow
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  streamlit run streamlit_app.py" -ForegroundColor White
Write-Host ""

# Run backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
