"""Text-to-speech helpers. No network: the Sarvam call is replaced."""
import httpx
import pytest

from keel.voice import tts


def test_audio_id_is_stable_and_depends_on_text_and_voice(monkeypatch):
    a = tts.audio_id("வணக்கம்")
    assert a == tts.audio_id("வணக்கம்") and a != tts.audio_id("நன்றி") and len(a) == 16
    monkeypatch.setenv("KEEL_TTS_SPEAKER", "ishita")
    assert tts.audio_id("வணக்கம்") != a


def test_speech_text_spells_figures_and_dates_for_the_voice():
    s = tts.speech_text("தினமும் ₹300 மட்டுமே. தொகை ₹2,800. முடிவு 11-12-2027 ஆகும்.")
    assert "300 ரூபாய்" in s and "2800 ரூபாய்" in s and "₹" not in s
    assert "11 டிசம்பர் 2027" in s and "11-12-2027" not in s
    assert tts.speech_text("Rs 2,800 deferred") == "2800 rupees deferred"


def test_ensure_audio_generates_once_then_reuses_the_cache(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(tts, "synthesize", lambda text, language="ta-IN": calls.append(text) or b"RIFFdata")
    p1 = tts.ensure_audio("சரி", tmp_path)
    p2 = tts.ensure_audio("சரி", tmp_path)
    assert p1 == p2 and p1.read_bytes() == b"RIFFdata" and len(calls) == 1


def test_synthesize_without_a_key_fails_cleanly(monkeypatch):
    monkeypatch.setattr(tts.config, "get", lambda name, default="": "")
    with pytest.raises(tts.TTSError):
        tts.synthesize("hi")


def test_synthesize_retries_on_rate_limit_and_decodes(monkeypatch):
    import base64
    n = {"i": 0}

    class R:
        def __init__(self, code, body=None):
            self.status_code, self._b, self.headers, self.text = code, body or {}, {"retry-after": "0"}, "x"
        def json(self):
            return self._b

    def post(url, json=None, headers=None, timeout=None):
        n["i"] += 1
        return R(429) if n["i"] < 3 else R(200, {"audios": [base64.b64encode(b"RIFFabc").decode()]})
    monkeypatch.setattr(httpx, "post", post)
    monkeypatch.setattr(tts.time, "sleep", lambda s: None)
    monkeypatch.setattr(tts.config, "get", lambda name, default="": "k" if name == "SARVAM_API_KEY" else default)
    assert tts.synthesize("சரி") == b"RIFFabc" and n["i"] == 3
