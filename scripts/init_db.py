#!/usr/bin/env python3
"""Initialize the PostgreSQL database schema."""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.db.models import init_db  # noqa: E402

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database tables created successfully.")
