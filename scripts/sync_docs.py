"""One-off: bring TRD.md, ARCHITECTURE.md and PRD.md in line with what was actually built (14 Nov 2026)."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent


def sub(text, old, new, label, regex=False):
    if regex:
        out, n = re.subn(old, new, text, count=1, flags=re.S)
        assert n == 1, f"not found: {label}"
        return out
    assert old in text, f"not found: {label}"
    return text.replace(old, new, 1)


# ---------------- TRD ----------------
p = ROOT / "TRD.md"
t = p.read_text(encoding="utf-8")
t = sub(t, "Status as of 13 Nov 2026: requirements for the demo build. Nothing is built yet.",
        "Status as of 14 Nov 2026: requirements for the demo build. The core is built and tested (policy engine, audit log, detector, scripted and model-driven agent, screen, scenario run); voice and the backup recording are not.", "status")
t = sub(t, "| Claude or Gemini with tool calling | F7 |", "| Sarvam `sarvam-105b` (OpenAI-compatible chat API) with tool calling | F7 |", "agent row")
t = sub(t, "extension_days = ceil(deferred_rupees / current_daily)`. For the reference case: Rs 300, 14 days, Rs 2,800, 6 days. |",
        "extension_days` is found by projecting the schedule forward with and without the relief and taking the difference in end dates (it equals `ceil(deferred_rupees / current_daily)` for the reference case, and stays correct when the last instalment is partial). For the reference case: Rs 300, 14 days, Rs 2,800, 6 days. |", "F10")
t = sub(t, "v2 is the relief amount from the day after the offer for `relief_days`; v3 resumes the original amount until the balance is cleared. `UNIQUE(offer_id)` blocks a double application. |",
        "v2 is the relief amount from the day after the offer for `relief_days`; v3 resumes the original amount until the balance is cleared. `UNIQUE(offer_id)` on v2 blocks a double application; v3 carries no `offer_id`. |", "F14")
t = sub(t, "`hash = SHA-256(seq, timestamp, actor, action, canonical(inputs), canonical(result), rule_id, prev_hash)`",
        "`hash = SHA-256(canonical([seq, timestamp, call_id, loan_id, merchant_id, actor, action, inputs, result, rule_id, prev_hash]))`", "F27")
t = sub(t, "| F29 | Must | 30 to 40 scenarios, generated from templates and kept in YAML, run in text mode against the real agent and the real policy engine. |",
        "| F29 | Must | About 60 scenarios, generated from templates (`evals/generate.py`) and kept in YAML, run in text mode against the real policy engine. The normal scenarios run with the scripted agent or the real model; the attack scenarios use a scripted tool-call sequence that simulates a misbehaving model. |", "F29")
t = re.sub(r"\| F30 \| Must \|.*?\|\n", "| F30 | Must | Categories: normal, unclear or declined, angry borrower (distress, disputes, requests outside the limits), out-of-hours, adversarial (merchant injection and simulated model misbehaviour). At least 5 per category. One known gap is reported separately and not counted as blocked. |\n", t, count=1)
t = sub(t, "| F32 | Could | A toy roll-rate simulation with its assumptions listed. It is not a headline figure. |",
        "| F32 | Won't | Roll-rate simulation. Dropped from the build; the deck must not promise it. |", "F32")
t = sub(t, "Signatures are in Python and MCP-shaped (name, typed arguments, structured result). Wrap them in an MCP server only if time remains, or to swap in a Paytm MCP server on the day.",
        "Signatures are in Python and MCP-shaped (name, typed arguments, structured result). There is no separate MCP server; the shape allows one later, or a Paytm MCP server on the day.", "mcp para")
# tool table: add the three extra tools
t = sub(t, "| `get_settlements` |", "| `verify_identity` | `last4` | `{verified, attempts_left}` | Two wrong tries end the call (R9) |\n| `listen` | none | `{merchant_said, escalated?}` | Every merchant message passes the distress and dispute backstop |\n| `get_settlements` |", "tool rows")
t = sub(t, "| `create_upi_link` | `loan_id`, `amount_rupees` | `{link_id, url}` | Could; mock only |",
        "| `finish_call` | none | `{finished, outcome}` | Ends the call |\n| `create_upi_link` | `loan_id`, `amount_rupees` | `{link_id, url}` | Not built; mock only if time allows |", "upi row")
# HTTP API block
t = sub(t, r"\| Endpoint \| Purpose \|\n\|---\|---\|\n.*?\n\n", """| Endpoint | Purpose |
|---|---|
| `GET /api/state` | Merchant, loan, derived balance, schedule versions, settlements, signals, calls with transcripts, handover queue |
| `GET /api/personas` | The merchant behaviours the screen can play |
| `POST /api/demo/run` | Run the detector on the seeded merchant, then place the call with the chosen behaviour and agent |
| `POST /api/demo/reset` | Rebuild the demo database |
| `GET /api/audit` | Audit rows, newest first |
| `GET /api/audit/verify` | Recompute the hash chain; return ok or the first broken seq |
| `POST /api/demo/tamper` | Edit a row outside the app, to show verification catching it |
| `GET /api/queue` | Open handover cases |
| `POST /api/eval/run` | Start the scenario run (`mode=scripted` or `llm`) in the background |
| `GET /api/eval/results` | Progress and the last results, including the three figures |

""", "http table", regex=True)
t = sub(t, "| Frontend | React (audit and handover view first, then call screen, then results screen) | Proposed |",
        "| Frontend | One static HTML page served by FastAPI, no build step, works offline (call, schedule, handover queue, audit with verify, results) | Built |", "frontend")
t = sub(t, "| Agent model | Claude or Gemini with tool calling | **Open: decide today** |",
        "| Agent model | Sarvam `sarvam-105b` through the OpenAI-compatible chat API, tool calling. Key in `.env`. Retries on rate limits; falls back to the scripted agent | **Decided** |", "model row")
t = sub(t, "  web/           React app", "  web/           single HTML page (no build step)\n  scripts/       run_llm_call, run_evals", "layout web")
t = sub(t, "  voice/         STT, TTS, call runner, text-mode adapter", "  voice/         text-mode channel (STT, TTS and the call runner are not built)", "layout voice")
t = sub(t, "The results screen shows the three figures for 30 to 40 scenarios, labelled synthetic, with zero blocked actions leaking through and zero figure mismatches spoken.",
        "The results screen shows the three figures for about 60 scenarios, labelled synthetic, with zero blocked actions leaking through and zero wrong figures spoken.", "A5")
t = sub(t, "Align the deck with these documents (30 to 40 scenarios, no separate MCP server, roll-rate optional)",
        "Align the deck with these documents (about 60 scenarios, no separate MCP server, no roll-rate simulation). Also state the known gap: free-form wording with no figure is not verified", "risk deck")
t = sub(t, "| Event logistics (registration", "| Sarvam rate limits (HTTP 429) or a network failure during the demo | The model call stalls or fails | Client retries with backoff; a failure before speech restarts with the scripted agent, a failure mid-call hands the case to a person; scenario run uses 2 parallel calls; keep the scripted agent selectable on screen |\n| Event logistics (registration", "risk 429") if "| Event logistics (registration" in t else t
t = sub(t, "1. Toy roll-rate simulation (F32) and the UPI link (`create_upi_link`).", "1. The UPI link (`create_upi_link`). The roll-rate simulation (F32) is already dropped.", "cut order")
t = sub(t, "1. Claude or Gemini (owner and date to be named).\n2. LiveKit or Pipecat (owner and date to be named).",
        "1. ~~Claude or Gemini~~ Decided: Sarvam `sarvam-105b`.\n2. Voice: Sarvam speech with LiveKit or Pipecat, or pre-generated audio for key lines (owner and date to be named).", "open items")
t = sub(t, "6. Updating the deck so it matches this TRD.", "6. Updating the deck so it matches this TRD (scenario count, roll-rate, MCP server, model).\n7. A Tamil speaker must review the spoken lines in `policy/templates.py` and the yes-word list.", "open 6")
p.write_text(t, encoding="utf-8")

# ---------------- ARCHITECTURE ----------------
p = ROOT / "ARCHITECTURE.md"
a = p.read_text(encoding="utf-8")
a = sub(a, "Status as of 13 Nov 2026: planned design for the hackathon demo. Nothing here is built yet.",
        "Status as of 14 Nov 2026: design for the hackathon demo. The core is built and tested; voice and the backup recording are not.", "arch status")
a = sub(a, "| A tool-calling LLM (Claude or Gemini; to be chosen today) |", "| Sarvam `sarvam-105b` through its OpenAI-compatible chat API, with tool calling; a scripted agent is the fallback |", "arch agent")
a = sub(a, "Wrap them in an MCP server only if time remains, or to swap in a Paytm MCP server on the day", "There is no separate MCP server; the shape allows one later, or a Paytm MCP server on the day", "arch mcp")
a = sub(a, "| FastAPI backend, React frontend: audit and handover view first, then the call screen, then the results dashboard |",
        "| FastAPI backend and one static HTML page (no build step, works offline): call, schedule, handover queue, audit with verify, results |", "arch app")
a = sub(a, "| 30 to 40 text-mode scenarios generated from templates, kept in YAML |", "| About 60 text-mode scenarios generated from templates, kept in YAML; attack scenarios use a scripted misbehaving model |", "arch eval")
a = sub(a, "1. Claude or Gemini for the agent.", "1. ~~Claude or Gemini~~ Decided: Sarvam `sarvam-105b`.", "arch open 1")
a = sub(a, "- `UNIQUE(offer_id)` stops a retried or double-accepted offer creating two versions.",
        "- `UNIQUE(offer_id)` on the relief row (v2) stops a retried or double-accepted offer creating two versions. v3 has no `offer_id`. A `kind` column marks each row original, relief or resume.", "arch unique")
a = sub(a, "The optional toy roll-rate simulation lists its assumptions.", "The roll-rate simulation was dropped.", "arch roll")
a = sub(a, "category (normal, adversarial, out_of_hours, angry_borrower, prompt_injection, hallucinated_clause)",
        "category (normal, unclear_or_declined, angry_borrower, out_of_hours, adversarial, known_gap), agent (flow or attack)", "arch cats")
p.write_text(a, encoding="utf-8")

# ---------------- PRD ----------------
p = ROOT / "PRD.md"
r = p.read_text(encoding="utf-8")
r = sub(r, "A results screen from 30 to 40 scripted text-mode scenarios, adversarial ones included",
        "A results screen from about 60 scripted text-mode scenarios, adversarial ones included", "prd 50")
r = sub(r, "- **Roll-rate (optional, if time allows):** a toy simulation with its assumptions listed. Not a headline figure.",
        "- **Roll-rate:** dropped from the build. We make no claim about reducing missed payments or credit losses.", "prd roll")
r = sub(r, "Status as of 13 Nov 2026: pitch deck written (`JustUs_Keel_Pitch.pdf`); prototype not yet built. Everything below describes the intended demo build, not shipped software.",
        "Status as of 14 Nov 2026: pitch deck written (`JustUs_Keel_Pitch.pdf`); the text-mode prototype is built and tested (detector, policy engine, audit log, screen, scenario run, Sarvam-driven agent). Voice and the backup recording are not done. Everything below describes the demo build, not shipped software.", "prd status")
p.write_text(r, encoding="utf-8")
print("docs updated")
