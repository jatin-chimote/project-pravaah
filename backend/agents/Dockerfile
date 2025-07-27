# Project Pravaah - Unified Agent Services Dockerfile
# Simplified version for reliable Cloud Build deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install core dependencies with compatible versions
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    pydantic==2.5.0 \
    httpx==0.25.2 \
    google-cloud-firestore==2.13.1 \
    google-cloud-pubsub==2.18.4 \
    firebase-admin==6.2.0 \
    vertexai==1.71.1 \
    google-cloud-aiplatform==1.71.1 \
    pyyaml==6.0.1

# Copy all Python files from agents directory
COPY *.py ./

# Copy ADK base files from local directory
COPY adk_base.py ./
COPY adk_config.yaml ./

# Copy service account key for authentication
COPY serviceAccountKey.json ./serviceAccountKey.json

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV PORT=8080
ENV GCP_PROJECT_ID=stable-sign-454210-i0

# Expose port
EXPOSE 8080

# Simple health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "-c", "print('Agent service ready')"]
