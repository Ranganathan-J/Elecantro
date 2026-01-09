# Multi-stage Dockerfile for reduced size and security

# ==================== BUILDER STAGE ====================
FROM python:3.11-slim-bookworm as builder

WORKDIR /app

# Install system dependencies for building packages (psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# ==================== FINAL STAGE ====================
FROM python:3.11-slim-bookworm

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install runtime dependencies (libpq for postgres)
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install packages
RUN pip install --no-cache /wheels/*

# Hugging Face / transformers cache dirs (writable for appuser)
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache/huggingface
ENV TORCH_HOME=/app/.cache/torch

# Copy application code
COPY . .

# Prepare writable cache dirs and set ownership to non-root user
RUN mkdir -p /app/.cache/huggingface /app/.cache/torch /app/logs \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Apply eventlet monkey patching for Celery
ENV EVENTLET_MONKEY_PATCH=1

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Default command (overridden by docker-compose or render.yaml)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "--error-logfile", "-"]
