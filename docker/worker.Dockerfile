# Worker Dockerfile using Base Image
# This builds on top of the base image with all dependencies
FROM elecantro/base:latest

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD celery -A core inspect active || exit 1

# Start command
CMD ["celery", "-A", "core", "worker", "-l", "info", "-P", "eventlet"]
