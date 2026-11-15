"""Plain data functions with MCP-shaped signatures. Called only through the policy engine."""
from __future__ import annotations

from datetime import date, timedelta


def d(s: str) -> date:
    return date.fromisoformat(s)


def merchant(con, merchant_id):
    return con.execute("SELECT * FROM merchant WHERE merchant_id=?", (merchant_id,)).fetchone()


def loan(con, loan_id):
    return con.execute("SELECT * FROM loan WHERE loan_id=?", (loan_id,)).fetchone()


def settlements(con, loan_id: str, from_date: str, to_date: str) -> list[dict]:
    rows = con.execute(
        "SELECT date, settlement_rupees FROM settlement_day WHERE loan_id=? AND date>=? AND date<=? ORDER BY date",
        (loan_id, from_date, to_date),
    )
    return [{"date": r["date"], "settlement_rupees": r["settlement_rupees"]} for r in rows]


def schedule_rows(con, loan_id: str) -> list[dict]:
    rows = con.execute("SELECT * FROM schedule_version WHERE loan_id=? ORDER BY version", (loan_id,))
    return [dict(r) for r in rows]


def daily_on(rows: list[dict], on: date) -> int:
    """The schedule for a date is the highest version whose date range covers it. Old rows are never edited."""
    best = None
    for r in rows:
        if d(r["starts_on"]) <= on and (r["ends_on"] is None or on <= d(r["ends_on"])):
            if best is None or r["version"] > best["version"]:
                best = r
    return best["daily_amount_rupees"] if best else 0


def collected(con, loan_id: str) -> int:
    return con.execute("SELECT COALESCE(SUM(amount_rupees),0) FROM ledger_entry WHERE loan_id=?", (loan_id,)).fetchone()[0]


def remaining(con, loan_id: str) -> int:
    """Balance = principal minus everything collected, so it cannot drift."""
    return loan(con, loan_id)["principal_rupees"] - collected(con, loan_id)


def project_end(rows: list[dict], balance: int, start: date) -> date:
    """Walk the schedule forward day by day. The last instalment is min(daily, remaining)."""
    day = start
    end = start - timedelta(days=1)
    for _ in range(20000):
        if balance <= 0:
            return end
        amt = daily_on(rows, day)
        if amt <= 0:
            raise ValueError("schedule has no instalment on " + day.isoformat())
        balance -= min(amt, balance)
        end = day
        day += timedelta(days=1)
    raise ValueError("loan does not end within the projection horizon")


def schedule_info(con, loan_id: str, on_date: date) -> dict:
    rows = schedule_rows(con, loan_id)
    last = con.execute("SELECT MAX(date) FROM ledger_entry WHERE loan_id=?", (loan_id,)).fetchone()[0]
    start = d(last) + timedelta(days=1) if last else d(rows[0]["starts_on"])
    bal = remaining(con, loan_id)
    return {
        "loan_id": loan_id,
        "daily_amount_rupees": daily_on(rows, on_date),
        "remaining_balance_rupees": bal,
        "ends_on": project_end(rows, bal, start).isoformat(),
    }
