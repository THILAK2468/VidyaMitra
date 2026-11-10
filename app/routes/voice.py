import uuid
import time
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.services.gnani_stt import transcribe_audio, STTError
from app.services.tutor_engine import generate_tutor_response
from app.services.gnani_tts import generate_speech, TTSError

router = APIRouter(
    prefix="/voice",
    tags=["Voice & Speech"]
)

# Directory to store generated audio clips for frontend playback
AUDIO_OUTPUT_DIR = Path("app/static/audio")
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class SynthesizeRequest(BaseModel):
    text: str
    language: str = "te"


@router.post("/transcribe")
async def transcribe(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form("te")
):
    """
    Transcribes an uploaded audio file using Gnani Prisma STT.
    """
    content = await audio_file.read()
    try:
        result = transcribe_audio(
            audio_bytes=content,
            filename=audio_file.filename or "audio.wav",
            content_type=audio_file.content_type or "audio/wav",
            language_code=language
        )
        return result
    except STTError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected transcription error: {exc}")


@router.post("/ask")
async def voice_ask(
    audio_file: UploadFile = File(...),
    language: str = Form("te"),
    play_audio: bool = Form(True),
    previous_topic: Optional[str] = Form(None)
):
    """
    End-to-end voice query flow:
    1. Transcribe audio using Gnani Prisma STT
    2. Retrieve curriculum & generate grounded explanation via LLM (with follow-up support)
    3. Synthesize spoken explanation with Gnani Timbre TTS (optional)
    4. Return transcript, answer, example, key terms, and timing metrics
    """
    overall_start = time.time()
    audio_content = await audio_file.read()

    # Step 1: Speech-to-Text
    try:
        stt_result = transcribe_audio(
            audio_bytes=audio_content,
            filename=audio_file.filename or "question.wav",
            content_type=audio_file.content_type or "audio/wav",
            language_code=language
        )
    except STTError as err:
        raise HTTPException(status_code=err.status_code, detail=f"STT Error: {err.message}")

    transcript = stt_result.get("transcript", "").strip()
    if not transcript:
        raise HTTPException(
            status_code=400,
            detail="Could not detect speech in the uploaded audio. Please speak clearly and try again."
        )

    # Step 2: Curriculum Retrieval & Grounded LLM Tutor (with follow-up context)
    tutor_result = generate_tutor_response(
        question=transcript,
        language=language,
        previous_topic=previous_topic
    )

    # Step 3: Text-to-Speech (if enabled and tutor generated an answer)
    audio_url = None
    tts_latency = 0.0
    audio_error = None

    if play_audio and tutor_result.get("answer"):
        speech_filename = f"reply_{uuid.uuid4().hex[:8]}.wav"
        speech_filepath = AUDIO_OUTPUT_DIR / speech_filename
        try:
            tts_res = generate_speech(
                text=tutor_result["answer"],
                output_path=str(speech_filepath),
                language=language
            )
            audio_url = f"/static/audio/{speech_filename}"
            tts_latency = tts_res.get("latency", 0.0)
        except TTSError as err:
            # Per RULES.md: TTS failure does not remove the text answer
            audio_error = err.message
        except Exception as exc:
            audio_error = str(exc)

    total_latency = round(time.time() - overall_start, 3)

    return {
        "success": tutor_result["success"],
        "transcript": transcript,
        "topic": tutor_result.get("topic"),
        "language": tutor_result.get("language"),
        "answer": tutor_result.get("answer"),
        "example": tutor_result.get("example"),
        "key_terms": tutor_result.get("key_terms", []),
        "source": tutor_result.get("source"),
        "audio_url": audio_url,
        "audio_error": audio_error,
        "timings": {
            "stt_latency": stt_result.get("latency", 0.0),
            "stt_processing_time": stt_result.get("processing_time"),
            "llm_latency": tutor_result.get("latency", 0.0),
            "tts_latency": tts_latency,
            "total_latency": total_latency
        }
    }


@router.post("/synthesize")
async def synthesize(request: SynthesizeRequest):
    """
    Directly converts text to speech using Gnani Timbre.
    """
    speech_filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
    speech_filepath = AUDIO_OUTPUT_DIR / speech_filename

    try:
        res = generate_speech(
            text=request.text,
            output_path=str(speech_filepath),
            language=request.language
        )
        return {
            "success": True,
            "audio_url": f"/static/audio/{speech_filename}",
            "latency": res.get("latency"),
            "language": res.get("language")
        }
    except TTSError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)

