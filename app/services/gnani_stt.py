import os
import time
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GNANI_API_KEY")
STT_URL = os.getenv("GNANI_STT_URL", "https://api.vachana.ai/stt/v3")
DEFAULT_LANGUAGE = os.getenv("GNANI_STT_LANGUAGE", "te-IN")

MAX_AUDIO_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".ogg", ".webm", ".m4a"}


class STTError(Exception):
    """Custom exception for Speech-to-Text failures."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def validate_audio(audio_bytes: bytes, filename: str) -> None:
    """Validates audio file size and extension."""
    if not audio_bytes:
        raise STTError("Audio file is empty", status_code=400)

    if len(audio_bytes) > MAX_AUDIO_SIZE_BYTES:
        max_mb = MAX_AUDIO_SIZE_BYTES / (1024 * 1024)
        raise STTError(f"Audio file exceeds maximum size of {max_mb:.0f}MB", status_code=400)

    _, ext = os.path.splitext(filename.lower())
    if ext and ext not in ALLOWED_EXTENSIONS:
        raise STTError(
            f"Unsupported audio extension '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            status_code=400
        )


def transcribe_audio(
    audio_bytes: bytes,
    filename: str = "audio.wav",
    content_type: str = "audio/wav",
    language_code: Optional[str] = None,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """
    Transcribes audio bytes using the Gnani Prisma STT API.
    
    Returns:
        dict with success, transcript, model, latency, and request_id.
    """
    if not API_KEY:
        raise STTError("GNANI_API_KEY is not configured", status_code=500)

    validate_audio(audio_bytes, filename)

    lang = language_code or DEFAULT_LANGUAGE
    # Map common aliases to Gnani language codes
    if lang.lower() in ("te", "telugu"):
        lang = "te-IN"
    elif lang.lower() in ("en", "english"):
        lang = "en-IN"

    headers = {
        "X-API-Key-ID": API_KEY
    }

    files = {
        "audio_file": (filename, audio_bytes, content_type)
    }
    data = {
        "language_code": lang
    }

    start_time = time.time()
    response = None

    # Safe bounded retry for transient gateway timeouts (502, 503, 504)
    for attempt in range(2):
        try:
            response = httpx.post(
                STT_URL,
                headers=headers,
                files={"audio_file": (filename, audio_bytes, content_type)},
                data=data,
                timeout=timeout
            )
            if response.status_code not in (502, 503, 504):
                break
            time.sleep(1.0)
        except httpx.TimeoutException:
            if attempt == 1:
                raise STTError(f"STT request timed out after {timeout:.1f} seconds", status_code=504)
            time.sleep(1.0)
        except httpx.RequestError as exc:
            if attempt == 1:
                raise STTError(f"STT network error: {exc}", status_code=502)
            time.sleep(1.0)

    latency = round(time.time() - start_time, 3)

    if response.status_code == 401:
        raise STTError("Gnani API authentication failed (invalid or expired key)", status_code=401)
    elif response.status_code == 422:
        raise STTError(f"Invalid STT request parameters: {response.text}", status_code=422)
    elif response.status_code != 200:
        raise STTError(
            f"Gnani STT error ({response.status_code}): {response.text[:500]}",
            status_code=response.status_code
        )

    try:
        res_data = response.json()
    except Exception as e:
        raise STTError(f"Failed to parse STT JSON response: {e}", status_code=502)

    transcript = res_data.get("transcript", "").strip()

    return {
        "success": True,
        "transcript": transcript,
        "language_code": lang,
        "model": res_data.get("model", "prisma-v2.5"),
        "processing_time": res_data.get("processing_time"),
        "latency": latency,
        "request_id": res_data.get("request_id")
    }

