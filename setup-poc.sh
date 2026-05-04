#!/bin/bash
#
# corp-mind-ai POC Setup Script
# Run this once to install all dependencies
#

set -e

echo "╔══════════════════════════════════════════╗"
echo "║  corp-mind-ai POC Setup                  ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

# ============================================
# 1. Setup Ingestion
# ============================================
echo "📦 Setting up ingestion pipeline..."
cd codebase/ingestion
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
cd ../..
echo -e "${GREEN}✓${NC} Ingestion ready"

# ============================================
# 2. Setup Backend
# ============================================
echo "📦 Setting up backend..."
cd codebase/backend
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
cd ../..
echo -e "${GREEN}✓${NC} Backend ready"

# ============================================
# 3. Setup Frontend
# ============================================
echo "📦 Setting up frontend..."
cd frontend
npm install
cd ..
echo -e "${GREEN}✓${NC} Frontend ready"

# ============================================
# 4. Check external services
# ============================================
echo ""
echo "🔍 Checking external services..."

# Check Qdrant
if curl -sf http://localhost:6333/readyz >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Qdrant is running"
else
    echo "⚠️  Qdrant is not running"
    echo "   Start with: docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest"
fi

# Check Ollama
if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Ollama is running"
else
    echo "⚠️  Ollama is not running"
    echo "   Start with: ollama serve"
    echo "   And pull model: ollama pull llama3.2:3b"
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Setup Complete!                         ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Start Qdrant:  docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest"
echo "  2. Start Ollama:  ollama serve  (and ollama pull llama3.2:3b)"
echo "  3. Ingest docs:  source codebase/ingestion/venv/bin/activate && python codebase/ingestion/main.py --dir /path/to/docs"
echo "  4. Run app:      ./start-poc.sh"
echo ""