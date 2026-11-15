"""Sarvam text-to-speech with an on-disk cache. Audio is generated ahead of time (scripts/make_audio.py)
so the demo plays without the network. The key is read through keel.config and never printed."""
from __future__ import annotations

import base64
import hashlib
import re
import time
from pathlib import Path

import httpx

from .. import config

TTS_URL = "https://api.sarvam.ai/text-to-speech"
AUDIO_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "audio"
TA_MONTHS = ["ஜனவரி", "பிப்ரவரி", "மார்ச்", "ஏப்ரல்", "மே", "ஜூன்", "ஜூலை", "ஆகஸ்ட்", "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "டிசம்பர்"]


class TTSError(Exception):
    pass


def settings() -> tuple[str, str]:
    return config.get("KEEL_TTS_MODEL", "bulbul:v3"), config.get("KEEL_TTS_SPEAKER", "ritu")


def audio_id(text: str) -> str:
    """Stable id for a line of text and the voice it is spoken in. The screen uses it to find the cached audio."""
    model, speaker = settings()
    return hashlib.sha256(f"{model}|{speaker}|{text}".encode("utf-8")).hexdigest()[:16]


def audio_path(text: str, directory: Path | None = None) -> Path:
    return (directory or AUDIO_DIR) / f"{audio_id(text)}.wav"


def speech_text(text: str) -> str:
    """What the voice reads. The written line keeps its figures for the number-audit; the spoken line spells them
    the way a Tamil speaker says them: 'Rs 300' becomes '300 ரூபாய்' and 11-12-2027 becomes '11 டிசம்பர் 2027'."""
    text = re.sub(r"\bKeel\b", "கீல்", text)   # the Latin brand name is read as Tamil letters, not spelled out
    text = re.sub(r"₹\s?([\d,]+)", lambda m: f"{m.group(1).replace(',', '')} ரூபாய்", text)
    text = re.sub(r"Rs\.?\s?([\d,]+)", lambda m: f"{m.group(1).replace(',', '')} rupees", text)
    text = re.sub(r"\b(\d{1,2})-(\d{2})-(\d{4})\b", lambda m: f"{int(m.group(1))} {TA_MONTHS[int(m.group(2)) - 1]} {m.group(3)}", text)
    return text


def synthesize(text: str, language: str = "ta-IN") -> bytes:
    key = config.get("SARVAM_API_KEY")
    if not key:
        raise TTSError("SARVAM_API_KEY is not set")
    model, speaker = settings()
    body = {"text": speech_text(text), "target_language_code": language, "model": model, "speaker": speaker}
    for attempt in range(5):
        try:
            r = httpx.post(TTS_URL, json=body, headers={"api-subscription-key": key}, timeout=60)
        except httpx.HTTPError as e:
            if attempt == 4:
                raise TTSError(f"network error: {type(e).__name__}") from None
            time.sleep(1 + attempt)
            continue
        if r.status_code in (429, 500, 502, 503, 504) and attempt < 4:
            try:
                wait = float(r.headers.get("retry-after", ""))
            except ValueError:
                wait = min(2 ** attempt * 2, 20)
            time.sleep(min(wait, 30))
            continue
        if r.status_code != 200:
            raise TTSError(f"HTTP {r.status_code}: {r.text[:200].replace(key, '[key]')}")
        return base64.b64decode("".join(r.json()["audios"]))
    raise TTSError("no response")


def ensure_audio(text: str, directory: Path | None = None) -> Path:
    """Return the cached file, generating it first if it is missing."""
    path = audio_path(text, directory)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(synthesize(text))
    return path
