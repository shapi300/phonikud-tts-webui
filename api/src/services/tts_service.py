"""TTS Service for generating speech from text."""

import io
import logging
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf
from phonikud import phonemize

from api.src.core.config import settings
from api.src.core.model_manager import model_manager

logger = logging.getLogger(__name__)


class TTSService:
    """Service for text-to-speech generation."""

    def __init__(self):
        self._custom_prompts: dict[str, tuple[str, str]] = {}  # voice_id -> (wav_path, ref_phonemes)

    def phonemize_text(self, text: str) -> tuple[str, str]:
        """
        Convert Hebrew text to phonemes.

        Args:
            text: Hebrew text (with or without diacritics)

        Returns:
            Tuple of (vocalized_text, phonemes)
        """
        phonikud = model_manager.get_phonikud()
        vocalized = phonikud.add_diacritics(text)
        phonemes = phonemize(vocalized)
        return vocalized, phonemes

    def generate_piper(
        self,
        phonemes: str,
        speed: Optional[float] = None,
        volume_factor: Optional[float] = None,
        voice_id: Optional[str] = None,
    ) -> tuple[np.ndarray, int]:
        """
        Generate audio using Piper TTS.

        Args:
            phonemes: Phonemes string
            speed: Speed multiplier
            volume_factor: Volume amplification factor
            voice_id: Voice identifier

        Returns:
            Tuple of (audio_samples, sample_rate)
        """
        speed = speed or settings.default_speed
        volume_factor = volume_factor or settings.default_volume_factor

        # Get voice info if specified
        model_path = None
        if voice_id:
            voice_info = model_manager.get_voice_info(voice_id)
            if voice_info and voice_info["engine"] == "piper":
                model_path = voice_info.get("model_path")

        piper = model_manager.get_piper(model_path)

        # Generate audio
        samples, sample_rate = piper.create(
            phonemes,
            is_phonemes=True,
            length_scale=settings.piper_length_scale / speed,
            noise_scale=settings.piper_noise_scale,
            noise_w=settings.piper_noise_w,
        )

        # Apply volume boost
        if volume_factor != 1.0:
            samples = samples * volume_factor
            samples = np.clip(samples, -1.0, 1.0)

        return samples, sample_rate

    def generate_zipvoice(
        self,
        phonemes: str,
        speed: Optional[float] = None,
        volume_factor: Optional[float] = None,
        voice_id: Optional[str] = None,
        custom_prompt_path: Optional[str] = None,
        custom_prompt_text: Optional[str] = None,
    ) -> tuple[np.ndarray, int]:
        """
        Generate audio using ZipVoice TTS.

        Args:
            phonemes: Target phonemes to synthesize
            speed: Speed multiplier
            volume_factor: Volume amplification factor
            voice_id: Voice identifier
            custom_prompt_path: Path to custom reference audio
            custom_prompt_text: Text for the reference audio (for phonemization)

        Returns:
            Tuple of (audio_samples, sample_rate)
        """
        speed = speed or settings.default_speed
        volume_factor = volume_factor or settings.default_volume_factor

        zipvoice = model_manager.get_zipvoice()

        # Get reference audio and phonemes
        if custom_prompt_path and custom_prompt_text:
            ref_wav = custom_prompt_path
            _, ref_phonemes = self.phonemize_text(custom_prompt_text)
        elif voice_id:
            voice_info = model_manager.get_voice_info(voice_id)
            if voice_info and voice_info["engine"] == "zipvoice":
                ref_wav = voice_info["prompt_path"]
                # Use default reference text for known prompts
                ref_text = self._get_default_ref_text(voice_info["name"])
                _, ref_phonemes = self.phonemize_text(ref_text)
            else:
                raise ValueError(f"ZipVoice voice '{voice_id}' not found")
        else:
            # Use first available ZipVoice prompt
            voices = model_manager.get_available_voices()
            for vid, info in voices.items():
                if info["engine"] == "zipvoice":
                    ref_wav = info["prompt_path"]
                    ref_text = self._get_default_ref_text(info["name"])
                    _, ref_phonemes = self.phonemize_text(ref_text)
                    voice_id = vid
                    break
            else:
                raise ValueError("No ZipVoice prompts available")

        # Generate audio
        samples, sample_rate = zipvoice.create(ref_wav, ref_phonemes, phonemes, speed=speed)

        # Apply volume boost
        if volume_factor != 1.0:
            samples = samples * volume_factor
            samples = np.clip(samples, -1.0, 1.0)

        return samples, sample_rate

    def _get_default_ref_text(self, prompt_name: str) -> str:
        """Get default reference text for known prompts."""
        # Default reference text used in examples
        return "הלכתי למכולת לקנות לחם וחלב, ובדרך פגשתי חבר ישן שלא ראיתי הרבה זמן."

    def generate_speech(
        self,
        text: str,
        engine: Optional[str] = None,
        voice_id: Optional[str] = None,
        speed: Optional[float] = None,
        volume_factor: Optional[float] = None,
        custom_prompt_path: Optional[str] = None,
        custom_prompt_text: Optional[str] = None,
    ) -> tuple[bytes, str, str, int]:
        """
        Generate speech from Hebrew text.

        Args:
            text: Hebrew text
            engine: TTS engine ("piper" or "zipvoice")
            voice_id: Voice identifier
            speed: Speed multiplier
            volume_factor: Volume amplification factor
            custom_prompt_path: Path to custom reference audio (ZipVoice only)
            custom_prompt_text: Text for the reference audio (ZipVoice only)

        Returns:
            Tuple of (audio_bytes, vocalized_text, phonemes, sample_rate)
        """
        engine = engine or settings.default_engine

        # Phonemize text
        vocalized, phonemes = self.phonemize_text(text)
        logger.debug(f"Phonemized '{text}' -> '{phonemes}'")

        # Generate audio based on engine
        if engine == "piper":
            samples, sample_rate = self.generate_piper(
                phonemes, speed=speed, volume_factor=volume_factor, voice_id=voice_id
            )
        elif engine == "zipvoice":
            samples, sample_rate = self.generate_zipvoice(
                phonemes,
                speed=speed,
                volume_factor=volume_factor,
                voice_id=voice_id,
                custom_prompt_path=custom_prompt_path,
                custom_prompt_text=custom_prompt_text,
            )
        else:
            raise ValueError(f"Unknown TTS engine: {engine}")

        # Convert to audio bytes
        buffer = io.BytesIO()
        sf.write(buffer, samples, sample_rate, format="WAV")
        buffer.seek(0)
        audio_bytes = buffer.read()

        return audio_bytes, vocalized, phonemes, sample_rate

    def register_custom_prompt(self, voice_id: str, wav_path: str, ref_text: str) -> None:
        """Register a custom prompt for ZipVoice voice cloning."""
        self._custom_prompts[voice_id] = (wav_path, ref_text)

    def get_custom_prompt(self, voice_id: str) -> Optional[tuple[str, str]]:
        """Get custom prompt for a voice."""
        return self._custom_prompts.get(voice_id)


# Global TTS service instance
tts_service = TTSService()