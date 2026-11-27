"""Reproduce every number of the result from public data and compare with data/expected.json.

Usage (from the result folder):
    python checks/rerun.py               # download (skips files present in work/), analyse, summarise, compare
    python checks/rerun.py --jobs 4      # the same with 4 analysis processes (default 2)
    python checks/rerun.py --compare     # only compare data/summary.json with data/expected.json

To force a fresh download, delete work/ first. data/candidates.csv and data/placebo.csv are inputs:
they are rebuilt from the DR14Q and 2QZ catalogues (about 800 MB) only if you delete them.
Run time on an M1 Pro with 2 processes: about 10 min download and about 45 min analysis.
The per-object random seeds do not depend on the number of processes.
"""
import json
import math
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def flatten(d, pre=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flatten(v, f"{pre}{k}."))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out.update(flatten(v, f"{pre}{i}."))
    else:
        out[pre[:-1]] = d
    return out


STOUFFER_TOL = 0.01


def compare():
    got = flatten(json.load(open(os.path.join(ROOT, "data", "summary.json"))))
    exp = flatten(json.load(open(os.path.join(ROOT, "data", "expected.json"))))
    bad = 0
    for k, v in exp.items():
        g = got.get(k, "MISSING")
        if isinstance(v, float) and isinstance(g, (int, float)) and not isinstance(g, bool):
            # Stouffer Z combines Monte Carlo p-values. They can differ slightly between
            # platforms (see checks/README.md), so these values get an absolute tolerance.
            tol = STOUFFER_TOL if k.rsplit(".", 1)[-1].startswith("stouffer_") else 1e-6
            ok = math.isclose(v, g, rel_tol=1e-3, abs_tol=tol) or (math.isnan(v) and math.isnan(g))
        else:
            ok = v == g
        if not ok:
            bad += 1
            print(f"MISMATCH {k}: expected {v!r}, got {g!r}")
    print(f"{len(exp) - bad}/{len(exp)} expected values reproduced")
    return bad == 0


def main():
    if "--compare" not in sys.argv:
        subprocess.run([PY, os.path.join(ROOT, "checks", "fetch_data.py")], check=True)
        n = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 2
        procs = [subprocess.Popen([PY, os.path.join(ROOT, "checks", "analysis.py"), str(i), str(n)]) for i in range(n)]
        codes = [p.wait() for p in procs]
        if any(codes):
            sys.exit(f"analysis.py failed: exit codes {codes}")
        subprocess.run([PY, os.path.join(ROOT, "checks", "summarize.py")], check=True, stdout=subprocess.DEVNULL)
    sys.exit(0 if compare() else 1)


if __name__ == "__main__":
    main()
