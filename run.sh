#!/usr/bin/env bash
# SentinelMesh - Intelligent Multi-Agent Software Testing & Bug Analysis Platform
# One-command startup script for Linux/macOS

set -e

echo "======================================================================"
echo "          Starting SentinelMesh Platform (Multi-Agent Swarm)"
echo "======================================================================"
echo ""

# 1. Install dependencies
echo "[1/3] Checking Python dependencies..."
python3 -m pip install -r requirements.txt --quiet

# 2. Initialize database
echo "[2/3] Initializing SentinelMesh SQLite database..."
python3 -c "from backend.database import init_db; init_db(); print('Database ready.')"

# 3. Launch server
echo "[3/3] Launching SentinelMesh server on http://localhost:8000 ..."
echo "      Dashboard: http://localhost:8000"
echo "      API Docs:  http://localhost:8000/docs"
echo "      Press Ctrl+C to terminate."
echo ""

exec python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
