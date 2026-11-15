"""Run one live call with the Sarvam model. Usage: python scripts/run_llm_call.py [reply1 reply2 ...]
Default merchant replies: the last four digits, then yes."""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from keel.agent.llm import make_client  # noqa: E402
from keel.agent.llm_agent import run_llm_call  # noqa: E402
from keel.demo import make_engine  # noqa: E402
from keel.detector import detect  # noqa: E402
from keel.policy import verify_chain  # noqa: E402
from keel.voice import TextChannel  # noqa: E402

replies = sys.argv[1:] or ["2345", "yes"]
eng = make_engine()
sig = detect(eng, "L1")
ch = TextChannel(replies)
cid = eng.start_call("L1", sig, ch)
trace: list = []
call = run_llm_call(eng, cid, make_client(), trace)
print("--- transcript ---")
for who, text in ch.transcript:
    print(f"{who}: {text}")
print("--- tool trace ---")
for t in trace:
    print(t.get("tool", "ERROR"), str(t.get("args", t.get("error")))[:80], "->", str(t.get("result", ""))[:110])
print("--- outcome ---")
print({k: call[k] for k in ("outcome", "autonomous", "identity_verified", "escalation_reason")})
print("audit chain:", verify_chain(eng.con))
