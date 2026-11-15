"""Append-only, hash-chained audit log. Redaction happens here, before the row is stored,
because rows cannot be changed afterwards (SQLite triggers abort UPDATE and DELETE)."""
from __future__ import annotations

import hashlib
import json
import re
import threading
from typing import Any, Callable, Iterable

GENESIS = "0" * 64
REDACT_KEYS = {"phone", "name", "last4", "merchant_name"}
PHONE_RE = re.compile(r"\b\d{10}\b")


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def redact(obj: Any, terms: Iterable[tuple[str, str]] = ()) -> Any:
    """terms: (needle, label) pairs, for example (merchant name, 'name')."""
    if isinstance(obj, dict):
        return {k: ("[redacted]" if k in REDACT_KEYS else redact(v, terms)) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [redact(v, terms) for v in obj]
    if isinstance(obj, str):
        out = PHONE_RE.sub("[phone]", obj)
        for needle, label in terms:
            if needle:
                out = re.sub(re.escape(needle), f"[{label}]", out, flags=re.IGNORECASE)
        return out
    return obj


def compute_hash(seq, ts, call_id, loan_id, merchant_id, actor, action, inputs, result, rule_id, prev_hash) -> str:
    payload = canonical([seq, ts, call_id, loan_id, merchant_id, actor, action, inputs, result, rule_id, prev_hash])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AuditWriter:
    def __init__(self, con, clock: Callable):
        self.con = con
        self.clock = clock
        self.lock = threading.RLock()

    def write(self, *, actor: str, action: str, loan_id: str, merchant_id: str, call_id: str | None = None,
              inputs: Any = None, result: Any = None, rule_id: str | None = None,
              terms: Iterable[tuple[str, str]] = ()) -> int:
        inputs_s = canonical(redact(inputs if inputs is not None else {}, terms))
        result_s = canonical(redact(result if result is not None else {}, terms))
        with self.lock:
            self.con.execute("BEGIN IMMEDIATE")
            try:
                last = self.con.execute("SELECT seq, hash FROM audit_event ORDER BY seq DESC LIMIT 1").fetchone()
                seq = last["seq"] + 1 if last else 1
                prev = last["hash"] if last else GENESIS
                ts = self.clock().isoformat(timespec="seconds")
                h = compute_hash(seq, ts, call_id, loan_id, merchant_id, actor, action, inputs_s, result_s, rule_id, prev)
                self.con.execute(
                    "INSERT INTO audit_event(seq,timestamp,call_id,loan_id,merchant_id,actor,action,inputs,result,rule_id,prev_hash,hash)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (seq, ts, call_id, loan_id, merchant_id, actor, action, inputs_s, result_s, rule_id, prev, h),
                )
                self.con.execute("COMMIT")
            except Exception:
                self.con.execute("ROLLBACK")
                raise
        return seq


def verify_chain(con) -> dict:
    """Recompute the hash chain. Returns ok, row count and the first broken seq with the reason."""
    prev = GENESIS
    expected_seq = 1
    n = 0
    for r in con.execute("SELECT * FROM audit_event ORDER BY seq"):
        n += 1
        if r["seq"] != expected_seq:
            return {"ok": False, "rows": n, "first_bad_seq": r["seq"], "reason": "sequence gap"}
        if r["prev_hash"] != prev:
            return {"ok": False, "rows": n, "first_bad_seq": r["seq"], "reason": "prev_hash mismatch"}
        h = compute_hash(r["seq"], r["timestamp"], r["call_id"], r["loan_id"], r["merchant_id"], r["actor"],
                         r["action"], r["inputs"], r["result"], r["rule_id"], r["prev_hash"])
        if h != r["hash"]:
            return {"ok": False, "rows": n, "first_bad_seq": r["seq"], "reason": "hash mismatch"}
        prev = r["hash"]
        expected_seq += 1
    return {"ok": True, "rows": n, "first_bad_seq": None, "reason": None}
