"""Reproduce every number of the paper from the raw public data and compare with data/expected.json.

Usage: python -I checks/rerun.py WORKDIR
WORKDIR must not hold parsed/, build/ or out/ (a from-zero run). WORKDIR/raw can already hold
the 36 monthly files (or be a link to them); each file is checked against its SHA-256.
Env: CHESSZIPF_WORKERS (default 1) months parsed in parallel; CHESSZIPF_DELETE_RAW=1 deletes
each raw file after its parse (peak disk about 8 GB instead of 15 GB).
Steps: download if missing and SHA-256 check (checks/download.sh) and parse (checks/parse_all.sh),
build the sorted key set (checks/build.py), run all pre-registered stages (checks/analyze.py),
run the exploratory analysis (checks/explore.py), run the fit-range robustness check
(checks/robustness.py, not pre-registered), draw fig1.png into WORKDIR/out, compare.
Use --compare-only RESULTS_JSON EXPLORE_JSON ROBUST_JSON to skip the computation.
Use --write-expected RESULTS_JSON EXPLORE_JSON ROBUST_JSON to write data/expected.json from a finished run.
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = os.path.join(ROOT, ".venv", "bin", "python")


def flat(d, pre=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, f"{pre}{k}/"))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out.update(flat(v, f"{pre}{i}/"))
    else:
        out[pre[:-1]] = d
    return out


def expected_view(res, explore, robust):
    """The numbers that the paper reports."""
    keep = {"tests": res["tests"], "csn": res.get("csn"),
            "placebo": {k: v for k, v in res.get("placebo", {}).items() if k.endswith("_mean") or k == "n_games_L40"},
            "strata": {k: ({f: v[f] for f in ("n_games", "alpha_pool", "b", "rho", "d_cr")} if isinstance(v, dict) and "n_games" in v else v)
                       for k, v in res.get("strata", {}).items()},
            "n_games_by_month": res.get("meta"),
            "explore": explore,
            "robustness": robust}
    return keep


def compare(res, explore, robust, exp, rtol=1e-6):
    a, b = flat(expected_view(res, explore, robust)), flat(exp)
    bad = []
    for k, v in b.items():
        w = a.get(k, "MISSING")
        if isinstance(v, float) and isinstance(w, float):
            if not (math.isclose(v, w, rel_tol=rtol, abs_tol=1e-9) or (math.isnan(v) and math.isnan(w))):
                bad.append((k, v, w))
        elif v != w:
            bad.append((k, v, w))
    for k, v, w in bad:
        print(f"MISMATCH {k}: expected {v}, got {w}")
    print(f"{len(b) - len(bad)}/{len(b)} numbers match")
    return not bad


def main():
    exp_path = os.path.join(ROOT, "data", "expected.json")
    months = json.load(open(exp_path))["months"]
    if len(sys.argv) > 4 and sys.argv[1] in ("--compare-only", "--write-expected"):
        res, explore, robust = (json.load(open(f)) for f in sys.argv[2:5])
        if sys.argv[1] == "--write-expected":
            json.dump({"months": months, "numbers": expected_view(res, explore, robust)}, open(exp_path, "w"), indent=1)
            print("wrote", exp_path)
            return
    else:
        if len(sys.argv) != 2:
            sys.exit(__doc__)
        work = sys.argv[1]
        raw, parsed, build, out = (os.path.join(work, x) for x in ("raw", "parsed", "build", "out"))
        old = [d for d in (parsed, build, out) if os.path.exists(d)]
        if old:
            sys.exit(f"rerun.py needs a from-zero run; remove {old} first")
        os.makedirs(out)
        nw = int(os.environ.get("CHESSZIPF_WORKERS", "1"))
        jobs = [subprocess.Popen([os.path.join(HERE, "parse_all.sh"), raw, parsed, str(w), str(nw)]) for w in range(nw)]
        if any([j.wait() != 0 for j in jobs]):
            sys.exit("download or parse failed")
        subprocess.run([PY, "-I", os.path.join(HERE, "build.py"), parsed, build] + months, check=True)
        rj, ej, bj = (os.path.join(out, f) for f in ("results.json", "explore.json", "robustness.json"))
        subprocess.run([PY, "-I", os.path.join(HERE, "analyze.py"), build, rj], check=True)
        subprocess.run([PY, "-I", os.path.join(HERE, "explore.py"), build, ej], check=True)
        subprocess.run([PY, "-I", os.path.join(HERE, "robustness.py"), build, bj], check=True)
        subprocess.run([PY, "-I", os.path.join(HERE, "figure.py"), rj, os.path.join(out, "hists_N%d.npz" % json.load(open(rj))["tests"]["N_full"]),
                        os.path.join(out, "fig1.png")], check=True)
        res, explore, robust = (json.load(open(f)) for f in (rj, ej, bj))
    exp = json.load(open(exp_path))
    ok = compare(res, explore, robust, exp["numbers"])
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
