# SentinelMesh - Intelligent Multi-Agent Software Testing & Bug Analysis Platform
# One-command launch script for Windows PowerShell

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "          Starting SentinelMesh Platform (Multi-Agent Swarm)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Determine Python executable
$PythonCmd = "python"
if (Test-Path ".\.venv\Scripts\python.exe") {
    $PythonCmd = ".\.venv\Scripts\python.exe"
}

# 2. Check and install dependencies
Write-Host "[1/3] Checking Python dependencies..." -ForegroundColor Yellow
& $PythonCmd -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install Python dependencies. Please verify your Python environment." -ForegroundColor Red
    exit 1
}

# 3. Initialize SQLite Database
Write-Host "[2/3] Initializing SentinelMesh SQLite database..." -ForegroundColor Yellow
& $PythonCmd -c "from backend.database import init_db; init_db(); print('Database ready.')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to initialize database." -ForegroundColor Red
    exit 1
}

# 4. Launch unified server
Write-Host "[3/3] Launching SentinelMesh server on http://localhost:8000 ..." -ForegroundColor Green
Write-Host "      Dashboard: http://localhost:8000" -ForegroundColor Green
Write-Host "      API Docs:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "      Press Ctrl+C to terminate." -ForegroundColor DarkGray
Write-Host ""

& $PythonCmd -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
