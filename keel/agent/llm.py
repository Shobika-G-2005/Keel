"""Model clients. Sarvam exposes an OpenAI-compatible chat API with tool calling.
The secret is read through keel.config and is never printed or logged."""
from __future__ import annotations

import json
import time
from typing import Protocol

import httpx

from .. import config

SARVAM_URL = "https://api.sarvam.ai/v2/chat/completions"
MAX_ATTEMPTS = 5


class LLMError(Exception):
    """The model or network failed. The caller falls back or escalates."""


class LLMClient(Protocol):
    def chat(self, messages: list[dict], tools: list[dict]) -> dict:
        """Return {'content': str, 'tool_calls': [{'id','name','arguments': dict}], 'finish_reason': str}."""


class SarvamClient:
    def __init__(self, model: str | None = None, timeout: float = 40.0, max_tokens: int = 3000):
        self.key = config.get("SARVAM_API_KEY")
        if not self.key:
            raise LLMError("SARVAM_API_KEY is not set")
        self.model = model or config.get("KEEL_SARVAM_MODEL", "sarvam-105b")
        self.timeout = timeout
        self.max_tokens = max_tokens

    def chat(self, messages: list[dict], tools: list[dict]) -> dict:
        body = {"model": self.model, "messages": messages, "tools": tools, "tool_choice": "auto",
                "max_tokens": self.max_tokens, "temperature": 0.2}
        data = None
        for attempt in range(MAX_ATTEMPTS):
            last = attempt == MAX_ATTEMPTS - 1
            try:
                r = httpx.post(SARVAM_URL, json=body, headers={"api-subscription-key": self.key}, timeout=self.timeout)
            except httpx.HTTPError as e:
                if last:
                    raise LLMError(f"network error: {type(e).__name__}") from None
                time.sleep(1 + attempt)
                continue
            if r.status_code == 400 and "temperature" in r.text and "temperature" in body:
                body.pop("temperature")  # some models reject it; retry without
                continue
            if r.status_code in (429, 500, 502, 503, 504) and not last:
                # rate limited or a server blip: wait (honouring Retry-After) and try again
                try:
                    wait = float(r.headers.get("retry-after", ""))
                except ValueError:
                    wait = min(2 ** attempt * 2, 20)
                time.sleep(min(wait, 30))
                continue
            if r.status_code != 200:
                raise LLMError(f"HTTP {r.status_code}: {r.text[:200].replace(self.key, '[key]')}")
            data = r.json()
            break
        if data is None:
            raise LLMError("no response")
        choice = data["choices"][0]
        msg = choice["message"]
        calls = []
        for tc in msg.get("tool_calls") or []:
            try:
                args = json.loads(tc["function"].get("arguments") or "{}")
                if not isinstance(args, dict):
                    args = {}
            except json.JSONDecodeError:
                args = {"__bad_json__": tc["function"].get("arguments")}
            calls.append({"id": tc["id"], "name": tc["function"]["name"], "arguments": args})
        return {"content": msg.get("content") or "", "tool_calls": calls, "finish_reason": choice.get("finish_reason")}


class FakeClient:
    """Scripted model for tests: each item is a list of (tool_name, arguments) or a plain string."""

    def __init__(self, turns):
        self.turns = list(turns)
        self.seen: list[list[dict]] = []

    def chat(self, messages, tools):
        self.seen.append(list(messages))
        if not self.turns:
            return {"content": "", "tool_calls": [], "finish_reason": "stop"}
        t = self.turns.pop(0)
        if isinstance(t, str):
            return {"content": t, "tool_calls": [], "finish_reason": "stop"}
        return {"content": "", "finish_reason": "tool_calls",
                "tool_calls": [{"id": f"fake-{len(self.seen)}-{i}", "name": n, "arguments": a} for i, (n, a) in enumerate(t)]}


def make_client() -> LLMClient:
    provider = config.get("KEEL_LLM_PROVIDER", "sarvam")
    if provider == "sarvam":
        return SarvamClient()
    raise LLMError(f"provider '{provider}' is not implemented")
