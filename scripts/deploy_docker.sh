#!/usr/bin/env bash
# One-click Docker deployment
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check for .env
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "IMPORTANT: Edit .env and set your OPENAI_API_KEY before proceeding."
    exit 1
fi

echo "=== Building and starting services ==="
docker compose up --build -d

echo ""
echo "=== Waiting for services to be healthy ==="
sleep 5

echo ""
echo "=== Service status ==="
docker compose ps

echo ""
echo "=== Application is running ==="
echo "  Streamlit UI:  http://localhost:${APP_PORT:-8501}"
echo "  PostgreSQL:    localhost:${POSTGRES_PORT:-5432}"
echo "  ChromaDB:      http://localhost:${CHROMA_PORT:-8000}"
echo ""
echo "To view logs:   docker compose logs -f app"
echo "To stop:        docker compose down"
