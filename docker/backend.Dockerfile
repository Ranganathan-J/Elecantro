# Production Backend Dockerfile using Base Image
# This builds on top of the base image with all dependencies
FROM elecantro/base:latest

# Copy application code
COPY . .

# Set ownership for appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Start command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
