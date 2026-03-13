"""Main FastAPI application for Phonikud TTS API."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from api.src.core.config import settings
from api.src.core.model_manager import model_manager
from api.src.routers import speech_router, voices_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    logger.info("Starting Phonikud TTS API...")
    logger.info(f"Models directory: {settings.models_dir}")
    logger.info(f"GPU enabled: {settings.use_gpu}")
    logger.info(f"Default engine: {settings.default_engine}")

    # Pre-load models
    try:
        logger.info("Loading Phonikud model...")
        model_manager.get_phonikud()
        logger.info("Phonikud model loaded successfully")
    except FileNotFoundError as e:
        logger.warning(f"Phonikud model not found: {e}")
    except Exception as e:
        logger.error(f"Error loading Phonikud model: {e}")

    try:
        logger.info("Loading Piper model...")
        model_manager.get_piper()
        logger.info("Piper model loaded successfully")
    except FileNotFoundError as e:
        logger.warning(f"Piper model not found: {e}")
    except Exception as e:
        logger.error(f"Error loading Piper model: {e}")

    # Log available voices
    voices = model_manager.get_available_voices()
    logger.info(f"Available voices: {list(voices.keys())}")

    yield

    # Shutdown
    logger.info("Shutting down Phonikud TTS API...")


# Create FastAPI app
app = FastAPI(
    title="Phonikud TTS WebUI",
    description="Hebrew Text-to-Speech API based on Phonikud",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(speech_router)
app.include_router(voices_router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic info and links."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Phonikud TTS WebUI</title>
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 700px;
                margin: 0 auto;
                padding: 60px 20px;
                background: #fafafa;
                color: #1a1a1a;
            }
            .container {
                background: white;
                border-radius: 8px;
                padding: 50px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            }
            h1 { 
                font-size: 28px; 
                font-weight: 600; 
                margin: 0 0 8px 0;
                letter-spacing: -0.5px;
            }
            .subtitle { 
                color: #666; 
                margin-bottom: 35px; 
                font-size: 15px;
            }
            .links { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 40px; }
            .link {
                display: inline-block;
                padding: 10px 18px;
                background: #1a1a1a;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: 500;
                transition: background 0.2s ease;
            }
            .link:hover { background: #333; }
            .link.secondary { 
                background: transparent; 
                color: #555; 
                border: 1px solid #ddd; 
            }
            .link.secondary:hover { 
                background: #f5f5f5; 
                border-color: #ccc;
                color: #333;
            }
            .section { 
                margin-top: 35px; 
                padding-top: 25px; 
                border-top: 1px solid #eee; 
            }
            .section h3 { 
                font-size: 13px;
                font-weight: 600; 
                color: #888;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin: 0 0 15px 0;
            }
            .section ul { list-style: none; padding: 0; margin: 0; }
            .section li { 
                padding: 10px 0; 
                border-bottom: 1px solid #f5f5f5;
                font-size: 14px;
            }
            .section li:last-child { border-bottom: none; }
            .section code { 
                background: #f5f5f5; 
                padding: 3px 8px; 
                border-radius: 3px; 
                font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
                font-size: 13px;
            }
            pre {
                background: #f8f8f8;
                padding: 18px;
                border-radius: 6px;
                overflow-x: auto;
                font-size: 13px;
                line-height: 1.5;
            }
            pre code {
                background: none;
                padding: 0;
            }
            .footer {
                text-align: center;
                padding: 30px 0 0;
                color: #999;
                font-size: 12px;
            }
            .footer a { color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Phonikud TTS WebUI</h1>
            <p class="subtitle">Hebrew Text-to-Speech API</p>

            <div class="links">
                <a href="/web" class="link">Web Interface</a>
                <a href="/docs" class="link secondary">API Docs</a>
                <a href="/redoc" class="link secondary">ReDoc</a>
                <a href="/v1/health" class="link secondary">Health</a>
            </div>

            <div class="section">
                <h3>Endpoints</h3>
                <ul>
                    <li><code>POST /v1/audio/speech</code> Generate speech from Hebrew text</li>
                    <li><code>GET /v1/voices</code> List available voices</li>
                    <li><code>POST /v1/phonemize</code> Convert text to phonemes</li>
                </ul>
            </div>

            <div class="section">
                <h3>Example</h3>
                <pre><code>from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8880/v1", 
    api_key="not-needed"
)

response = client.audio.speech.create(
    model="phonikud",
    voice="shaul",
    input="שלום עולם!"
)
response.stream_to_file("output.wav")</code></pre>
            </div>

            <div class="footer">
                Powered by <a href="https://github.com/thewh1teagle/phonikud" target="_blank">Phonikud</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/api/status")
async def status():
    """Get API status."""
    return {
        "status": "running",
        "version": "1.0.0",
        "default_engine": settings.default_engine,
        "gpu_enabled": settings.use_gpu,
    }


# Mount Gradio Web UI at /web
def mount_gradio_ui():
    """Mount Gradio UI at /web endpoint."""
    try:
        import sys
        import os
        import gradio as gr
        from gradio import mount_gradio_app
        
        # Add ui directory to path
        ui_path = os.path.join(os.path.dirname(__file__), "..", "..", "ui")
        if ui_path not in sys.path:
            sys.path.insert(0, ui_path)
        
        from lib.interface import create_interface as create_gradio_interface
        
        logger.info("Mounting Gradio Web UI at /web")
        gradio_demo = create_gradio_interface()
        mount_gradio_app(app, gradio_demo, path="/web")
        logger.info("Gradio Web UI mounted successfully")
    except Exception as e:
        logger.error(f"Failed to mount Gradio UI: {e}")


# Mount the Gradio UI
mount_gradio_ui()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.src.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )