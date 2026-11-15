# Keel

An AI agent that keeps a small merchant's loan on track, in Tamil, inside the lender's rules.
Team JustUs, Paytm Build for India AI Hackathon (Chennai), Track 2. Everything runs on synthetic data.

## Run it

```
.venv\Scripts\python -m uvicorn keel.api.app:app --port 8000
```

Open http://localhost:8000. Put your Sarvam key in `.env` (`SARVAM_API_KEY=`). The scripted agent and the cached audio work without it.

| Task | Command |
|---|---|
| Run the tests | `.venv\Scripts\python -m pytest -q` |
| Run all scenarios, scripted | `.venv\Scripts\python scripts\run_evals.py scripted` |
| Run all scenarios with the Sarvam model (about 3 minutes) | `.venv\Scripts\python scripts\run_evals.py llm` |
| One live call with the model | `.venv\Scripts\python scripts\run_llm_call.py 2345 yes` |
| Regenerate the Tamil audio | `.venv\Scripts\python scripts\make_audio.py --force` |
| Re-record the backup video (server running) | `.venv\Scripts\python scripts\record_backup.py` |
| Rebuild the colour tokens (checks contrast) | `.venv\Scripts\python scripts\make_tokens.py` |

## A three-minute demo

1. **Live case.** Murugan's sales are at 62.5% of a normal day. Say what Keel watches: settlements, not missed payments.
2. Choose *Merchant agrees (Tamil)*, agent *Scripted* (or *Sarvam model*), press **Check stress and place call**. The four steps turn green and the schedule changes: ₹300 a day for 14 days, the loan ends 6 days later.
3. Press **Play the call** to hear Keel's Tamil lines.
4. Press **Reset demo data**, choose *Says the shop is closing*, place the call. The case lands in the **Handover queue** with a summary.
5. **Audit log.** Press *Verify the chain* (intact), then *Edit a row outside the app*, then verify again (broken at row 3).
6. **Test results.** About 60 scenarios, three figures. Say the known gap out loud.

If anything fails live, play `backup\Keel_demo_backup.mp4` (about 100 seconds, works offline).

## What is real and what is mocked

| Real | Mocked or not built |
|---|---|
| Stress detector, offer maths, schedule versions | Merchants, loans, settlements (synthetic) |
| Policy engine, rules R1 to R10, consent capture, number-audit | Paytm and bank systems, money movement, e-mandate |
| Hash-chained audit log, handover queue | WhatsApp, SMS and UPI link (not built) |
| Sarvam `sarvam-105b` tool-calling agent (and a scripted fallback) | Live speech-to-text and a live voice call (not built) |
| Sarvam text-to-speech, cached | Paytm sandbox, unless offered on the day |

## Known gaps

- The agent's free-form wording is checked for figures only. A false statement with no number in it is not caught (scenario G01).
- The scenarios are ours. Results show the rules work as designed, not that every attack is covered.
- The Tamil lines in `keel/policy/templates.py` are not yet checked by a native speaker. A machine round trip (`scripts/check_audio_stt.py`) confirms every figure is spoken correctly, but not how natural it sounds. Use `TAMIL_REVIEW.md` for a five-minute human check.
- The offer terms (₹500 a day, 75% rule, ₹300 floor, 14 days) are illustrative, not Paytm's real terms.

## Where things are

`keel/policy` rules engine, audit chain, templates · `keel/detector` stress rule · `keel/agent` scripted and model agents · `keel/voice` text channel and text-to-speech · `keel/evals` scenarios and runner · `keel/api` FastAPI · `keel/web` the screen · `PRD.md`, `TRD.md`, `ARCHITECTURE.md` the design documents.
