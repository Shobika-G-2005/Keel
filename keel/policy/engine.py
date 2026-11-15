"""The policy engine: the only dispatcher for tools, the output gate before speech, the consent
capture, the handover router and the audit writer. The model never reaches data or actions any other way."""
from __future__ import annotations

import hashlib
import re
import threading
from datetime import datetime, timedelta
from typing import Callable

from ..db import next_id
from ..tools import data as D
from .audit import AuditWriter
from .envelope import Envelope
from .offer import check_envelope, compute_offer
from .templates import TEMPLATES, fact_numbers, fmt_date, numbers_in, render

REASONS = {"DISTRESS", "DISPUTE", "OUT_OF_ENVELOPE", "LOW_CONFIDENCE", "POLICY_BLOCK"}
MAX_BLOCKS_PER_CALL = 3

DISTRESS_KW = [
    "can't pay", "cannot pay", "can not pay", "unable to pay", "no money", "closing the shop", "shop is closing",
    "close the shop", "closed the shop", "shutting down", "suicide", "kill myself",
    "கட்ட முடியாது", "கடையை மூட", "கடை மூட", "பணம் இல்லை", "தற்கொலை",
    "katta mudiyathu", "kadai moodu", "kadaiya moodu", "panam illai",
]
DISPUTE_KW = [
    "wrong amount", "dispute", "i did not take", "i didn't take", "not my loan", "overcharged", "you are cheating",
    "தவறான தொகை", "நான் வாங்கவில்லை", "ஏமாற்று", "thappu", "nan vangala",
]
AFFIRM = {"yes", "yeah", "yep", "ok", "okay", "sure", "haan", "ha", "aam", "aamam", "amam", "seri", "sari", "agree",
          "aama", "aamanga", "seringa", "okay", "ஆம்", "ஆமாம்", "ஆமா", "ஆமாங்க", "ஆமாம்ங்க", "சரி", "சரிங்க", "சரிங்கய்யா",
          "ஓகே", "ஒகே", "சம்மதம்", "ஒப்புக்கொள்கிறேன்", "ஒத்துக்கொள்கிறேன்", "ஒத்துக்கிறேன்", "ok.", "👍"}
FILLER = {"sir", "madam", "da", "pa", "ma", "please", "thanks", "thank", "you", "i", "do", "fine", "go", "ahead",
          "ஐயா", "அம்மா", "நன்றி", "தம்பி", "ங்க", "பா", "மா", "டா"}
NEGATE = {"no", "nope", "not", "don't", "dont", "never", "illai", "illa", "venda", "vendam", "vena", "venam",
          "வேண்டாம்", "வேண்டாங்க", "வேணாம்", "வேணாங்க", "இல்லை", "இல்ல", "இல்லைங்க", "இல்லீங்க", "இல்லங்க"}


class PolicyBlock(Exception):
    def __init__(self, rule_id: str, reason: str):
        super().__init__(reason)
        self.rule_id = rule_id
        self.reason = reason


def match_yes(text: str) -> str:
    """Deterministic confirmation: 'yes', 'no' or 'ambiguous'. The model never decides this."""
    norm = text.lower().replace("’", "'")
    toks = [t for t in re.split(r"[\s,.!?;:]+", norm) if t]
    if not toks:
        return "ambiguous"
    if any(t in NEGATE for t in toks):
        return "no"
    if any(t in AFFIRM for t in toks) and all(t in AFFIRM or t in FILLER for t in toks):
        return "yes"
    return "ambiguous"


class Engine:
    def __init__(self, con, envelope: Envelope, clock: Callable[[], datetime]):
        self.con = con
        self.env = envelope
        self.clock = clock
        self.audit = AuditWriter(con, clock)
        self.lock = threading.RLock()
        self.channels: dict[str, object] = {}
        self.facts: dict[str, set[int]] = {}
        self.blocks: dict[str, int] = {}
        self.closed: set[str] = set()
        self.attempts: dict[str, int] = {}
        self.transcripts: dict[str, list[tuple[str, str]]] = {}
        self.tools: dict[str, Callable] = {
            "verify_identity": self._t_verify_identity,
            "get_settlements": self._t_get_settlements,
            "get_schedule": self._t_get_schedule,
            "propose_relief": self._t_propose_relief,
            "request_confirmation": self._t_request_confirmation,
            "apply_schedule": self._t_apply_schedule,
            "raise_handover": self._t_raise_handover,
            "speak": self._t_speak,
            "listen": self._t_listen,
            "finish_call": self._t_finish_call,
        }
        # R6: there is deliberately no tool that rejects, cancels or reduces a loan.

    # ---------- helpers ----------
    def today(self):
        return self.clock().date()

    def _call(self, call_id: str):
        return self.con.execute("SELECT * FROM call WHERE call_id=?", (call_id,)).fetchone()

    def _terms(self, merchant_id: str):
        m = D.merchant(self.con, merchant_id)
        return [(m["name"], "name"), (m["phone"], "phone"), (m["phone"][-4:], "digits")]

    def _log(self, actor, action, *, loan_id, merchant_id, call_id=None, inputs=None, result=None, rule_id=None):
        return self.audit.write(actor=actor, action=action, loan_id=loan_id, merchant_id=merchant_id, call_id=call_id,
                                inputs=inputs, result=result, rule_id=rule_id, terms=self._terms(merchant_id))

    def _log_call(self, call, actor, action, inputs=None, result=None, rule_id=None):
        return self._log(actor, action, loan_id=call["loan_id"], merchant_id=call["merchant_id"],
                         call_id=call["call_id"], inputs=inputs, result=result, rule_id=rule_id)

    def is_closed(self, call_id: str) -> bool:
        return call_id in self.closed

    # ---------- dialer ----------
    def start_call(self, loan_id: str, signal_id: str | None, channel) -> str | None:
        """The dialer asks permission here. Calls outside the calling window are refused and logged (R1)."""
        loan = D.loan(self.con, loan_id)
        m = D.merchant(self.con, loan["merchant_id"])
        now = self.clock()
        if not self.env.in_window(now.time()):
            self._log("policy_engine", "call_refused", loan_id=loan_id, merchant_id=m["merchant_id"],
                      inputs={"time": now.strftime("%H:%M")}, result={"allowed": False}, rule_id="R1")
            return None
        call_id = next_id(self.con, "call", "call_id", "C")
        self.con.execute(
            "INSERT INTO call(call_id,merchant_id,loan_id,signal_id,started_at,language) VALUES (?,?,?,?,?,?)",
            (call_id, m["merchant_id"], loan_id, signal_id, now.isoformat(timespec="seconds"), m["language"]),
        )
        self.channels[call_id] = channel
        self.facts[call_id] = set()
        self.blocks[call_id] = 0
        self.transcripts[call_id] = []
        self._log("policy_engine", "call_started", loan_id=loan_id, merchant_id=m["merchant_id"], call_id=call_id,
                  inputs={"signal_id": signal_id}, result={"allowed": True})
        return call_id

    def end_call(self, call_id: str, outcome: str | None = None) -> dict:
        with self.lock:
            call = self._call(call_id)
            if call_id not in self.closed:
                outcome = outcome or call["outcome"] or "no_answer"
                autonomous = 1 if (outcome == "resolved" and call["escalation_reason"] is None) else 0
                self.con.execute("UPDATE call SET outcome=?, autonomous=? WHERE call_id=?", (outcome, autonomous, call_id))
                self.closed.add(call_id)
                self._log_call(call, "policy_engine", "call_ended", result={"outcome": outcome, "autonomous": bool(autonomous)})
        return dict(self._call(call_id))

    # ---------- the single dispatcher ----------
    def call_tool(self, call_id: str, name: str, args: dict | None = None) -> dict:
        args = dict(args or {})
        with self.lock:
            call = self._call(call_id)
            if call_id in self.closed:
                return {"blocked": True, "rule_id": "CALL_CLOSED", "reason": "the call has ended"}
            if name not in self.tools:
                return self._blocked(call, name, args, "R6", f"no tool named '{name}'; the agent cannot make adverse credit decisions")
            try:
                result = self.tools[name](call, **args)
            except PolicyBlock as b:
                return self._blocked(call, name, args, b.rule_id, b.reason)
            except TypeError as e:
                return self._blocked(call, name, args, "ARGS", f"bad arguments: {e}")
            self.facts[call_id] |= fact_numbers(result)
            self._log_call(call, "agent" if name != "request_confirmation" else "policy_engine", "tool_call",
                           inputs={"tool": name, "args": args}, result=result)
            return result

    def _blocked(self, call, name, args, rule_id, reason) -> dict:
        self._log_call(call, "policy_engine", "policy_block", inputs={"tool": name, "args": args},
                       result={"reason": reason}, rule_id=rule_id)
        out = {"blocked": True, "rule_id": rule_id, "reason": reason}
        cid = call["call_id"]
        if cid not in self.closed:
            self.blocks[cid] = self.blocks.get(cid, 0) + 1
            if self.blocks[cid] >= MAX_BLOCKS_PER_CALL:
                self._handover(self._call(cid), "POLICY_BLOCK", "policy_engine")
                out["escalated"] = True
        return out

    # ---------- merchant utterances: deterministic backstop ----------
    def observe(self, call_id: str, text: str) -> str | None:
        """Called for every merchant message. Escalates on distress or dispute keywords even if the model misses them."""
        with self.lock:
            if call_id in self.closed:
                return None
            call = self._call(call_id)
            self.transcripts[call_id].append(("merchant", text))
            self._log_call(call, "merchant", "utterance", inputs={"text": text})
            low = text.lower().replace("’", "'")
            for kw in DISTRESS_KW:
                if kw in low:
                    self._handover(call, "DISTRESS", "policy_engine")
                    return "DISTRESS"
            for kw in DISPUTE_KW:
                if kw in low:
                    self._handover(call, "DISPUTE", "policy_engine")
                    return "DISPUTE"
        return None

    # ---------- tools ----------
    def _require_identity(self, call):
        if not call["identity_verified"]:
            raise PolicyBlock("R9", "identity is not verified; no loan details may be read or spoken")

    def _own_loan(self, call, loan_id):
        if loan_id is not None and loan_id != call["loan_id"]:
            raise PolicyBlock("R9", "this call is only authorised for its own loan")
        return call["loan_id"]

    def _t_verify_identity(self, call, last4: str):
        cid = call["call_id"]
        m = D.merchant(self.con, call["merchant_id"])
        ok = str(last4).strip() == m["phone"][-4:]
        if ok:
            self.con.execute("UPDATE call SET identity_verified=1 WHERE call_id=?", (cid,))
            return {"verified": True}
        self.attempts[cid] = self.attempts.get(cid, 0) + 1
        if self.attempts[cid] >= 2:
            self._speak(call, "id_failed", {})
            self.con.execute("UPDATE call SET outcome='identity_failed', autonomous=0 WHERE call_id=?", (cid,))
            self.closed.add(cid)
            self._log_call(call, "policy_engine", "identity_failed", result={"attempts": self.attempts[cid]}, rule_id="R9")
            return {"verified": False, "attempts_left": 0, "call_closed": True}
        return {"verified": False, "attempts_left": 1}

    def _t_get_settlements(self, call, from_date: str, to_date: str, loan_id: str | None = None):
        self._require_identity(call)
        lid = self._own_loan(call, loan_id)
        to_date = min(to_date, self.today().isoformat())  # no reading the future
        return {"settlements": D.settlements(self.con, lid, from_date, to_date)}

    def _t_get_schedule(self, call, loan_id: str | None = None, on_date: str | None = None):
        self._require_identity(call)
        lid = self._own_loan(call, loan_id)
        on = D.d(on_date) if on_date else self.today()
        return D.schedule_info(self.con, lid, on)

    def _t_propose_relief(self, call, signal_id: str | None = None, requested_daily_amount_rupees: int | None = None,
                          requested_relief_days: int | None = None):
        self._require_identity(call)
        if signal_id is not None and signal_id != call["signal_id"]:
            raise PolicyBlock("R9", "this call is only authorised for its own stress signal")
        if not call["signal_id"]:
            raise PolicyBlock("R10", "there is no stress signal for this call")
        lid = call["loan_id"]
        tomorrow = self.today() + timedelta(days=1)
        rows = D.schedule_rows(self.con, lid)
        current = D.daily_on(rows, tomorrow)
        balance = D.remaining(self.con, lid)
        o = compute_offer(current, self.env, requested_daily_amount_rupees, requested_relief_days)
        r = o["relief_days"]
        top = max(x["version"] for x in rows)
        hypo = rows + [
            {"version": top + 1, "daily_amount_rupees": o["new_daily_amount_rupees"], "starts_on": tomorrow.isoformat(),
             "ends_on": (tomorrow + timedelta(days=max(r, 1) - 1)).isoformat()},
            {"version": top + 2, "daily_amount_rupees": current, "starts_on": (tomorrow + timedelta(days=max(r, 1))).isoformat(),
             "ends_on": None},
        ]
        old_end = D.project_end(rows, balance, tomorrow)
        new_end = D.project_end(hypo, balance, tomorrow)
        o["extension_days"] = (new_end - old_end).days
        o["old_end_date"] = old_end.isoformat()
        o["new_end_date"] = new_end.isoformat()
        o["starts_on"] = tomorrow.isoformat()
        breaches = check_envelope(o, self.env)
        if breaches:
            rule, reason = breaches[0]
            raise PolicyBlock(rule, reason)
        offer_id = next_id(self.con, "offer", "offer_id", "O")
        self.con.execute(
            "INSERT INTO offer(offer_id,signal_id,call_id,envelope_id,current_daily_amount_rupees,new_daily_amount_rupees,"
            "relief_days,deferred_rupees,extension_days,old_end_date,new_end_date,starts_on,within_envelope)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1)",
            (offer_id, call["signal_id"], call["call_id"], self.env.envelope_id, o["current_daily_amount_rupees"],
             o["new_daily_amount_rupees"], o["relief_days"], o["deferred_rupees"], o["extension_days"],
             o["old_end_date"], o["new_end_date"], o["starts_on"]),
        )
        return {"offer_id": offer_id, "within_envelope": True, **o}

    def _offer(self, call, offer_id):
        o = self.con.execute("SELECT * FROM offer WHERE offer_id=?", (offer_id,)).fetchone()
        if not o or o["call_id"] != call["call_id"]:
            raise PolicyBlock("R9", "unknown offer for this call")
        return o

    def _t_request_confirmation(self, call, offer_id: str):
        self._require_identity(call)
        o = self._offer(call, offer_id)
        if o["status"] != "proposed" or not o["within_envelope"]:
            raise PolicyBlock("R2", "this offer cannot be confirmed in its current state")
        cid = call["call_id"]
        ch = self.channels[cid]
        for attempt, tid in enumerate(("readback", "readback_again")):
            text = self._speak(call, tid, {}, offer=o)
            reply = ch.listen()
            if self.observe(cid, reply):  # distress or dispute while confirming
                return {"confirmed": False, "reason": "escalated"}
            verdict = match_yes(reply)
            if verdict == "yes":
                consent_id = next_id(self.con, "consent", "consent_id", "K")
                self.con.execute(
                    "INSERT INTO consent(consent_id,merchant_id,offer_id,text_hash,granted_at,transcript_span) VALUES (?,?,?,?,?,?)",
                    (consent_id, call["merchant_id"], offer_id, hashlib.sha256(text.encode("utf-8")).hexdigest(),
                     self.clock().isoformat(timespec="seconds"), reply),
                )
                self._log_call(call, "policy_engine", "consent", inputs={"offer_id": offer_id}, result={"consent_id": consent_id})
                return {"confirmed": True, "reason": "yes", "consent_id": consent_id}
            if verdict == "no":
                self.con.execute("UPDATE offer SET status='declined' WHERE offer_id=?", (offer_id,))
                self.con.execute("UPDATE call SET outcome='declined' WHERE call_id=?", (cid,))
                return {"confirmed": False, "reason": "declined"}
            if numbers_in(reply):
                # A reply that is not a yes but names a figure is a counter-request. The engine cannot negotiate terms.
                self._handover(self._call(cid), "OUT_OF_ENVELOPE", "policy_engine")
                return {"confirmed": False, "reason": "escalated"}
        self._handover(self._call(cid), "LOW_CONFIDENCE", "policy_engine")
        return {"confirmed": False, "reason": "escalated"}

    def _t_apply_schedule(self, call, offer_id: str):
        self._require_identity(call)
        o = self._offer(call, offer_id)
        if not o["within_envelope"]:
            raise PolicyBlock("R3", "the offer is outside the lender envelope")
        if self.env.requires_consent:
            c = self.con.execute("SELECT * FROM consent WHERE offer_id=? AND revoked_at IS NULL", (offer_id,)).fetchone()
            if not c:
                raise PolicyBlock("R2", "no consent on record for this offer")
        if o["status"] != "proposed":
            raise PolicyBlock("DUPLICATE", f"the offer is already {o['status']}")
        lid = call["loan_id"]
        start = D.d(o["starts_on"])
        relief_end = start + timedelta(days=o["relief_days"] - 1)
        resume = relief_end + timedelta(days=1)
        top = self.con.execute("SELECT MAX(version) FROM schedule_version WHERE loan_id=?", (lid,)).fetchone()[0]
        self.con.execute("BEGIN IMMEDIATE")
        try:
            self.con.execute(
                "INSERT INTO schedule_version(loan_id,version,kind,daily_amount_rupees,starts_on,ends_on,offer_id,created_by)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (lid, top + 1, "relief", o["new_daily_amount_rupees"], start.isoformat(), relief_end.isoformat(), offer_id, "policy_engine"))
            self.con.execute(
                "INSERT INTO schedule_version(loan_id,version,kind,daily_amount_rupees,starts_on,ends_on,offer_id,created_by)"
                " VALUES (?,?,?,?,?,?,NULL,?)",
                (lid, top + 2, "resume", o["current_daily_amount_rupees"], resume.isoformat(), None, "policy_engine"))
            self.con.execute("UPDATE offer SET status='accepted' WHERE offer_id=?", (offer_id,))
            self.con.execute("UPDATE loan SET status='relief' WHERE loan_id=?", (lid,))
            self.con.execute("UPDATE call SET outcome='resolved' WHERE call_id=?", (call["call_id"],))
            self.con.execute("COMMIT")
        except Exception as e:
            self.con.execute("ROLLBACK")
            raise PolicyBlock("DUPLICATE", f"could not apply the offer: {e}")
        return {"applied": True, "offer_id": offer_id, "schedule": D.schedule_rows(self.con, lid),
                "new_end_date": o["new_end_date"]}

    def _t_raise_handover(self, call, reason_code: str):
        if reason_code not in REASONS:
            raise PolicyBlock("ARGS", f"reason_code must be one of {sorted(REASONS)}")
        return self._handover(call, reason_code, "agent")

    # ---------- output gate ----------
    def _values(self, call, offer=None) -> dict:
        m = D.merchant(self.con, call["merchant_id"])
        v = {"name": m["name"]}
        if offer is None:
            offer = self.con.execute("SELECT * FROM offer WHERE call_id=? ORDER BY offer_id DESC LIMIT 1", (call["call_id"],)).fetchone()
        if offer is not None:
            for k in ("new_daily_amount_rupees", "relief_days", "deferred_rupees", "extension_days"):
                v[k] = offer[k]
            v["new_end_date"] = fmt_date(offer["new_end_date"])
            v["old_end_date"] = fmt_date(offer["old_end_date"])
        return v

    def _speak(self, call, template_id: str, params: dict, offer=None) -> str:
        if template_id not in TEMPLATES:
            raise PolicyBlock("R8", f"unknown template '{template_id}'")
        discloses = TEMPLATES[template_id][0]
        if discloses:
            self._require_identity(self._call(call["call_id"]))
        values = self._values(call, offer)
        values.update(params or {})
        _, text = render(template_id, call["language"], values)
        facts = self.facts[call["call_id"]]
        if offer is not None:
            facts = facts | fact_numbers(dict(offer))
        else:
            latest = self.con.execute("SELECT * FROM offer WHERE call_id=? ORDER BY offer_id DESC LIMIT 1", (call["call_id"],)).fetchone()
            if latest is not None:
                facts = facts | fact_numbers(dict(latest))
        if template_id == "greet_verify":
            facts = facts | {0}
        bad = [n for n in numbers_in(text) if n not in facts]
        if bad:
            self._log_call(call, "policy_engine", "speech_blocked", inputs={"template_id": template_id, "text": text},
                           result={"unmatched_figures": bad}, rule_id="R8")
            self._handover(self._call(call["call_id"]), "POLICY_BLOCK", "policy_engine")
            raise PolicyBlock("R8", f"figure(s) {bad} do not match tool output; the sentence was blocked and the call escalated")
        self.channels[call["call_id"]].say(text)
        self.transcripts[call["call_id"]].append(("agent", text))
        self._log_call(call, "agent", "speech", inputs={"template_id": template_id}, result={"text": text})
        return text

    def _t_speak(self, call, template_id: str, params: dict | None = None):
        self._speak(call, template_id, params or {})
        return {"spoken": True}

    def _t_listen(self, call):
        """Wait for the merchant's next message. It passes through the distress and dispute backstop."""
        text = self.channels[call["call_id"]].listen()
        reason = self.observe(call["call_id"], text)
        out = {"merchant_said": text}
        if not text.strip():
            out["silence"] = True
        if reason:
            out["escalated"] = reason
        return out

    def _t_finish_call(self, call):
        done = self.end_call(call["call_id"])
        return {"finished": True, "outcome": done["outcome"]}

    # ---------- escalation ----------
    def _handover(self, call, reason: str, actor: str) -> dict:
        cid = call["call_id"]
        if cid in self.closed:
            return {"case_id": None, "already_closed": True}
        offer = self.con.execute("SELECT * FROM offer WHERE call_id=? ORDER BY offer_id DESC LIMIT 1", (cid,)).fetchone()
        if offer is not None and offer["status"] == "proposed":
            self.con.execute("UPDATE offer SET status='escalated' WHERE offer_id=?", (offer["offer_id"],))
        last = next((t for who, t in reversed(self.transcripts.get(cid, [])) if who == "merchant"), "")
        summary = (
            f"Escalated ({reason}). Identity {'verified' if self._call(cid)['identity_verified'] else 'not verified'}. "
            + (f"Offer {offer['offer_id']}: Rs {offer['new_daily_amount_rupees']} a day for {offer['relief_days']} days, status {offer['status']}. "
               if offer is not None else "No offer made. ")
            + f"Last merchant message: \"{last[:120]}\". See audit trail for call {cid}."
        )
        case_id = next_id(self.con, "handover_case", "case_id", "H")
        self.con.execute(
            "INSERT INTO handover_case(case_id,call_id,loan_id,reason,summary,created_at) VALUES (?,?,?,?,?,?)",
            (case_id, cid, call["loan_id"], reason, summary, self.clock().isoformat(timespec="seconds")))
        self.con.execute("UPDATE call SET outcome='escalated', autonomous=0, escalation_reason=?, handover_summary=? WHERE call_id=?",
                         (reason, summary, cid))
        self._log_call(call, actor, "escalation", inputs={"reason": reason}, result={"case_id": case_id, "summary": summary})
        text = render("handover", call["language"], {})[1]
        self.channels[cid].say(text)
        self.transcripts[cid].append(("agent", text))
        self.closed.add(cid)
        return {"case_id": case_id, "escalated": True, "reason": reason}
