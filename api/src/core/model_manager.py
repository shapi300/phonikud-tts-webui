"""Model manager for loading and managing TTS models."""

import logging
from pathlib import Path
from typing import Optional

from phonikud_onnx import Phonikud
from piper_onnx import Piper

from api.src.core.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages TTS model loading and caching."""

    _instance: Optional["ModelManager"] = None

    def __new__(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._phonikud_model: Optional[Phonikud] = None
        self._piper_model: Optional[Piper] = None
        self._zipvoice_model = None
        self._available_voices: dict[str, dict] = {}
        self._load_voices()

    def _load_voices(self) -> None:
        """Load available voice configurations."""
        # Piper voices
        piper_dir = settings.models_dir / "piper"
        if piper_dir.exists():
            for onnx_file in piper_dir.glob("*.onnx"):
                voice_name = onnx_file.stem
                self._available_voices[f"piper_{voice_name}"] = {
                    "engine": "piper",
                    "name": voice_name,
                    "model_path": str(onnx_file),
                    "gender": self._guess_gender(voice_name),
                }

        # ZipVoice prompts
        zipvoice_prompts_dir = settings.models_dir / settings.zipvoice_dir / settings.default_prompts_dir
        if zipvoice_prompts_dir.exists():
            for wav_file in zipvoice_prompts_dir.glob("*.wav"):
                voice_name = wav_file.stem
                self._available_voices[f"zipvoice_{voice_name}"] = {
                    "engine": "zipvoice",
                    "name": voice_name,
                    "prompt_path": str(wav_file),
                    "gender": self._guess_gender(voice_name),
                }

        # Add default voice if no voices found
        if not self._available_voices:
            self._available_voices["piper_default"] = {
                "engine": "piper",
                "name": "default",
                "model_path": str(settings.models_dir / "piper" / settings.piper_model),
                "gender": "male",
            }

    def _guess_gender(self, name: str) -> str:
        """Guess voice gender from name."""
        name_lower = name.lower()
        female_indicators = ["female", "woman", "girl", "f"]
        male_indicators = ["male", "man", "boy", "m", "shaul"]

        for indicator in female_indicators:
            if indicator in name_lower:
                return "female"
        for indicator in male_indicators:
            if indicator in name_lower:
                return "male"
        return "unknown"

    def get_phonikud(self) -> Phonikud:
        """Get or load the Phonikud model."""
        if self._phonikud_model is None:
            model_path = settings.models_dir / settings.phonikud_model
            if not model_path.exists():
                raise FileNotFoundError(f"Phonikud model not found at {model_path}")

            logger.info(f"Loading Phonikud model from {model_path}")
            self._phonikud_model = Phonikud(str(model_path))

        return self._phonikud_model

    def get_piper(self, model_path: Optional[str] = None) -> Piper:
        """Get or load the Piper TTS model."""
        if model_path:
            model_path = Path(model_path)
            config_path = model_path.with_suffix(".config.json")
        else:
            model_path = settings.models_dir / "piper" / settings.piper_model
            config_path = settings.models_dir / "piper" / settings.piper_config

        # Check if we need to load a different model
        if self._piper_model is None or (model_path and str(model_path) != getattr(self._piper_model, "_model_path", "")):
            if not model_path.exists():
                raise FileNotFoundError(f"Piper model not found at {model_path}")
            if not config_path.exists():
                raise FileNotFoundError(f"Piper config not found at {config_path}")

            logger.info(f"Loading Piper model from {model_path}")
            self._piper_model = Piper(str(model_path), str(config_path))
            self._piper_model._model_path = str(model_path)  # type: ignore

        return self._piper_model

    def get_zipvoice(self):
        """Get or load the ZipVoice TTS model."""
        if self._zipvoice_model is None:
            # Note: ZipVoice requires PyTorch and uses command-line inference
            # The ONNX version (zipvoice-onnx) is not yet available on PyPI
            # For now, ZipVoice is disabled until the ONNX version is released
            raise ImportError(
                "ZipVoice engine is not yet available. "
                "ZipVoice requires PyTorch and is not packaged as an ONNX library yet. "
                "Please use the 'piper' engine for Hebrew TTS. "
                "See https://github.com/k2-fsa/ZipVoice for more info."
            )

        return self._zipvoice_model

    def get_available_voices(self) -> dict[str, dict]:
        """Get all available voices."""
        return self._available_voices.copy()

    def get_voice_info(self, voice_id: str) -> Optional[dict]:
        """Get information about a specific voice."""
        return self._available_voices.get(voice_id)

    def is_zipvoice_available(self) -> bool:
        """Check if ZipVoice is available."""
        try:
            import zipvoice  # noqa: F401

            zipvoice_dir = settings.models_dir / settings.zipvoice_dir
            return (zipvoice_dir / settings.zipvoice_text_encoder).exists()
        except ImportError:
            return False


# Global model manager instance
model_manager = ModelManager()