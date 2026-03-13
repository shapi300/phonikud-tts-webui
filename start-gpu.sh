#!/bin/bash
# Start Phonikud TTS API with GPU support

set -e

echo "Starting Phonikud TTS API (GPU mode)..."

# Check if models exist
if [ ! -f "api/models/phonikud-1.0.int8.onnx" ]; then
    echo "Models not found. Downloading..."
    python scripts/download_models.py
fi

# Set environment variables
export PHONIKUD_USE_GPU=true
export PHONIKUD_HOST=0.0.0.0
export PHONIKUD_PORT=8880

# Start the API
echo "Starting API on http://localhost:8880"
echo "API Docs: http://localhost:8880/docs"
echo "Web UI: http://localhost:8880/web"

uv run uvicorn api.src.main:app --host 0.0.0.0 --port 8880 --reload