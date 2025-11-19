#!/bin/bash
set -e

echo "=========================================="
echo "Starting LLM-Ops API..."
echo "=========================================="

cd /app

echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Python path: $(which python)"

echo "Testing app import..."
python -c "import sys; sys.path.insert(0, '/app'); from app.app import app; print('✓ App imported successfully')" || {
    echo "ERROR: Failed to import app"
    exit 1
}

echo "Starting uvicorn server..."
exec python -m uvicorn app.app:app --host 0.0.0.0 --port 8001 --log-level info

