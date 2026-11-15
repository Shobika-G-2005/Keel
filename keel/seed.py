"""Synthetic data only. The hero merchant matches the worked example in the PRD and TRD."""
from __future__ import annotations

from datetime import date, timedelta

HERO_SETTLEMENTS = [4000, 3800, 3300, 2900, 2500, 2400, 2400]
START = date(2026, 11, 1)


def add_merchant(con, *, merchant_id="M1", loan_id="L1", name="Murugan", trade="Tea stall", city="T. Nagar, Chennai",
                 phone="9000012345", normal=4000, principal=200000, daily=500, settlements=None, collected_days=5,
                 start: date = START, language="ta"):
    settlements = HERO_SETTLEMENTS if settlements is None else settlements
    con.execute("INSERT INTO merchant VALUES (?,?,?,?,?,?,?)", (merchant_id, name, trade, city, language, phone, normal))
    con.execute("INSERT INTO loan(loan_id,merchant_id,principal_rupees) VALUES (?,?,?)", (loan_id, merchant_id, principal))
    con.execute(
        "INSERT INTO schedule_version(loan_id,version,kind,daily_amount_rupees,starts_on,ends_on,offer_id,created_by)"
        " VALUES (?,?,?,?,?,NULL,NULL,?)", (loan_id, 1, "original", daily, start.isoformat(), "seed"))
    for i, s in enumerate(settlements):
        day = (start + timedelta(days=i)).isoformat()
        con.execute("INSERT INTO settlement_day VALUES (?,?,?,?)", (loan_id, merchant_id, day, s))
        if i < collected_days:
            con.execute("INSERT INTO ledger_entry(loan_id,date,amount_rupees,kind) VALUES (?,?,?,'scheduled')",
                        (loan_id, day, daily))


def seed_hero(con):
    add_merchant(con)
