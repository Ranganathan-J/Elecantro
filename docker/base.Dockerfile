# Base Docker Image for Elecantro Backend
# This image pre-installs all dependencies and can be reused
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy requirements first (for better layer caching)
COPY backend/requirements.txt .

# Install Python dependencies with pip cache
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV EVENTLET_MONKEY_PATCH=1

# Switch to non-root user
USER appuser

# Default command (will be overridden by specific containers)
CMD ["python", "--version"]
