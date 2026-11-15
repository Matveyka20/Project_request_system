#!/bin/bash
# Wait for PostgreSQL to be ready
# Usage: ./scripts/wait-for-db.sh [host] [port] [user] [max_attempts]

set -e

HOST="${1:-db}"
PORT="${2:-5432}"
USER="${3:-postgres}"
MAX_ATTEMPTS="${4:-30}"

echo "Waiting for PostgreSQL to be ready..."
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  User: $USER"
echo "  Max attempts: $MAX_ATTEMPTS"

attempt=1
until [ $attempt -gt $MAX_ATTEMPTS ]; do
    if pg_isready -h "$HOST" -p "$PORT" -U "$USER" > /dev/null 2>&1; then
        echo "✓ PostgreSQL is ready!"
        exit 0
    fi
    
    echo "  Attempt $attempt/$MAX_ATTEMPTS: PostgreSQL not ready yet..."
    attempt=$((attempt + 1))
    sleep 1
done

echo "✗ PostgreSQL failed to start within $MAX_ATTEMPTS seconds"
exit 1
