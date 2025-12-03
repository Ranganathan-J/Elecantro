# FROM python:3.10
# WORKDIR /code
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .



# Use a lightweight Python base image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable easier logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /code

# Install dependencies for psycopg2 & linux libs required by Django
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirement file first — better layer caching
COPY requirements.txt /code/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /code/

# Expose the port Django runs on
EXPOSE 8000

# Default command (overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
