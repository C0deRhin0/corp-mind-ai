#!/bin/bash
# Ingest documents into corp-mind-ai
# Usage: ./ingest.sh --dir /path/to/docs
#        ./ingest.sh --file /path/to/document.pdf
#        ./ingest.sh --dir /path/to/docs --reset

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
            echo "Usage: ./ingest.sh --dir /path/to/docs"
            echo "       ./ingest.sh --file /path/to/document.pdf"
            echo "       ./ingest.sh --dir /path/to/docs --reset"
            exit 1
            ;;
    esac
done

# Check if at least one of dir or file is provided
if [ -z "$DIR" ] && [ -z "$FILE" ]; then
    echo "Error: Please specify --dir or --file"
    echo ""
    echo "Usage: ./ingest.sh --dir /path/to/docs"
    echo "       ./ingest.sh --file /path/to/document.pdf"
    exit 1
fi

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
echo "📦 Activating ingestion environment..."
source codebase/ingestion/venv/bin/activate

# Build command
CMD="python3 codebase/ingestion/main.py"
if [ -n "$DIR" ]; then
    CMD="$CMD --dir $DIR"
fi
if [ -n "$FILE" ]; then
    CMD="$CMD --file $FILE"
fi
if [ -n "$RESET" ]; then
    CMD="$CMD --reset"
fi

# Run ingestion
echo "🚀 Running ingestion..."
echo ""
eval $CMD

echo ""
echo "✅ Ingestion complete!"