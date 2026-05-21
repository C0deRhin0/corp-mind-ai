#!/bin/bash
# Ingest documents into corp-mind-ai
# Usage: ./scripts/ingest.sh --dir /path/to/docs
#        ./scripts/ingest.sh --file /path/to/document.pdf
#        ./scripts/ingest.sh --dir /path/to/docs --reset

set -euo pipefail

DIR=""
FILE=""
RESET=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dir)
            DIR="$2"
            shift 2
            ;;
        --file)
            FILE="$2"
            shift 2
            ;;
        --reset)
            RESET="--reset"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./scripts/ingest.sh --dir /path/to/docs"
            echo "       ./scripts/ingest.sh --file /path/to/document.pdf"
            echo "       ./scripts/ingest.sh --dir /path/to/docs --reset"
            exit 1
            ;;
    esac
done

# Check if at least one of dir or file is provided
if [ -z "$DIR" ] && [ -z "$FILE" ]; then
    echo "Error: Please specify --dir or --file"
    echo ""
    echo "Usage: ./scripts/ingest.sh --dir /path/to/docs"
    echo "       ./scripts/ingest.sh --file /path/to/document.pdf"
    exit 1
fi

# Get the script's directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Activate virtual environment
echo "📦 Activating ingestion environment..."
source ingestion/venv/bin/activate

# Build command
CMD=(python3 ingestion/main.py)
if [ -n "$DIR" ]; then
    CMD+=(--dir "$DIR")
fi
if [ -n "$FILE" ]; then
    CMD+=(--file "$FILE")
fi
if [ -n "$RESET" ]; then
    CMD+=(--reset)
fi

# Run ingestion
echo "🚀 Running ingestion..."
echo ""
"${CMD[@]}"

echo ""
echo "✅ Ingestion complete!"
