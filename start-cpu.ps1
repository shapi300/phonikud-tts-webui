# Start Phonikud TTS API with CPU support (Windows PowerShell)

Write-Host "Starting Phonikud TTS API (CPU mode)..."

# Check if models exist
if (-not (Test-Path "api/models/phonikud-1.0.int8.onnx")) {
    Write-Host "Models not found. Downloading..."
    python scripts/download_models.py
}

# Set environment variables
$env:PHONIKUD_USE_GPU = "false"
$env:PHONIKUD_HOST = "0.0.0.0"
$env:PHONIKUD_PORT = "8880"

# Start the API
Write-Host "Starting API on http://localhost:8880"
Write-Host "API Docs: http://localhost:8880/docs"
Write-Host "Web UI: http://localhost:8880/web"

uv run uvicorn api.src.main:app --host 0.0.0.0 --port 8880 --reload