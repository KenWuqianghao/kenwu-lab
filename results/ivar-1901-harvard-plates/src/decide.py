"""Decision for set E (1901, 1906 plates) and set A (all plates) from data/results.json (PROTOCOL.md)."""
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); from measure import poisson_binomial_tail
D = Path(os.environ["PRECOVERY_DATA"]) if os.environ.get("PRECOVERY_DATA") else Path(__file__).resolve().parent.parent / "data"
res = json.load(open(D / "results.json"))["plates"]
out = {}
for name, f in [("E", lambda r: r["mid"][:4] in ("1901", "1906")), ("A", lambda r: True)]:
    rs = [r for r in res if f(r)]; k = sum(r["pass"] for r in rs)
    P = poisson_binomial_tail([r["p0"] for r in rs], k) if rs else 1.0
    out[name] = {"n": len(rs), "k_pass": k, "P_null": P, "detected": k >= 2 and P < 0.001,
                 "passing": [r["plate"] for r in rs if r["pass"]], "earliest_pass": min((r["mid"] for r in rs if r["pass"]), default=None)}
    print(name, out[name])
(D / "decision.json").write_text(json.dumps(out, indent=1))
