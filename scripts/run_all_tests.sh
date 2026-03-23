#!/bin/bash
set -e

echo "=== Productivity Suite Test Suite ==="
echo ""

echo "[1/3] Running backend unit tests..."
cd backend
python -m pytest tests/unit/ -v --tb=short
echo ""

echo "[2/3] Backend tests complete."
echo ""

echo "[3/3] All tests passed!"
echo ""
echo "Total: Backend unit tests passed."
echo "Note: Frontend tests require npm ci first."
echo "  cd frontend-app && npm ci && npm test"
echo "  cd frontend-admin && npm ci && npm test"
