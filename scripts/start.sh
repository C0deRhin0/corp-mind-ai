#!/bin/bash
# Simple start script - run this one command from the repository root or scripts/.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 Starting corp-mind-ai..."

# Start Ollama if not running
if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "  → Starting Ollama..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    # Wait for Ollama to be ready
    for i in {1..10}; do
        sleep 1
        if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
            break
        fi
    done
fi

# Start Qdrant if not running
if ! curl -sf http://localhost:6333/readyz >/dev/null 2>&1; then
    echo "  → Starting Qdrant..."
    docker run -d --name qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest 2>/dev/null || true
    sleep 3
fi

# Start Backend
echo "  → Starting Backend..."
cd "$ROOT_DIR/backend"
source venv/bin/activate
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 > /tmp/backend.log 2>&1 &
cd "$ROOT_DIR"

# Start Frontend
echo "  → Starting Frontend..."
cd "$ROOT_DIR/frontend"
nohup npm run dev > /tmp/frontend.log 2>&1 &
cd "$ROOT_DIR"

sleep 3

echo ""
echo "✅ All services started!"
echo ""
echo "  📱 App:       http://localhost:5174"
echo "  📚 API Docs:  http://localhost:8001/docs"
echo "  🗄️  Qdrant:   http://localhost:6333/dashboard"
echo ""
echo "Press Ctrl+C to stop, or run: ./scripts/stop.sh"
