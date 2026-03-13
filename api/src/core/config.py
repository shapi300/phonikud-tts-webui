"""Configuration settings for Phonikud TTS API."""

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings."""

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8880
    workers: int = 1

    # Model settings
    models_dir: Path = Path("api/models")
    phonikud_model: str = "phonikud-1.0.int8.onnx"

    # Piper settings
    piper_model: str = "shaul.onnx"
    piper_config: str = "model.config.json"

    # ZipVoice settings
    zipvoice_dir: str = "zipvoice"
    zipvoice_text_encoder: str = "text_encoder.onnx"
    zipvoice_fm_decoder: str = "fm_decoder.onnx"
    zipvoice_text_encoder_int8: str = "text_encoder_int8.onnx"
    zipvoice_fm_decoder_int8: str = "fm_decoder_int8.onnx"
    zipvoice_model_json: str = "model.json"
    zipvoice_tokens: str = "tokens.txt"

    # Default voice prompts
    default_prompts_dir: str = "prompts"

    # TTS settings
    default_engine: Literal["piper", "zipvoice"] = "piper"
    default_speed: float = 1.2
    default_volume_factor: float = 2.0

    # Piper specific settings
    piper_length_scale: float = 1.20
    piper_noise_scale: float = 0.640
    piper_noise_w: float = 1.0

    # GPU settings
    use_gpu: bool = False
    onnx_providers: list[str] = ["CPUExecutionProvider"]

    # Audio settings
    output_format: Literal["wav", "mp3"] = "wav"

    class Config:
        env_prefix = "PHONIKUD_"


def get_settings() -> Settings:
    """Get settings with environment variable overrides."""
    settings = Settings()

    # Override with environment variables
    if os.getenv("PHONIKUD_HOST"):
        settings.host = os.getenv("PHONIKUD_HOST")  # type: ignore
    if os.getenv("PHONIKUD_PORT"):
        settings.port = int(os.getenv("PHONIKUD_PORT", "8880"))
    if os.getenv("PHONIKUD_USE_GPU", "").lower() == "true":
        settings.use_gpu = True
        settings.onnx_providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    if os.getenv("PHONIKUD_MODELS_DIR"):
        settings.models_dir = Path(os.getenv("PHONIKUD_MODELS_DIR", "api/models"))
    if os.getenv("PHONIKUD_DEFAULT_ENGINE"):
        settings.default_engine = os.getenv("PHONIKUD_DEFAULT_ENGINE", "piper")  # type: ignore

    return settings


# Global settings instance
settings = get_settings()