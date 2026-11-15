"""Builds an engine on seeded synthetic data. The demo clock is the evening of day 5, inside the calling window."""
from __future__ import annotations

from datetime import datetime

from . import db
from .policy import Engine, Envelope
from .seed import seed_hero

DEMO_NOW = datetime(2026, 11, 5, 18, 0)


class Clock:
    def __init__(self, now: datetime = DEMO_NOW):
        self.now = now

    def __call__(self) -> datetime:
        return self.now


def make_engine(now: datetime = DEMO_NOW, path: str = ":memory:", seed: bool = True) -> Engine:
    con = db.connect(path)
    if seed:
        seed_hero(con)
    return Engine(con, Envelope.load(), Clock(now))
