"""Routers module for Phonikud TTS API."""

from api.src.routers.speech import router as speech_router
from api.src.routers.voices import router as voices_router

__all__ = ["speech_router", "voices_router"]