"""Voice management router."""

import logging
import os
import uuid
import tempfile
import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from api.src.core.config import settings
from api.src.core.model_manager import model_manager
from api.src.schemas import HealthResponse, VoiceInfo, VoicesResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["voices"])

# Directory for custom voices
CUSTOM_VOICES_DIR = settings.models_dir / settings.zipvoice_dir / "prompts" / "custom"


@router.get("/voices", response_model=VoicesResponse)
async def list_voices():
    """
    List all available voices.

    Returns a list of voices that can be used for speech synthesis.
    """
    try:
        voices_dict = model_manager.get_available_voices()
        voices = [
            VoiceInfo(
                voice_id=voice_id,
                name=info["name"],
                engine=info["engine"],
                gender=info.get("gender", "unknown"),
                language="he",
            )
            for voice_id, info in voices_dict.items()
        ]

        return VoicesResponse(voices=voices)

    except Exception as e:
        logger.exception(f"Error listing voices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list voices: {str(e)}")


@router.get("/voices/{voice_id}", response_model=VoiceInfo)
async def get_voice(voice_id: str):
    """
    Get information about a specific voice.
    """
    try:
        voice_info = model_manager.get_voice_info(voice_id)
        if not voice_info:
            raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")

        return VoiceInfo(
            voice_id=voice_id,
            name=voice_info["name"],
            engine=voice_info["engine"],
            gender=voice_info.get("gender", "unknown"),
            language="he",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting voice: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get voice: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health status of the TTS service.

    Returns information about loaded models and available voices.
    """
    try:
        # Check if models are loaded
        phonikud_loaded = model_manager._phonikud_model is not None
        piper_loaded = model_manager._piper_model is not None
        zipvoice_available = model_manager.is_zipvoice_available()

        # Try to load models if not loaded
        if not phonikud_loaded:
            try:
                model_manager.get_phonikud()
                phonikud_loaded = True
            except Exception:
                pass

        if not piper_loaded:
            try:
                model_manager.get_piper()
                piper_loaded = True
            except Exception:
                pass

        voices = model_manager.get_available_voices()

        return HealthResponse(
            status="healthy" if phonikud_loaded else "degraded",
            phonikud_loaded=phonikud_loaded,
            piper_loaded=piper_loaded,
            zipvoice_available=zipvoice_available,
            voices_count=len(voices),
        )

    except Exception as e:
        logger.exception(f"Error in health check: {e}")
        return HealthResponse(
            status="unhealthy",
            phonikud_loaded=False,
            piper_loaded=False,
            zipvoice_available=False,
            voices_count=0,
        )


@router.get("/engines")
async def list_engines():
    """
    List available TTS engines.
    """
    engines = [
        {
            "name": "piper",
            "description": "Fast, lightweight TTS engine",
            "available": True,
        },
        {
            "name": "zipvoice",
            "description": "Voice cloning TTS with reference audio",
            "available": model_manager.is_zipvoice_available(),
        },
    ]

    return {"engines": engines}


def _ensure_custom_dir():
    """Ensure custom voices directory exists."""
    CUSTOM_VOICES_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/voices/upload")
async def upload_custom_voice(
    file: UploadFile = File(...),
    name: str = Form(...),
    reference_text: str = Form(...),
):
    """
    Upload a custom voice for ZipVoice voice cloning.

    Args:
        file: Audio file (WAV format recommended, 5-15 seconds)
        name: Name for the custom voice (alphanumeric, underscores, hyphens only)
        reference_text: The text that was spoken in the audio file

    Returns:
        Voice info with the new voice_id
    """
    try:
        # Validate name
        import re
        if not re.match(r'^[\w-]+$', name):
            raise HTTPException(
                status_code=400,
                detail="Name must contain only letters, numbers, underscores, and hyphens"
            )

        # Validate file type
        if not file.filename.lower().endswith(('.wav', '.mp3', '.ogg', '.m4a')):
            raise HTTPException(
                status_code=400,
                detail="File must be an audio file (WAV, MP3, OGG, M4A)"
            )

        # Ensure directory exists
        _ensure_custom_dir()

        # Generate unique filename
        voice_id = f"custom_{name}_{uuid.uuid4().hex[:8]}"
        filename = f"{voice_id}.wav"
        filepath = CUSTOM_VOICES_DIR / filename

        # Save the uploaded file
        with filepath.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        # Register the voice in model manager
        model_manager._available_voices[f"zipvoice_{voice_id}"] = {
            "engine": "zipvoice",
            "name": name,
            "prompt_path": str(filepath),
            "gender": "unknown",
            "custom": True,
        }

        logger.info(f"Uploaded custom voice: {voice_id}")

        return {
            "voice_id": f"zipvoice_{voice_id}",
            "name": name,
            "engine": "zipvoice",
            "prompt_path": str(filepath),
            "reference_text": reference_text,
            "message": "Custom voice uploaded successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error uploading custom voice: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload voice: {str(e)}")


@router.get("/voices/custom")
async def list_custom_voices():
    """
    List all custom uploaded voices.
    """
    try:
        custom_voices = []
        for voice_id, info in model_manager.get_available_voices().items():
            if info.get("custom"):
                custom_voices.append({
                    "voice_id": voice_id,
                    "name": info["name"],
                    "engine": "zipvoice",
                })

        return {"voices": custom_voices, "count": len(custom_voices)}

    except Exception as e:
        logger.exception(f"Error listing custom voices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list custom voices: {str(e)}")


@router.delete("/voices/custom/{voice_id}")
async def delete_custom_voice(voice_id: str):
    """
    Delete a custom uploaded voice.
    """
    try:
        voice_info = model_manager.get_voice_info(voice_id)
        if not voice_info:
            raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")

        if not voice_info.get("custom"):
            raise HTTPException(
                status_code=400,
                detail="Cannot delete built-in voices"
            )

        # Delete the file
        prompt_path = Path(voice_info.get("prompt_path", ""))
        if prompt_path.exists():
            prompt_path.unlink()

        # Remove from available voices
        del model_manager._available_voices[voice_id]

        logger.info(f"Deleted custom voice: {voice_id}")

        return {"message": f"Voice '{voice_id}' deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting custom voice: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete voice: {str(e)}")
