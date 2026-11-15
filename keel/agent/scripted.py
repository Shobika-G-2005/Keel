"""Deterministic scripted agent. It is the text-mode golden path with no LLM, and the fallback if the model
or network fails. It calls tools only through the policy engine, like any other agent."""
from __future__ import annotations

import re


def run_call(engine, call_id: str) -> dict:
    ch = engine.channels[call_id]

    def say(template_id, **params):
        return engine.call_tool(call_id, "speak", {"template_id": template_id, "params": params})

    def hear():
        text = ch.listen()
        engine.observe(call_id, text)
        return text

    def done():
        return engine.is_closed(call_id)

    say("greet_verify")
    verified = False
    for _ in range(2):
        reply = hear()
        if done():
            break
        m = re.search(r"\d{4}", reply)
        res = engine.call_tool(call_id, "verify_identity", {"last4": m.group() if m else reply.strip()})
        if res.get("verified"):
            verified = True
            break
        if done():
            break
        say("verify_retry")
    if not verified:
        return engine.end_call(call_id)

    say("situation")
    offer = engine.call_tool(call_id, "propose_relief", {})
    if offer.get("blocked"):
        engine.call_tool(call_id, "raise_handover", {"reason_code": "OUT_OF_ENVELOPE"})
        return engine.end_call(call_id)
    say("offer")
    conf = engine.call_tool(call_id, "request_confirmation", {"offer_id": offer["offer_id"]})
    if conf.get("confirmed"):
        applied = engine.call_tool(call_id, "apply_schedule", {"offer_id": offer["offer_id"]})
        if applied.get("applied"):
            say("applied")
    elif conf.get("reason") == "declined":
        say("declined_ack")
    return engine.end_call(call_id)
