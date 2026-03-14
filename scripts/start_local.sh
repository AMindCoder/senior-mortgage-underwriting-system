#!/usr/bin/env bash
# Start the application locally (without Docker)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check for .env
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

# Export env vars
set -a
source .env
set +a

# Override hosts for local dev
export POSTGRES_HOST=localhost
export CHROMA_HOST=localhost

echo "Starting Streamlit application..."
streamlit run app.py \
    --server.port="${APP_PORT:-8501}" \
    --server.address="${APP_HOST:-0.0.0.0}" \
    --server.headless=true
