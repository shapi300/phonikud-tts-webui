"""Speech generation router (OpenAI-compatible endpoint)."""

import base64
import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse

from api.src.schemas import PhonemizeRequest, PhonemizeResponse, SpeechRequest
from api.src.services.tts_service import tts_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["speech"])


@router.post("/audio/speech")
async def create_speech(request: SpeechRequest):
    """
    Generate speech from text (OpenAI-compatible endpoint).

    This endpoint accepts Hebrew text and returns audio in WAV format.
    Supports custom reference audio for ZipVoice voice cloning.
    """
    try:
        # Extract custom prompt parameters if provided
        custom_prompt_path = getattr(request, 'custom_prompt_path', None)
        custom_prompt_text = getattr(request, 'custom_prompt_text', None)
        
        # Generate speech
        audio_bytes, vocalized, phonemes, sample_rate = tts_service.generate_speech(
            text=request.input,
            engine=request.engine,
            voice_id=request.voice,
            speed=request.speed,
            volume_factor=request.volume_factor,
            custom_prompt_path=custom_prompt_path,
            custom_prompt_text=custom_prompt_text,
        )

        # Return audio as response
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "X-Vocalized-Text": vocalized.encode("utf-8").decode("latin-1"),
                "X-Phonemes": phonemes.encode("utf-8").decode("latin-1"),
                "X-Sample-Rate": str(sample_rate),
            },
        )

    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        raise HTTPException(status_code=503, detail=f"Model not available: {str(e)}")
    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error generating speech: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")


@router.post("/audio/speech/base64")
async def create_speech_base64(request: SpeechRequest):
    """
    Generate speech from text and return as base64 encoded audio.

    This is useful for web applications that need to embed audio directly.
    """
    try:
        # Generate speech
        audio_bytes, vocalized, phonemes, sample_rate = tts_service.generate_speech(
            text=request.input,
            engine=request.engine,
            voice_id=request.voice,
            speed=request.speed,
            volume_factor=request.volume_factor,
        )

        # Calculate duration
        import io

        import soundfile as sf

        buffer = io.BytesIO(audio_bytes)
        info = sf.info(buffer)
        duration = info.duration

        # Encode as base64
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        return {
            "audio": f"data:audio/wav;base64,{audio_base64}",
            "vocalized_text": vocalized,
            "phonemes": phonemes,
            "sample_rate": sample_rate,
            "duration_seconds": duration,
        }

    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        raise HTTPException(status_code=503, detail=f"Model not available: {str(e)}")
    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error generating speech: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")


@router.post("/phonemize", response_model=PhonemizeResponse)
async def phonemize_text(request: PhonemizeRequest):
    """
    Convert Hebrew text to phonemes.

    This endpoint shows how the text will be phonemized without generating audio.
    """
    try:
        vocalized, phonemes = tts_service.phonemize_text(request.text)
        return PhonemizeResponse(
            original_text=request.text,
            vocalized_text=vocalized,
            phonemes=phonemes,
        )
    except Exception as e:
        logger.exception(f"Error phonemizing text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to phonemize: {str(e)}")