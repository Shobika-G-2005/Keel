from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from pathlib import Path

import yaml

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "envelope.yaml"


def _t(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


@dataclass(frozen=True)
class Envelope:
    envelope_id: str
    stress_threshold_pct: int
    stress_consecutive_days: int
    min_daily_amount_rupees: int
    max_relief_days: int
    max_extension_days: int
    call_window_start: time
    call_window_end: time
    requires_consent: bool = True

    def in_window(self, t: time) -> bool:
        return self.call_window_start <= t < self.call_window_end

    @classmethod
    def load(cls, path: str | Path = DEFAULT_PATH) -> "Envelope":
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        raw["call_window_start"] = _t(raw["call_window_start"])
        raw["call_window_end"] = _t(raw["call_window_end"])
        return cls(**raw)
