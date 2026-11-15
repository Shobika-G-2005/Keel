"""Round-trip check on the cached Tamil audio: send each file to Sarvam speech-to-text and compare what comes back
with what Keel meant to say. It catches mis-read figures and dropped words. It cannot judge how natural the Tamil
sounds; a Tamil speaker still has to listen. Usage: python scripts/check_audio_stt.py"""
import io
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from keel import config  # noqa: E402
from keel.policy.templates import TEMPLATES, render  # noqa: E402
from keel.voice import tts  # noqa: E402
from keel.policy.templates import fmt_date  # noqa: E402

HERO = {"name": "Murugan", "new_daily_amount_rupees": 300, "relief_days": 14, "deferred_rupees": 2800,
        "extension_days": 6, "new_end_date": fmt_date("2027-12-11"), "old_end_date": fmt_date("2027-12-05")}

STT_URL = "https://api.sarvam.ai/speech-to-text"
key = config.get("SARVAM_API_KEY")
if not key:
    sys.exit("SARVAM_API_KEY is not set")

TAMIL_DIGITS = str.maketrans("௦௧௨௩௪௫௬௭௮௯", "0123456789")


def transcribe(path: Path) -> str:
    with path.open("rb") as f:
        r = httpx.post(STT_URL, headers={"api-subscription-key": key},
                       files={"file": (path.name, f, "audio/wav")},
                       data={"model": "saarika:v2.5", "language_code": "ta-IN"}, timeout=120)
    if r.status_code != 200:
        return f"[HTTP {r.status_code}] {r.text[:150].replace(key, '[key]')}"
    return r.json().get("transcript", "")


# the speech-to-text model writes numbers as Tamil words, so each figure is accepted as digits or as these words
WORDS = {"14": ["பதினான்கு"], "300": ["முன்னூறு", "முந்நூறு"], "2800": ["இரண்டாயிரத்து எண்ணூறு"], "6": ["ஆறு"],
         "11": ["பதினொன்று"], "2027": ["இரண்டாயிரத்து இருபத்து ஏழு", "இரண்டாயிரத்து இருபத்தி ஏழு"]}


def figures(text: str) -> set[str]:
    return set(re.findall(r"\d+", text.translate(TAMIL_DIGITS).replace(",", "")))


def found_in(heard: str, figure: str) -> bool:
    return figure in figures(heard) or any(w in heard for w in WORDS.get(figure, []))


for tid in TEMPLATES:
    if tid == "free_text":
        continue
    _, written = render(tid, "ta", HERO)
    path = tts.audio_path(written)
    heard = transcribe(path)
    want = figures(tts.speech_text(written))
    missing = sorted(f for f in want if not found_in(heard, f))
    status = "ok     " if not missing else "CHECK  "
    print(f"{status}{tid}\n  said : {tts.speech_text(written)}\n  heard: {heard}\n  figures wanted {sorted(want)} missing {missing}\n")
