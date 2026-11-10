import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GNANI_API_KEY")
TTS_URL = os.getenv("GNANI_TTS_URL", "https://api.vachana.ai/api/v1/tts/inference")
TTS_MODEL = os.getenv("GNANI_TTS_MODEL", "timbre-v2.5")
TTS_VOICE = os.getenv("GNANI_TTS_VOICE", "Suhana")
DEFAULT_LANGUAGE = os.getenv("GNANI_TTS_LANGUAGE", "te-IN")


class TTSError(Exception):
    """Custom exception for Text-to-Speech failures."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def generate_speech(
    text: str,
    output_path: str = "output.wav",
    language: Optional[str] = None,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """
    Generates speech audio from text using Gnani Timbre TTS.
    Returns metadata including latency and output path.
    """
    if not API_KEY:
        raise TTSError("GNANI_API_KEY is missing in .env", status_code=500)

    if not text or not text.strip():
        raise TTSError("Cannot generate speech for empty text", status_code=400)

    lang = language or DEFAULT_LANGUAGE
    if lang.lower() in ("te", "telugu"):
        lang = "te-IN"
    elif lang.lower() in ("en", "english"):
        lang = "en-IN"

    payload = {
        "text": text.strip(),
        "model": TTS_MODEL,
        "voice": TTS_VOICE,
        "language": lang,
        "speed": 1.0,
        "audio_config": {
            "encoding": "linear_pcm",
            "container": "wav",
            "num_channels": 1,
            "sample_rate": 48000,
            "sample_width": 2
        }
    }

    headers = {
        "X-API-Key-ID": API_KEY,
        "Content-Type": "application/json"
    }

    start_time = time.time()
    try:
        response = httpx.post(
            TTS_URL,
            json=payload,
            headers=headers,
            timeout=timeout
        )
    except httpx.TimeoutException:
        raise TTSError(f"TTS request timed out after {timeout:.1f}s", status_code=504)
    except httpx.RequestError as exc:
        raise TTSError(f"TTS network error: {exc}", status_code=502)

    latency = round(time.time() - start_time, 3)

    if response.status_code != 200:
        raise TTSError(
            f"Gnani TTS failed: {response.status_code} - {response.text[:500]}",
            status_code=response.status_code
        )

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_bytes(response.content)

    return {
        "success": True,
        "output_path": str(out_file),
        "file_size": len(response.content),
        "latency": latency,
        "language": lang
    }
