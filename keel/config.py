"""Loads settings from the environment, falling back to the project's .env file.
Secrets are read here and nowhere else. Values are never printed or logged."""
from __future__ import annotations

import os
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def load_env(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if value and key not in os.environ:  # a real environment variable wins over the file
            os.environ[key] = value


def get(name: str, default: str = "") -> str:
    load_env()
    return os.environ.get(name, default)


def has_key(name: str) -> bool:
    return bool(get(name))
