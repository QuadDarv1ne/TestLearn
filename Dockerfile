# Multi-stage Dockerfile for TestLearn Application
# Production-optimized build

# ==================== Builder Stage ====================
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies to a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==================== Production Stage ====================
FROM python:3.9-slim AS production

WORKDIR /app

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appgroup . .

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health', timeout=5)" || exit 1

# Run with gunicorn for production (if installed) or uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ==================== Development Stage ====================
FROM production AS development

USER root

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-cov httpx

USER appuser

# Enable reload for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==================== Test Stage ====================
FROM production AS test

USER root

# Install test dependencies
RUN pip install --no-cache-dir pytest pytest-cov httpx

# Copy test files
COPY --chown=appuser:appgroup tests/ ./tests/

USER appuser

# Run tests
CMD ["pytest", "tests/", "-v", "--tb=short"]
