"""API client for the Gradio UI."""

import httpx
from typing import Optional


API_BASE_URL = "http://localhost:8880"


async def check_api_status() -> tuple[bool, list[str]]:
    """
    Check if the API is available and get available voices.

    Returns:
        Tuple of (is_available, voice_ids)
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check health
            health_response = await client.get(f"{API_BASE_URL}/v1/health")
            if health_response.status_code != 200:
                return False, []

            # Get voices
            voices_response = await client.get(f"{API_BASE_URL}/v1/voices")
            if voices_response.status_code == 200:
                data = voices_response.json()
                voices = [v["voice_id"] for v in data.get("voices", [])]
                return True, voices

            return True, []

    except Exception as e:
        print(f"Error checking API status: {e}")
        return False, []


async def generate_speech(
    text: str,
    voice: str = "shaul",
    engine: str = "piper",
    speed: float = 1.0,
    volume_factor: float = 2.0,
) -> tuple[Optional[bytes], str, str]:
    """
    Generate speech from text.

    Args:
        text: Hebrew text to synthesize
        voice: Voice ID
        engine: TTS engine (piper or zipvoice)
        speed: Speech speed multiplier
        volume_factor: Volume amplification

    Returns:
        Tuple of (audio_bytes, vocalized_text, phonemes)
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/v1/audio/speech",
                json={
                    "model": "phonikud",
                    "input": text,
                    "voice": voice,
                    "engine": engine,
                    "speed": speed,
                    "volume_factor": volume_factor,
                },
            )

            if response.status_code == 200:
                audio_bytes = response.content
                vocalized = response.headers.get("X-Vocalized-Text", "")
                phonemes = response.headers.get("X-Phonemes", "")
                return audio_bytes, vocalized, phonemes
            else:
                error = response.json().get("detail", "Unknown error")
                raise Exception(error)

    except Exception as e:
        print(f"Error generating speech: {e}")
        raise


async def generate_speech_base64(
    text: str,
    voice: str = "shaul",
    engine: str = "piper",
    speed: float = 1.0,
    volume_factor: float = 2.0,
) -> dict:
    """
    Generate speech and return as base64.

    Args:
        text: Hebrew text to synthesize
        voice: Voice ID
        engine: TTS engine (piper or zipvoice)
        speed: Speech speed multiplier
        volume_factor: Volume amplification

    Returns:
        Dict with audio (data URI), vocalized_text, phonemes, etc.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/v1/audio/speech/base64",
                json={
                    "model": "phonikud",
                    "input": text,
                    "voice": voice,
                    "engine": engine,
                    "speed": speed,
                    "volume_factor": volume_factor,
                },
            )

            if response.status_code == 200:
                return response.json()
            else:
                error = response.json().get("detail", "Unknown error")
                raise Exception(error)

    except Exception as e:
        print(f"Error generating speech: {e}")
        raise


async def phonemize_text(text: str) -> tuple[str, str]:
    """
    Convert Hebrew text to phonemes.

    Args:
        text: Hebrew text

    Returns:
        Tuple of (vocalized_text, phonemes)
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/v1/phonemize",
                json={"text": text},
            )

            if response.status_code == 200:
                data = response.json()
                return data["vocalized_text"], data["phonemes"]
            else:
                error = response.json().get("detail", "Unknown error")
                raise Exception(error)

    except Exception as e:
        print(f"Error phonemizing text: {e}")
        raise


async def get_engines() -> list[dict]:
    """
    Get available TTS engines.

    Returns:
        List of engine info dicts
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE_URL}/v1/engines")
            if response.status_code == 200:
                return response.json().get("engines", [])
            return []

    except Exception as e:
        print(f"Error getting engines: {e}")
        return []