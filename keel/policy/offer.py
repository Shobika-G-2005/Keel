"""Offer maths. Deterministic, integer rupees only. The model never calls this directly."""
from __future__ import annotations

from .envelope import Envelope


def compute_offer(current_daily: int, env: Envelope, requested_daily: int | None = None,
                  requested_days: int | None = None) -> dict:
    new_daily = env.min_daily_amount_rupees if requested_daily is None else int(requested_daily)
    days = env.max_relief_days if requested_days is None else int(requested_days)
    deferred = max(current_daily - new_daily, 0) * days
    return {
        "current_daily_amount_rupees": current_daily,
        "new_daily_amount_rupees": new_daily,
        "relief_days": days,
        "deferred_rupees": deferred,
    }


def check_envelope(offer: dict, env: Envelope) -> list[tuple[str, str]]:
    """Return (rule_id, reason) for each breach. Empty list means within the envelope."""
    out = []
    if offer["new_daily_amount_rupees"] < env.min_daily_amount_rupees:
        out.append(("R3", f"daily amount {offer['new_daily_amount_rupees']} is below the lender minimum {env.min_daily_amount_rupees}"))
    if offer["relief_days"] > env.max_relief_days or offer["relief_days"] < 1:
        out.append(("R4", f"relief of {offer['relief_days']} days is outside the lender limit of {env.max_relief_days}"))
    if offer.get("extension_days", 0) > env.max_extension_days:
        out.append(("R5", f"extension of {offer['extension_days']} days is above the lender limit of {env.max_extension_days}"))
    if offer["new_daily_amount_rupees"] >= offer["current_daily_amount_rupees"]:
        out.append(("R3", "the new amount does not reduce the current daily amount"))
    return out
