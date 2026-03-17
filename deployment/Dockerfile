# ── PatentGuard IP — Dockerfile ────────────────────────────────────────────────
# Multi-service container: runs FastAPI (port 8080) and Streamlit (port 8501)
# behind a single exposed port via a startup script.
# For DigitalOcean App Platform, only port 8080 is exposed externally.

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create log directory
RUN mkdir -p /app/logs

# Expose port (DigitalOcean App Platform target)
EXPOSE 8080

# Default: start FastAPI backend on port 8080
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8080"]
