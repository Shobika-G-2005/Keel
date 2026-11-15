"""Text-mode merchant channel. Voice (speech-to-text, text-to-speech) plugs in behind the same two methods."""
from __future__ import annotations

from typing import Callable, Iterable


class TextChannel:
    """say() records what the agent says. listen() returns the next merchant message.

    replies: scripted merchant messages (used by evals and the demo).
    ask: optional callable for live use, called when the script is exhausted."""

    def __init__(self, replies: Iterable[str] = (), ask: Callable[[], str] | None = None):
        self.replies = list(replies)
        self.ask = ask
        self.transcript: list[tuple[str, str]] = []

    def say(self, text: str) -> None:
        self.transcript.append(("agent", text))

    def listen(self) -> str:
        if self.replies:
            text = self.replies.pop(0)
        elif self.ask:
            text = self.ask()
        else:
            text = ""  # silence
        self.transcript.append(("merchant", text))
        return text
