"""Pre-generate Tamil audio for every sentence Keel can say in the demo, so playback needs no network.
Usage: python scripts/make_audio.py [--force]. Existing files are kept unless --force is given."""
import io
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from keel.policy.templates import TEMPLATES, fmt_date, render  # noqa: E402
from keel.voice import tts  # noqa: E402

# the hero case from the PRD: Murugan, Rs 500 a day, relief Rs 300 for 14 days, loan ends 6 days later
HERO = {"name": "Murugan", "new_daily_amount_rupees": 300, "relief_days": 14, "deferred_rupees": 2800,
        "extension_days": 6, "new_end_date": fmt_date("2027-12-11"), "old_end_date": fmt_date("2027-12-05")}

force = "--force" in sys.argv
made = kept = 0
for tid in TEMPLATES:
    if tid == "free_text":
        continue
    _, text = render(tid, "ta", HERO)
    path = tts.audio_path(text)
    if path.exists() and not force:
        kept += 1
        status = "kept "
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(tts.synthesize(text))
        made += 1
        status = "made "
    with wave.open(str(path)) as w:
        secs = w.getnframes() / w.getframerate()
    print(f"{status} {tid:15} {secs:5.1f}s  {path.name}")
print(f"\n{made} generated, {kept} kept, in {tts.AUDIO_DIR}")
