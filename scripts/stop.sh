#!/bin/bash
# Simple stop script

echo "🛑 Stopping corp-mind-ai..."

# Kill backend
pkill -f "uvicorn main:app" 2>/dev/null && echo "  ✓ Backend stopped" || true

# Kill frontend
pkill -f "vite" 2>/dev/null && echo "  ✓ Frontend stopped" || true

# Optionally stop Ollama (commented out - you might want it running)
# pkill -f "ollama serve" 2>/dev/null && echo "  ✓ Ollama stopped" || true

# Optionally stop Qdrant (commented out - you might want it running)
# docker stop qdrant 2>/dev/null && echo "  ✓ Qdrant stopped" || true

echo ""
echo "✅ Services stopped!"