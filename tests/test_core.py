from datetime import date, datetime, timedelta

import pytest

from keel import db
from keel.agent.scripted import run_call
from keel.demo import Clock, make_engine
from keel.detector import detect
from keel.policy import verify_chain
from keel.policy.audit import GENESIS
from keel.policy.engine import match_yes
from keel.policy.offer import check_envelope, compute_offer
from keel.policy.templates import indian, numbers_in
from keel.seed import add_merchant
from keel.tools import data as D
from keel.voice import TextChannel

DAY5 = date(2026, 11, 5)


def new_call(eng, replies, signal=True):
    sig = detect(eng, "L1") if signal else None
    return eng.start_call("L1", sig, TextChannel(replies)), sig


YES_FLOW = ["2345", "yes"]


# ---------- detector ----------
def test_stress_rule_fires_after_day_5_not_before():
    eng = make_engine()
    assert detect(eng, "L1", date(2026, 11, 3)) is None  # day 3 at 82.5% is not low
    assert detect(eng, "L1", date(2026, 11, 4)) is None  # one low day only
    sig = detect(eng, "L1", DAY5)
    assert sig == "S1"
    row = eng.con.execute("SELECT * FROM stress_signal").fetchone()
    assert row["normal_daily_settlement_rupees"] == 4000 and row["envelope_id"] == "env-1"


def test_flat_week_never_fires():
    eng = make_engine(seed=False)
    add_merchant(eng.con, settlements=[4000, 3900, 4100, 3800, 4000, 3950, 4000])
    for i in range(7):
        assert detect(eng, "L1", date(2026, 11, 1) + timedelta(days=i)) is None


def test_no_second_signal_for_same_low_run():
    eng = make_engine()
    assert detect(eng, "L1", DAY5)
    assert detect(eng, "L1", date(2026, 11, 6)) is None


def test_no_signal_during_active_relief():
    eng = make_engine()
    cid, sig = new_call(eng, YES_FLOW)
    run_call(eng, cid)
    assert detect(eng, "L1", date(2026, 11, 7)) is None
    r = eng.con.execute("SELECT rule_id FROM audit_event WHERE actor='detector' ORDER BY seq DESC LIMIT 1").fetchone()
    assert r["rule_id"] == "R10"


# ---------- offer maths ----------
def test_offer_maths_reference_case():
    eng = make_engine()
    cid, sig = new_call(eng, ["2345"])
    eng.call_tool(cid, "verify_identity", {"last4": "2345"})
    o = eng.call_tool(cid, "propose_relief", {})
    assert o["new_daily_amount_rupees"] == 300 and o["relief_days"] == 14
    assert o["deferred_rupees"] == 2800 and o["extension_days"] == 6
    assert D.d(o["new_end_date"]) - D.d(o["old_end_date"]) == timedelta(days=6)


def test_request_below_minimum_is_blocked_with_rule():
    eng = make_engine()
    cid, _ = new_call(eng, ["2345"])
    eng.call_tool(cid, "verify_identity", {"last4": "2345"})
    r = eng.call_tool(cid, "propose_relief", {"requested_daily_amount_rupees": 100})
    assert r["blocked"] and r["rule_id"] == "R3"
    r = eng.call_tool(cid, "propose_relief", {"requested_relief_days": 30})
    assert r["blocked"] and r["rule_id"] == "R4"


def test_check_envelope_extension_limit():
    eng = make_engine()
    o = compute_offer(500, eng.env)
    o["extension_days"] = 9
    assert [r for r, _ in check_envelope(o, eng.env)] == ["R5"]


def test_last_instalment_is_min_of_daily_and_remaining():
    rows = [{"version": 1, "daily_amount_rupees": 500, "starts_on": "2026-11-01", "ends_on": None}]
    end = D.project_end(rows, 1200, date(2026, 11, 1))
    assert end == date(2026, 11, 3)  # 500 + 500 + 200
    assert D.project_end(rows, 1000, date(2026, 11, 1)) == date(2026, 11, 2)


# ---------- schedule, consent ----------
def test_golden_path_end_to_end():
    eng = make_engine()
    cid, _ = new_call(eng, YES_FLOW)
    call = run_call(eng, cid)
    assert call["outcome"] == "resolved" and call["autonomous"] == 1 and call["identity_verified"] == 1
    rows = D.schedule_rows(eng.con, "L1")
    assert [(r["version"], r["daily_amount_rupees"], r["starts_on"], r["ends_on"]) for r in rows] == [
        (1, 500, "2026-11-01", None),
        (2, 300, "2026-11-06", "2026-11-19"),
        (3, 500, "2026-11-20", None),
    ]
    info = D.schedule_info(eng.con, "L1", date(2026, 11, 6))
    assert info["daily_amount_rupees"] == 300
    old_end = D.project_end([rows[0]], D.remaining(eng.con, "L1"), date(2026, 11, 6))
    assert D.d(info["ends_on"]) - old_end == timedelta(days=6)
    assert eng.con.execute("SELECT status FROM loan").fetchone()[0] == "relief"
    assert eng.con.execute("SELECT COUNT(*) FROM consent").fetchone()[0] == 1
    assert verify_chain(eng.con)["ok"]


def test_schedule_resolution_by_date_and_total_repaid():
    eng = make_engine()
    cid, _ = new_call(eng, YES_FLOW)
    run_call(eng, cid)
    rows = D.schedule_rows(eng.con, "L1")
    assert D.daily_on(rows, date(2026, 11, 5)) == 500
    assert D.daily_on(rows, date(2026, 11, 6)) == 300
    assert D.daily_on(rows, date(2026, 11, 19)) == 300
    assert D.daily_on(rows, date(2026, 11, 20)) == 500


def test_apply_without_consent_is_refused_r2():
    eng = make_engine()
    cid, _ = new_call(eng, ["2345"])
    eng.call_tool(cid, "verify_identity", {"last4": "2345"})
    o = eng.call_tool(cid, "propose_relief", {})
    r = eng.call_tool(cid, "apply_schedule", {"offer_id": o["offer_id"]})
    assert r["blocked"] and r["rule_id"] == "R2"
    assert len(D.schedule_rows(eng.con, "L1")) == 1


def test_double_apply_is_rejected():
    eng = make_engine()
    cid, _ = new_call(eng, ["yes"])
    eng.call_tool(cid, "verify_identity", {"last4": "2345"})
    o = eng.call_tool(cid, "propose_relief", {})
    assert eng.call_tool(cid, "request_confirmation", {"offer_id": o["offer_id"]})["confirmed"]
    assert eng.call_tool(cid, "apply_schedule", {"offer_id": o["offer_id"]})["applied"]
    again = eng.call_tool(cid, "apply_schedule", {"offer_id": o["offer_id"]})
    assert again["blocked"] and len(D.schedule_rows(eng.con, "L1")) == 3


def test_yes_matching():
    assert match_yes("yes") == "yes" and match_yes("ஆம்") == "yes" and match_yes("ok sir") == "yes"
    assert match_yes("no") == "no" and match_yes("வேண்டாம்") == "no"
    assert match_yes("yes but how much") == "ambiguous" and match_yes("") == "ambiguous"
    assert match_yes("maybe") == "ambiguous"


def test_ambiguous_twice_escalates_low_confidence():
    eng = make_engine()
    cid, _ = new_call(eng, ["2345", "hmm what", "umm tell me again"])
    call = run_call(eng, cid)
    assert call["outcome"] == "escalated" and call["escalation_reason"] == "LOW_CONFIDENCE"
    assert len(D.schedule_rows(eng.con, "L1")) == 1


def test_counter_request_during_readback_escalates_out_of_envelope():
    eng = make_engine()
    cid, _ = new_call(eng, ["2345", "I can only pay 100 rupees a day"])
    call = run_call(eng, cid)
    assert call["outcome"] == "escalated" and call["escalation_reason"] == "OUT_OF_ENVELOPE"
    assert len(D.schedule_rows(eng.con, "L1")) == 1


def test_decline_leaves_schedule_unchanged():
    eng = make_engine()
    cid, _ = new_call(eng, ["2345", "no thanks"])
    call = run_call(eng, cid)
    assert call["outcome"] == "declined" and len(D.schedule_rows(eng.con, "L1")) == 1


# ---------- policy engine ----------
def test_no_data_before_identity_r9():
    eng = make_engine()
    cid, _ = new_call(eng, [])
    r = eng.call_tool(cid, "get_schedule", {})
    assert r["blocked"] and r["rule_id"] == "R9"
    r = eng.call_tool(cid, "speak", {"template_id": "situation"})
    assert r["blocked"] and r["rule_id"] == "R9"


def test_identity_failure_ends_call():
    eng = make_engine()
    cid, _ = new_call(eng, ["1111", "2222"])
    call = run_call(eng, cid)
    assert call["outcome"] == "identity_failed" and eng.is_closed(cid)


def test_unknown_tool_blocked_r6():
    eng = make_engine()
    cid, _ = new_call(eng, [])
    r = eng.call_tool(cid, "reject_loan", {"loan_id": "L1"})
    assert r["blocked"] and r["rule_id"] == "R6"


def test_number_audit_blocks_wrong_figure_and_escalates():
    eng = make_engine()
    cid, _ = new_call(eng, ["2345"])
    eng.call_tool(cid, "verify_identity", {"last4": "2345"})
    o = eng.call_tool(cid, "propose_relief", {})
    r = eng.call_tool(cid, "speak", {"template_id": "offer", "params": {"new_daily_amount_rupees": 250}})
    assert r["blocked"] and r["rule_id"] == "R8"
    assert eng.is_closed(cid) and D.d  # call escalated
    assert eng.con.execute("SELECT escalation_reason FROM call").fetchone()[0] == "POLICY_BLOCK"


def test_free_text_figures_are_audited():
    eng = make_engine()
    cid, _ = new_call(eng, ["2345"])
    eng.call_tool(cid, "verify_identity", {"last4": "2345"})
    eng.call_tool(cid, "propose_relief", {})
    ok = eng.call_tool(cid, "speak", {"template_id": "free_text", "params": {"text": "You pay Rs 300 a day."}})
    assert ok == {"spoken": True}
    bad = eng.call_tool(cid, "speak", {"template_id": "free_text", "params": {"text": "We will waive Rs 50,000."}})
    assert bad["blocked"] and bad["rule_id"] == "R8"


def test_indian_grouping():
    assert indian(200000) == "2,00,000" and indian(2800) == "2,800" and indian(300) == "300"
    assert numbers_in("Rs 2,00,000 and 14 days") == [200000, 14]


def test_call_outside_window_refused_r1():
    eng = make_engine(now=datetime(2026, 11, 5, 22, 0))
    sig = detect(eng, "L1")
    assert eng.start_call("L1", sig, TextChannel([])) is None
    r = eng.con.execute("SELECT action, rule_id FROM audit_event ORDER BY seq DESC LIMIT 1").fetchone()
    assert (r["action"], r["rule_id"]) == ("call_refused", "R1")


def test_distress_backstop_escalates():
    eng = make_engine()
    cid, _ = new_call(eng, ["2345", "I cannot pay anything, I am closing the shop"])
    call = run_call(eng, cid)
    assert call["outcome"] == "escalated" and call["escalation_reason"] == "DISTRESS"
    case = eng.con.execute("SELECT * FROM handover_case").fetchone()
    assert case["reason"] == "DISTRESS" and cid in case["summary"]


def test_out_of_envelope_request_escalates_via_tool():
    eng = make_engine()
    cid, _ = new_call(eng, ["2345"])
    eng.call_tool(cid, "verify_identity", {"last4": "2345"})
    blocked = eng.call_tool(cid, "propose_relief", {"requested_daily_amount_rupees": 100})
    assert blocked["blocked"]
    h = eng.call_tool(cid, "raise_handover", {"reason_code": "OUT_OF_ENVELOPE"})
    assert h["escalated"]


def test_three_blocks_escalate_policy_block():
    eng = make_engine()
    cid, _ = new_call(eng, [])
    for _ in range(3):
        eng.call_tool(cid, "waive_loan", {})
    assert eng.con.execute("SELECT escalation_reason FROM call").fetchone()[0] == "POLICY_BLOCK"


def test_cross_loan_access_blocked():
    eng = make_engine()
    cid, _ = new_call(eng, ["2345"])
    eng.call_tool(cid, "verify_identity", {"last4": "2345"})
    r = eng.call_tool(cid, "get_schedule", {"loan_id": "L99"})
    assert r["blocked"] and r["rule_id"] == "R9"


def test_cannot_read_future_settlements():
    eng = make_engine()
    cid, _ = new_call(eng, ["2345"])
    eng.call_tool(cid, "verify_identity", {"last4": "2345"})
    r = eng.call_tool(cid, "get_settlements", {"from_date": "2026-11-01", "to_date": "2026-11-30"})
    assert len(r["settlements"]) == 5


# ---------- audit ----------
def test_audit_chain_append_only_and_tamper_detection(tmp_path):
    path = str(tmp_path / "k.db")
    eng = make_engine(path=path)
    cid, _ = new_call(eng, YES_FLOW)
    run_call(eng, cid)
    v = verify_chain(eng.con)
    assert v["ok"] and v["rows"] > 10
    first = eng.con.execute("SELECT prev_hash FROM audit_event WHERE seq=1").fetchone()[0]
    assert first == GENESIS
    import sqlite3
    with pytest.raises(sqlite3.DatabaseError):
        eng.con.execute("UPDATE audit_event SET result='{}' WHERE seq=3")
    with pytest.raises(sqlite3.DatabaseError):
        eng.con.execute("DELETE FROM audit_event WHERE seq=3")
    # edit outside the app: drop the trigger on a separate connection, change a row, verification names it
    other = db.connect(path)
    other.execute("DROP TRIGGER audit_no_update")
    other.execute("UPDATE audit_event SET result='{\"x\":1}' WHERE seq=4")
    bad = verify_chain(other)
    assert not bad["ok"] and bad["first_bad_seq"] == 4


def test_pii_redacted_in_audit():
    eng = make_engine()
    cid, _ = new_call(eng, YES_FLOW)
    run_call(eng, cid)
    blob = " ".join(f"{r['inputs']} {r['result']}" for r in eng.con.execute("SELECT inputs,result FROM audit_event"))
    assert "Murugan" not in blob and "9000012345" not in blob and "2345" not in blob
