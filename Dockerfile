# ==============================================================================
# Multi-Stage Dockerfile for SentinelMesh Production Deployment
# Supports unified single-server deployment on Render, Railway, Fly.io, or VPS.
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build React 19 / Vite Frontend
# ------------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder
WORKDIR /build

COPY frontend/package*.json ./
RUN npm ci --prefer-offline --no-audit

COPY frontend/ ./
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 2: Production Python Runtime with Sandboxed Runner
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DATA_DIR=/app/data

WORKDIR /app

# Install security updates, system dependencies, and testing tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create dedicated non-root security user
RUN groupadd -g 10001 sentinel && \
    useradd -u 10001 -g sentinel -m -s /bin/bash sentinel

# Create data and project directories with correct permissions
RUN mkdir -p /app/data/projects && \
    chown -R sentinel:sentinel /app

# Copy application backend, agents, demo, and sandbox
COPY --chown=sentinel:sentinel backend/ /app/backend/
COPY --chown=sentinel:sentinel agents/ /app/agents/
COPY --chown=sentinel:sentinel demo/ /app/demo/
COPY --chown=sentinel:sentinel sandbox/ /app/sandbox/
COPY --chown=sentinel:sentinel pytest.ini /app/pytest.ini

# Copy pre-built frontend distribution from Stage 1
COPY --from=frontend-builder --chown=sentinel:sentinel /build/dist /app/frontend/dist

# Switch to non-root user
USER sentinel

# Declare persistent volume mount point for database and projects
VOLUME ["/app/data"]

EXPOSE 8000

# Container liveness health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:${PORT:-8000}/healthz || exit 1

# Start Uvicorn ASGI server with dynamic port support (Render/Railway/Docker)
CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --proxy-headers --forwarded-allow-ips='*'"]
