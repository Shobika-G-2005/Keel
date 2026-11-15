"""Stress detector. Applies the lender envelope's rule to settlements and writes a StressSignal."""
from __future__ import annotations

import json
from datetime import date, timedelta

from ..db import next_id
from ..tools import data as D


def _relief_active(con, loan_id: str, on: date) -> bool:
    for r in D.schedule_rows(con, loan_id):
        if r["kind"] == "relief" and on <= D.d(r["ends_on"]):  # in force now, or agreed and starting tomorrow
            return True
    return False


def detect(engine, loan_id: str, as_of: date | None = None) -> str | None:
    """Return a new signal_id if the stress rule fires, else None."""
    con, env = engine.con, engine.env
    as_of = as_of or engine.today()
    loan = D.loan(con, loan_id)
    m = D.merchant(con, loan["merchant_id"])
    normal = m["normal_daily_settlement_rupees"]

    def log(action, result, rule_id=None, inputs=None):
        engine._log("detector", action, loan_id=loan_id, merchant_id=m["merchant_id"], inputs=inputs or {"as_of": as_of.isoformat()},
                    result=result, rule_id=rule_id)

    if _relief_active(con, loan_id, as_of):
        log("detector_skipped", {"reason": "relief schedule is active"}, rule_id="R10")
        return None

    rows = D.settlements(con, loan_id, "0000-01-01", as_of.isoformat())
    run = []  # trailing run of consecutive low days
    for r in reversed(rows):
        low = r["settlement_rupees"] * 100 < env.stress_threshold_pct * normal
        contiguous = not run or D.d(r["date"]) == D.d(run[-1]["date"]) - timedelta(days=1)
        if low and contiguous:
            run.append({"date": r["date"], "pct_tenths": r["settlement_rupees"] * 1000 // normal})
        else:
            break
    run.reverse()
    if len(run) < env.stress_consecutive_days:
        log("detector_checked", {"signal": False, "low_days_in_a_row": len(run)})
        return None
    prior = con.execute("SELECT 1 FROM stress_signal WHERE loan_id=? AND detected_on>=?", (loan_id, run[0]["date"])).fetchone()
    if prior:
        log("detector_checked", {"signal": False, "reason": "signal already raised for this low run"})
        return None
    signal_id = next_id(con, "stress_signal", "signal_id", "S")
    con.execute(
        "INSERT INTO stress_signal(signal_id,loan_id,detected_on,low_days,normal_daily_settlement_rupees,envelope_id) VALUES (?,?,?,?,?,?)",
        (signal_id, loan_id, as_of.isoformat(), json.dumps(run), normal, env.envelope_id))
    log("stress_signal", {"signal_id": signal_id, "low_days": run, "normal_daily_settlement_rupees": normal,
                          "envelope_id": env.envelope_id})
    return signal_id
