# Project Pravaah - API Gateway Service Dockerfile
# Multi-stage build for production-ready container

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY main.py .

# Set environment variables
ENV PYTHONPATH=/home/appuser/.local/lib/python3.11/site-packages:$PYTHONPATH
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# GCP Cloud Run environment variables
ENV PORT=8080
ENV HOST=0.0.0.0

# API Gateway specific environment variables
ENV ORCHESTRATOR_SERVICE_URL=https://pravaah-orchestrator-service-stable-sign-454210-i0.a.run.app
ENV REQUEST_TIMEOUT=300
ENV MAX_RETRIES=3
ENV CORS_ORIGINS=https://pravaah-dashboard.web.app,http://localhost:4200
ENV GCP_PROJECT_ID=stable-sign-454210-i0

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
