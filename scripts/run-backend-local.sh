#!/bin/zsh
# Local helper for the legacy Corp Mind development server.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/backend"
source "$ROOT_DIR/backend/venv/bin/activate"
exec python -m uvicorn main:app --host 127.0.0.1 --port 8002 >> /tmp/corp-mind-backend.log 2>&1
