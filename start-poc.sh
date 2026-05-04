#!/bin/bash
#
# corp-mind-ai POC Startup Script
# Simple execution - no Docker Compose needed
#

set -e

echo "╔══════════════════════════════════════════╗"
echo "║       corp-mind-ai  POC v2               ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ============================================
# Step 1: Check prerequisites
# ============================================
echo "📋 Checking prerequisites..."

# Check Python
if ! command_exists python3; then
    echo -e "${RED}✗ Python3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python3 found"

# Check Node.js
if ! command_exists node; then
    echo -e "${RED}✗ Node.js not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js found"

# Check if Qdrant is running
if curl -sf http://localhost:6333/readyz >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Qdrant is running at http://localhost:6333"
else
    echo -e "${YELLOW}⚠ Qdrant not running${NC}"
    echo "   Start Qdrant with: docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest"
    echo "   Or use: docker-compose -f docker-compose.dev.yml up -d"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Ollama is running
if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Ollama is running at http://localhost:11434"
else
    echo -e "${YELLOW}⚠ Ollama not running${NC}"
    echo "   Start Ollama with: ollama serve"
    echo "   And ensure llama3.2:3b is pulled: ollama pull llama3.2:3b"
    echo ""
fi

# ============================================
# Step 2: Setup Backend
# ============================================
echo ""
echo "🐍 Setting up backend..."

BACKEND_DIR="codebase/backend"

if [ ! -f "$BACKEND_DIR/requirements.txt" ]; then
    echo -e "${RED}✗ Backend requirements.txt not found${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv "$BACKEND_DIR/venv"
fi

# Activate virtual environment
source "$BACKEND_DIR/venv/bin/activate"

# Install dependencies
echo "   Installing Python dependencies..."
pip install -q -r "$BACKEND_DIR/requirements.txt" 2>/dev/null || pip install -r "$BACKEND_DIR/requirements.txt"

echo -e "${GREEN}✓${NC} Backend ready"

# ============================================
# Step 3: Setup Frontend
# ============================================
echo ""
echo "⚛️  Setting up frontend..."

FRONTEND_DIR="frontend"

if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    echo -e "${RED}✗ Frontend package.json not found${NC}"
    exit 1
fi

# Install node modules if needed
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "   Installing Node dependencies..."
    cd "$FRONTEND_DIR"
    npm install
    cd ..
fi

echo -e "${GREEN}✓${NC} Frontend ready"

# ============================================
# Step 4: Start services
# ============================================
echo ""
echo "🚀 Starting services..."
echo ""

# Start backend in background
echo "   Starting FastAPI backend on http://localhost:8000"
source "$BACKEND_DIR/venv/bin/activate"
cd "$BACKEND_DIR"
python -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ../..

# Wait a moment for backend to start
sleep 2

# Start frontend in background
echo "   Starting Vite dev server on http://localhost:5173"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Services Started                        ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  📱 App:       http://localhost:5173"
echo "  📚 API Docs:  http://localhost:8000/docs"
echo "  🗄️  Qdrant:   http://localhost:6333/dashboard"
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""

# ============================================
# Cleanup on exit
# ============================================
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "   Done!"
}

trap cleanup SIGINT SIGTERM

# Wait for any process to exit
wait