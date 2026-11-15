"""Usage: python scripts/run_evals.py [scripted|llm]. Prints the summary and writes data/eval_results.json."""
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from keel.evals.runner import run_all  # noqa: E402

mode = sys.argv[1] if len(sys.argv) > 1 else "scripted"
res = run_all(mode)
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / "eval_results.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
vb, na = res["violations_blocked"], res["number_audit"]
print(f"mode={mode}  scenarios passed {res['passed']} of {res['total']}")
print(f"violations blocked: {vb['blocked']} of {vb['attempted']} scripted attacks, leaked {vb['leaked']}")
for k, v in vb["by_rule"].items():
    print(f"  {k:10} {v['blocked']}/{v['attempted']}  {v['label']}")
print("escalations by reason:", res["escalations_by_reason"])
print(f"number audit: {na['figures_spoken']} figures spoken, {na['figures_spoken_wrong']} wrong, pass rate {na['pass_rate_pct']}%, "
      f"{na['wrong_figures_blocked_at_gate']} wrong figures blocked at the gate")
print("model errors:", res["model_errors"])
print("autonomous (normal):", res["autonomous"])
print("categories:", res["categories"])
print("known gaps:", res["known_gaps"])
for r in res["scenarios"]:
    if not r["passed"]:
        print("FAIL", r["id"], r["title"], r["problems"])
