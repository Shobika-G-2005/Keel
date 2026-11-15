"""Fixed sentences the agent may speak. Rupee figures and dates are filled from tool output.
Tamil lines are a first draft: a Tamil speaker must review them before the demo."""
from __future__ import annotations

import re

# id -> (discloses loan details, {language: text})
TEMPLATES: dict[str, tuple[bool, dict[str, str]]] = {
    "greet_verify": (False, {
        "ta": "வணக்கம் {name}. நான் Keel, உங்கள் கடன் உதவியாளர். பாதுகாப்புக்காக, உங்கள் பதிவு செய்யப்பட்ட மொபைல் எண்ணின் கடைசி நான்கு எண்களைச் சொல்லுங்கள்.",
        "en": "Hello {name}, this is Keel, your loan assistant. For your safety, please tell me the last four digits of your registered mobile number.",
    }),
    "verify_retry": (False, {
        "ta": "அந்த எண்கள் பொருந்தவில்லை. கடைசி நான்கு எண்களை மீண்டும் சொல்லுங்கள்.",
        "en": "That did not match. Please say the last four digits again.",
    }),
    "id_failed": (False, {
        "ta": "பாதுகாப்பு காரணமாக இந்த அழைப்பை இப்போது முடிக்கிறோம். நன்றி.",
        "en": "For your safety we are ending this call now. Thank you.",
    }),
    "situation": (True, {
        "ta": "இந்த வாரம் உங்கள் தினசரி விற்பனை வழக்கத்தை விடக் குறைவாக இருப்பதைக் கவனித்தோம். அதனால், உங்களுக்குக் கொஞ்சம் அவகாசம் தர விரும்புகிறோம்.",
        "en": "We noticed your daily sales are lower than usual this week, so we would like to give you some room.",
    }),
    "offer": (True, {
        "ta": "நீங்கள் விரும்பினால், அடுத்த {relief_days} நாட்களுக்கு உங்கள் தினசரி தவணையை ₹{new_daily_amount_rupees} ஆகக் குறைக்கலாம். தள்ளிவைக்கப்படும் தொகை ₹{deferred_rupees}. கடன் {extension_days} நாட்கள் தாமதமாக, {new_end_date} அன்று முடியும்.",
        "en": "If you like, we can reduce your daily repayment to Rs {new_daily_amount_rupees} for the next {relief_days} days. Rs {deferred_rupees} is deferred, and the loan ends {extension_days} days later, on {new_end_date}.",
    }),
    "readback": (True, {
        "ta": "உறுதிப்படுத்துகிறேன்: அடுத்த {relief_days} நாட்களுக்கு, தினமும் ₹{new_daily_amount_rupees} மட்டும் செலுத்தினால் போதும். கடன் முடியும் தேதி {extension_days} நாட்கள் தள்ளிப்போய், {new_end_date} ஆகும். இதற்கு ஒப்புக்கொள்கிறீர்களா? ஒப்புக்கொண்டால், ஆம் என்று சொல்லுங்கள்.",
        "en": "To confirm: for the next {relief_days} days you pay only Rs {new_daily_amount_rupees} a day. The loan end date moves {extension_days} days later to {new_end_date}. Do you agree? Please say yes.",
    }),
    "readback_again": (True, {
        "ta": "மன்னிக்கவும், சரியாகக் கேட்கவில்லை. மீண்டும் சொல்கிறேன்: அடுத்த {relief_days} நாட்களுக்கு தினமும் ₹{new_daily_amount_rupees}. கடன் {extension_days} நாட்கள் தாமதமாக, {new_end_date} அன்று முடியும். ஒப்புக்கொள்கிறீர்களா? ஒப்புக்கொண்டால், ஆம் என்று சொல்லுங்கள்.",
        "en": "Sorry, I did not catch that. Once more: for the next {relief_days} days Rs {new_daily_amount_rupees} a day. The loan ends {extension_days} days later on {new_end_date}. Do you agree? Please say yes.",
    }),
    "applied": (True, {
        "ta": "சரி, புதிய தவணை இப்போது நடைமுறைக்கு வந்துவிட்டது. அடுத்த {relief_days} நாட்களுக்கு தினமும் ₹{new_daily_amount_rupees}. நன்றி!",
        "en": "Done. Your new repayment is in place: Rs {new_daily_amount_rupees} a day for the next {relief_days} days. Thank you!",
    }),
    "declined_ack": (False, {
        "ta": "புரிகிறது. உங்கள் தற்போதைய தவணையில் எந்த மாற்றமும் இல்லை. நன்றி.",
        "en": "Understood. Your current repayment stays the same. Thank you.",
    }),
    "handover": (False, {
        "ta": "உங்கள் நிலைமை எங்களுக்குப் புரிகிறது. எங்கள் குழுவில் ஒருவர் விரைவில் உங்களை அழைப்பார். நன்றி.",
        "en": "We understand. A member of our team will call you shortly. Thank you.",
    }),
    # Model-written wording. Allowed, but every figure in it is number-audited.
    "free_text": (True, {"ta": "{text}", "en": "{text}"}),
}

NUM_RE = re.compile(r"\d{1,3}(?:,\d{2,3})+|\d+")


def indian(n: int) -> str:
    """2,00,000 style grouping."""
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        head = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", head)
        s = f"{head},{tail}"
    return ("-" if n < 0 else "") + s


def numbers_in(text: str) -> list[int]:
    return [int(m.replace(",", "")) for m in NUM_RE.findall(text)]


def fact_numbers(obj) -> set[int]:
    """Every integer that appears in a tool result, including parts of ISO dates."""
    out: set[int] = set()
    if isinstance(obj, bool):
        return out
    if isinstance(obj, int):
        out.add(obj)
    elif isinstance(obj, str):
        out.update(numbers_in(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            out |= fact_numbers(v)
    elif isinstance(obj, (list, tuple, set)):
        for v in obj:
            out |= fact_numbers(v)
    return out


def fmt_date(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{d}-{m}-{y}"


class _Safe(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def render(template_id: str, lang: str, values: dict) -> tuple[bool, str]:
    discloses, texts = TEMPLATES[template_id]
    text = texts.get(lang) or texts["en"]
    shown = {}
    for k, v in values.items():
        if isinstance(v, bool):
            shown[k] = v
        elif isinstance(v, int) and k.endswith("_rupees"):
            shown[k] = indian(v)
        else:
            shown[k] = v
    return discloses, text.format_map(_Safe(shown))
