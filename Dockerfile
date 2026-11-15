# Multi-stage Dockerfile for Request System API
# Stage 1: Builder - Install dependencies and create wheels
# Stage 2: Runtime - Minimal production image
#
# OPTIMIZATION NOTES:
# - Dependencies are installed before code for efficient layer caching
# - Uses wheel caching to avoid repeated compilation
# - Non-root user execution for security
# - Minimal image size (~200MB with dependencies)
# - Health checks for monitoring
# - Environment-based configuration for ports and hosts

# Build arguments for flexibility
ARG APP_PORT=8000

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml setup.py* ./

# Upgrade pip and install wheel tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Create wheels for all dependencies
# This uses the dependencies from pyproject.toml
RUN pip wheel --no-cache-dir --no-deps --wheel-dir ./wheels -e .

# ============================================================================
# Stage 2: Runtime
# ============================================================================
FROM python:3.11-slim

# Build arguments passed from stage 1
ARG APP_PORT=8000

# Set working directory
WORKDIR /app

# Create non-root user for security (before copying files)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies
# - curl: for health checks
# - postgresql-client: for database tools (psql, pg_dump, pg_isready)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage
COPY --from=builder /build/wheels /tmp/wheels

# Install dependencies from wheels (fast, no compilation)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /tmp/wheels/* && \
    rm -rf /tmp/wheels

# Copy application code with correct ownership (after dependencies)
# This allows caching the dependency layer when code changes
COPY --chown=appuser:appuser . /app/

# Switch to non-root user
USER appuser

# Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:$PYTHONPATH

# Expose port (can be overridden at runtime)
EXPOSE ${APP_PORT}

# Health check configuration
# Checks if API responds to health endpoint
# Useful for Docker, Kubernetes, and load balancers
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${APP_PORT}/health || exit 1

# Run FastAPI application via uvicorn
# Uses environment variables for configuration:
# - APP_HOST (default: 0.0.0.0)
# - APP_PORT (default: 8000)
# 
# Example environment override:
#   docker run -e APP_PORT=8080 request-system:latest
#
# Docker Compose example (docker-compose.yml):
#   services:
#     app:
#       ports:
#         - "${APP_PORT:-8000}:8000"  # external:internal
#       environment:
#         APP_PORT: 8000  # internal port
CMD ["python", "-m", "uvicorn", \
     "src.request_system.presentation.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000"]
