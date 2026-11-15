"""API tests against a temporary database, never the demo one."""
import pytest
from fastapi.testclient import TestClient

import keel.api.app as A


@pytest.fixture()
def client(tmp_path):
    A.DB_PATH = tmp_path / "t.db"
    A.S.build(reset=True)
    yield TestClient(A.app)
    A.S.engine.con.close()


def run(c, persona="agrees", agent="scripted"):
    return c.post("/api/demo/run", json={"persona": persona, "agent": agent}).json()


def test_state_before_any_call(client):
    s = client.get("/api/state").json()
    assert s["loan"]["daily_rupees"] == 500 and s["signals"] == [] and "phone" not in s["merchant"]
    assert len(s["settlements"]) == 5  # only days up to today


def test_golden_run_changes_schedule_and_verifies(client):
    out = run(client)
    assert out["status"] == "ok" and out["outcome"] == "resolved"
    s = client.get("/api/state").json()
    assert s["accepted_offer"]["deferred_rupees"] == 2800 and s["accepted_offer"]["extension_days"] == 6
    assert s["loan"]["ends_on"] != s["loan"]["ends_on_without_relief"]
    assert client.get("/api/audit/verify").json()["ok"]


def test_second_run_blocked_by_r10(client):
    run(client)
    out = run(client)
    assert out["status"] == "no_signal" and out["rule_id"] == "R10"


def test_after_hours_refused_r1(client):
    out = run(client, "after_hours")
    assert out["status"] == "refused" and out["rule_id"] == "R1"


def test_escalations_land_in_queue(client):
    assert run(client, "distress")["outcome"] == "escalated"
    q = client.get("/api/queue").json()
    assert q and q[0]["reason"] == "DISTRESS"


def test_tamper_then_verify_names_the_row(client):
    run(client)
    assert client.post("/api/demo/tamper?seq=3").json()["status"] == "tampered"
    v = client.get("/api/audit/verify").json()
    assert not v["ok"] and v["first_bad_seq"] == 3


def test_llm_agent_without_key_falls_back_to_scripted(client, monkeypatch):
    monkeypatch.setenv("SARVAM_API_KEY", "")
    monkeypatch.setattr("keel.config.load_env", lambda *a, **k: None)
    out = run(client, "agrees", "llm")
    assert out["status"] == "ok" and out["outcome"] == "resolved" and "scripted" in out["agent"]


def test_reset_clears_everything(client):
    run(client)
    client.post("/api/demo/reset")
    s = client.get("/api/state").json()
    assert s["calls"] == [] and s["loan"]["status"] == "active"


def test_eval_endpoints_run_and_return_results(client, tmp_path, monkeypatch):
    import time
    monkeypatch.setattr(A, "EVAL_PATH", tmp_path / "eval.json")
    assert client.get("/api/eval/results").json()["results"] is None
    assert client.post("/api/eval/run?mode=scripted").json()["status"] in ("started", "already_running")
    for _ in range(100):
        r = client.get("/api/eval/results").json()
        if not r["running"] and r["results"]:
            break
        time.sleep(0.1)
    res = r["results"]
    assert res["passed"] == res["total"] and res["violations_blocked"]["leaked"] == 0
    assert client.post("/api/eval/run?mode=bogus").json()["status"] == "error"


def test_console_page_and_assets_are_served(client):
    page = client.get("/")
    assert page.status_code == 200 and "Keel" in page.text and "/static/app.js" in page.text
    for path in ("/static/tokens.css", "/static/app.css", "/static/app.js"):
        assert client.get(path).status_code == 200
    css = client.get("/static/tokens.css").text
    for token in ("--accent-solid", "--text-primary", "--bg-surface", "--ok-text", "--bad-text", "--relief-fill"):
        assert token in css


def test_app_css_uses_only_defined_tokens(client):
    import re
    tokens = set(re.findall(r"(--[a-z0-9-]+):", client.get("/static/tokens.css").text))
    css = client.get("/static/app.css").text
    local = set(re.findall(r"(--[a-z0-9-]+):", css))
    used = set(re.findall(r"var\((--[a-z0-9-]+)", css))
    runtime = {"--i"}  # set per bar by app.js for the staggered animation, not a colour
    assert not (used - tokens - local - runtime), used - tokens - local - runtime
    assert not re.findall(r"#[0-9a-fA-F]{3,8}\b", css.replace("%23", "")), "raw hex colour in app.css; use a token"


def test_state_attaches_cached_audio_to_keel_lines(client, tmp_path, monkeypatch):
    from keel.voice import tts
    monkeypatch.setattr(tts, "AUDIO_DIR", tmp_path / "audio")
    run(client)
    lines = client.get("/api/state").json()["calls"][0]["transcript"]
    assert all(len(l) == 3 for l in lines) and all(l[2] is None for l in lines)  # nothing generated yet
    (tmp_path / "audio").mkdir()
    for who, text, _ in lines:
        if who == "agent":
            tts.audio_path(text).write_bytes(b"RIFF")
    lines = client.get("/api/state").json()["calls"][0]["transcript"]
    assert all((l[2] is not None) == (l[0] == "agent") for l in lines)
