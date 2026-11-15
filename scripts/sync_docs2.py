"""One-off: record the voice work (cached Tamil audio, recorded backup) in the TRD, ARCHITECTURE and PRD."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent


def sub(text, old, new, label):
    assert old in text, f"not found: {label}"
    return text.replace(old, new, 1)


p = ROOT / "TRD.md"
t = p.read_text(encoding="utf-8")
t = sub(t, "scripted and model-driven agent, screen, scenario run); voice and the backup recording are not.",
        "scripted and model-driven agent, screen, scenario run, cached Tamil audio for Keel's lines, recorded backup video). Live speech-to-text and a live voice call are not built.", "trd status")
t = sub(t, "Text chat is the baseline; Tamil speech-to-text and text-to-speech are added if time allows | Text adapter; Sarvam; LiveKit or Pipecat |",
        "Text chat is the baseline. Keel's lines are spoken in Tamil from pre-generated audio; live speech-to-text is not built | Text adapter; Sarvam text-to-speech (`bulbul:v3`) |", "trd channel")
t = sub(t, "| F6 | Must | The call runs in Tamil: speech-to-text for the merchant, text-to-speech for the agent. |",
        "| F6 | Must | Keel's lines are spoken in Tamil. Audio is generated ahead of time with Sarvam text-to-speech and cached (`data/audio`, `scripts/make_audio.py`), so playback needs no network. The merchant's side is text in the demo; live speech-to-text is not built. |", "trd F6")
t = sub(t, "| F9 | Should | A **recorded** run of the golden path exists as a last-resort backup and is shown as a recording. |",
        "| F9 | Should | A **recorded** run exists as a last-resort backup: `backup/Keel_demo_backup.mp4` (about 100 seconds: the Tamil call with audio, the schedule change, one escalation, the audit tamper test, the results). Rebuild it with `scripts/record_backup.py`. |", "trd F9")
t = sub(t, "### 4.3 Voice (to be confirmed by the voice owner)", "### 4.3 Voice", "trd 4.3 heading")
t = sub(t, "- Sarvam speech-to-text and text-to-speech, Tamil. The Sarvam docs gave inconsistent model names, so check the current names before building.\n- LiveKit or Pipecat to run the call loop. One is chosen today.\n- If real-time voice is not stable by the end of 14 Nov, the demo runs the text-mode flow with pre-generated Tamil audio for the agent's lines, plus the recorded run.",
        "- Built: Sarvam text-to-speech, model `bulbul:v3`, speaker `ritu`, language `ta-IN` (`keel/voice/tts.py`). Each line is generated once and cached by a hash of the text and voice. The screen shows a Listen button on each Keel line and a Play the call button.\n- The spoken text differs slightly from the written text: `₹300` is read as `300 ரூபாய்` and `11-12-2027` as `11 டிசம்பர் 2027`. The number-audit runs on the written text.\n- Not built: live speech-to-text, and a LiveKit or Pipecat call loop. The demo plays cached audio over the text-mode flow.\n- Not verified: how natural the Tamil sounds, and whether numbers are read correctly. A Tamil speaker must listen to every line in `data/audio` before the demo.", "trd voice bullets")
t = sub(t, "| Voice | Sarvam STT and TTS; LiveKit or Pipecat | **Open: decide today** |",
        "| Voice | Sarvam `bulbul:v3` text-to-speech with cached audio; no live speech-to-text | **Built (playback only)** |", "trd tech voice")
t = sub(t, "  voice/         text-mode channel (STT, TTS and the call runner are not built)", "  voice/         text-mode channel and the Sarvam text-to-speech cache (no live speech-to-text)", "trd layout")
t = sub(t, "2. Voice: Sarvam speech with LiveKit or Pipecat, or pre-generated audio for key lines (owner and date to be named).",
        "2. Live speech-to-text and a real-time call loop (LiveKit or Pipecat): not built; decide whether it is worth the time before the event.", "trd open 2")
t = sub(t, "7. A Tamil speaker must review the spoken lines in `policy/templates.py` and the yes-word list.",
        "7. A Tamil speaker must review the written lines in `policy/templates.py`, listen to the generated audio, and check the yes-word list.", "trd open 7")
p.write_text(t, encoding="utf-8")

p = ROOT / "ARCHITECTURE.md"
a = p.read_text(encoding="utf-8")
a = sub(a, "The core is built and tested; voice and the backup recording are not.",
        "The core is built and tested, Keel's lines have cached Tamil audio, and a recorded backup video exists; live speech-to-text is not built.", "arch status")
a = re.sub(r"\| Voice \| Sarvam speech-to-text and text-to-speech for Tamil;.*?\n", "| Voice | Sarvam text-to-speech (`bulbul:v3`, Tamil) with pre-generated, cached audio for Keel's lines; text chat for the merchant; a recorded run in `backup/` as the last-resort backup. Live speech-to-text and a LiveKit or Pipecat call loop are not built | Plays Keel's lines in Tamil and carries the merchant's text |\n", a, count=1)
a = sub(a, "2. LiveKit or Pipecat for the call (whichever the voice owner already knows).\n3. Who owns the voice loop and the backup recording.",
        "2. Whether a live speech-to-text call loop (LiveKit or Pipecat) is worth building before the event.\n3. Who checks the Tamil lines and the generated audio.", "arch open")
p.write_text(a, encoding="utf-8")

p = ROOT / "PRD.md"
r = p.read_text(encoding="utf-8")
r = re.sub(r"Voice and the backup rec[^\n]*?not done\.", "Keel's lines have cached Tamil audio and a recorded backup video exists; live speech-to-text is not built.", r, count=1)
p.write_text(r, encoding="utf-8")
print("docs updated")
