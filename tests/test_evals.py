"""The evaluation must be able to fail. These tests break the engine on purpose and check the run notices."""
from collections import Counter

import yaml

from keel.evals import generate
from keel.evals.runner import load_scenarios, run_all, run_scenario
from keel.policy import engine as engine_mod


def sc(id_):
    return next(s for s in load_scenarios() if s["id"] == id_)


def test_every_category_has_at_least_five_scenarios():
    counts = Counter(s["category"] for s in load_scenarios() if s["category"] != "known_gap")
    assert set(counts) == {"normal", "unclear_or_declined", "angry_borrower", "out_of_hours", "adversarial"}
    assert min(counts.values()) >= 5


def test_scenario_file_matches_generator():
    assert yaml.safe_load(generate.OUT.read_text(encoding="utf-8")) == yaml.safe_load(
        yaml.safe_dump(generate.S, allow_unicode=True, sort_keys=False, width=120))


def test_full_scripted_run_passes_and_reports_three_figures():
    res = run_all("scripted")
    assert res["passed"] == res["total"]
    vb = res["violations_blocked"]
    assert vb["blocked"] == vb["attempted"] and vb["leaked"] == 0
    assert res["number_audit"]["figures_spoken_wrong"] == 0 and res["number_audit"]["pass_rate_pct"] == 100.0
    assert {"DISTRESS", "DISPUTE", "OUT_OF_ENVELOPE", "LOW_CONFIDENCE", "POLICY_BLOCK"} <= set(res["escalations_by_reason"])
    assert res["known_gaps"][0]["reached_the_merchant"] is True  # reported, not hidden


def test_eval_catches_a_broken_identity_check(monkeypatch):
    monkeypatch.setattr(engine_mod.Engine, "_require_identity", lambda self, call: None)
    r = run_scenario(sc("A08"))
    assert not r["passed"]


def test_eval_catches_a_broken_number_gate(monkeypatch):
    monkeypatch.setattr(engine_mod, "numbers_in", lambda text: [])  # the gate sees no figures
    r = run_scenario(sc("A11"))
    assert not r["passed"] and r["figures_spoken_wrong"] > 0


def test_eval_catches_a_missing_consent_check(monkeypatch):
    real = engine_mod.Engine._t_apply_schedule

    def no_consent(self, call, offer_id):
        self.con.execute("INSERT INTO consent(consent_id,merchant_id,offer_id,text_hash,granted_at,transcript_span) "
                         "VALUES ('Kx','M1',?, 'x','x','x')", (offer_id,))
        return real(self, call, offer_id)

    # simulates an engine that forges consent; the schedule changes, so the run must fail on the expected versions
    monkeypatch.setattr(engine_mod.Engine, "_t_apply_schedule", no_consent)
    r = run_scenario(sc("A01"))
    assert not r["passed"] and any("versions" in p for p in r["problems"])
