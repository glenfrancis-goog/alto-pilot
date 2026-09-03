# Production Dockerfile for Google Cloud Run
# Strictly conforms to SDD Section 1.3, 7.1, and Table 5.6
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project manifests and install dependencies
COPY pyproject.toml .env.example ./
RUN uv pip install --system -r pyproject.toml

# Copy application source code and knowledge assets
COPY src/ ./src/
COPY knowledge/ ./knowledge/
COPY main.py ./

EXPOSE 8080

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/healthz || exit 1

CMD ["python", "main.py", "--serve", "--host", "0.0.0.0", "--port", "8080"]
