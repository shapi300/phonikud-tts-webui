# Phonikud TTS WebUI - CPU Image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY api ./api
COPY scripts ./scripts

# Install dependencies
RUN uv sync --no-dev

# Download models
RUN uv run python scripts/download_models.py --output api/models

# Set environment variables
ENV PHONIKUD_USE_GPU=false
ENV PHONIKUD_HOST=0.0.0.0
ENV PHONIKUD_PORT=8880

# Expose port
EXPOSE 8880

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8880/v1/health || exit 1

# Run the API
CMD ["uv", "run", "uvicorn", "api.src.main:app", "--host", "0.0.0.0", "--port", "8880"]