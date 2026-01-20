# Production Dockerfile for Skileez V2.0
# Moving to root to ensure Railway picks it up over V1

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install V2 dependencies
# Note the path change since we are now in the root
COPY v2_rebuild/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn uvicorn

# Copy all code (needed for v2_rebuild/backend imports to work)
COPY . .

# Set working directory to the backend for the app to run correctly
WORKDIR /app/v2_rebuild/backend

# Expose port
EXPOSE 8000

# Run with Gunicorn
# Use explicit port 8000 as Railway's $PORT seems unreliable in current config
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "app.main:app"]
