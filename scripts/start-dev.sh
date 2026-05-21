#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "🟦 Starting Qdrant..."
docker compose -f docker-compose.dev.yml up -d qdrant

echo "⏳ Waiting for Qdrant to be ready..."
until curl -sf http://localhost:6333/readyz > /dev/null; do sleep 1; done
echo "✅ Qdrant ready → http://localhost:6333/dashboard"

echo "🐍 Starting backend..."
cd "$ROOT_DIR/backend"
python -m uvicorn main:app --reload --port 8001 &
BACKEND_PID=$!
cd "$ROOT_DIR"

echo "⚛️  Starting frontend..."
cd "$ROOT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
cd "$ROOT_DIR"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║       corp-mind-ai  PoC v2           ║"
echo "║                                      ║"
echo "║  App:     http://localhost:5174      ║"
echo "║  API:     http://localhost:8001/docs ║"
echo "║  Qdrant:  http://localhost:6333      ║"
echo "╚══════════════════════════════════════╝"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; cd '$ROOT_DIR' && docker compose -f docker-compose.dev.yml stop" EXIT
wait
