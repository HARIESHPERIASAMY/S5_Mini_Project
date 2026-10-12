@echo off
REM SentinelMesh - Intelligent Multi-Agent Software Testing & Bug Analysis Platform
REM One-command launch script for Windows

echo ======================================================================
echo           Starting SentinelMesh Platform (Multi-Agent Swarm)
echo ======================================================================
echo.

REM 1. Ensure Python dependencies are present
echo [1/3] Checking Python dependencies...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies. Please check python environment.
    pause
    exit /b 1
)

REM 2. Initialize database
echo [2/3] Initializing SentinelMesh SQLite database...
python -c "from backend.database import init_db; init_db(); print('Database ready.')"

REM 3. Launch the platform server
echo [3/3] Launching SentinelMesh server on http://localhost:8000 ...
echo       Opening Dashboard: http://localhost:8000
echo       API Docs:          http://localhost:8000/docs
echo       Press Ctrl+C to terminate.
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
