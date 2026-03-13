"""Pydantic schemas for the audio API."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class SpeechRequest(BaseModel):
    """Request schema for speech generation (OpenAI-compatible)."""

    model: str = Field(default="phonikud", description="Model to use for TTS")
    input: str = Field(..., description="Hebrew text to convert to speech")
    voice: str = Field(default="shaul", description="Voice to use for synthesis")
    response_format: Optional[str] = Field(default="wav", description="Audio format (wav or mp3)")
    speed: Optional[float] = Field(default=1.0, ge=0.25, le=4.0, description="Speed of speech")

    # Extended options
    engine: Optional[Literal["piper", "zipvoice"]] = Field(default="piper", description="TTS engine to use")
    volume_factor: Optional[float] = Field(default=2.0, ge=0.1, le=10.0, description="Volume amplification")


class SpeechResponse(BaseModel):
    """Response schema for speech generation metadata."""

    vocalized_text: str = Field(..., description="Text with added diacritics")
    phonemes: str = Field(..., description="Phoneme representation")
    duration_seconds: float = Field(..., description="Duration of generated audio")
    sample_rate: int = Field(..., description="Audio sample rate")


class VoiceInfo(BaseModel):
    """Information about a voice."""

    voice_id: str = Field(..., description="Unique voice identifier")
    name: str = Field(..., description="Voice name")
    engine: str = Field(..., description="TTS engine (piper or zipvoice)")
    gender: str = Field(default="unknown", description="Voice gender")
    language: str = Field(default="he", description="Language code")


class VoicesResponse(BaseModel):
    """Response schema for listing voices."""

    voices: list[VoiceInfo] = Field(..., description="List of available voices")


class HealthResponse(BaseModel):
    """Response schema for health check."""

    status: str = Field(..., description="Service status")
    phonikud_loaded: bool = Field(..., description="Whether Phonikud model is loaded")
    piper_loaded: bool = Field(..., description="Whether Piper model is loaded")
    zipvoice_available: bool = Field(..., description="Whether ZipVoice is available")
    voices_count: int = Field(..., description="Number of available voices")


class PhonemizeRequest(BaseModel):
    """Request schema for phonemization."""

    text: str = Field(..., description="Hebrew text to phonemize")


class PhonemizeResponse(BaseModel):
    """Response schema for phonemization."""

    original_text: str = Field(..., description="Original input text")
    vocalized_text: str = Field(..., description="Text with added diacritics")
    phonemes: str = Field(..., description="Phoneme representation")