"""Reproduce every number from the raw public data and compare with data/expected.json.

Usage (from the problem folder, with the venv of README/RESULT.md):
  .venv/bin/python -I checks/rerun.py [--work DIR] [--work2016 DIR] [--skip-2016]

Steps:
 1. Stream the 36 (or 48) monthly Lichess files, keep header rows, check each sha256 against
    https://database.lichess.org/standard/sha256sums.txt.
 2. Build the 2013-2015 player-game table and run the primary analysis.
 3. Build the 2013-2016 table and run addendum A (periods A and B and their difference).
 4. Compare every number with data/expected.json (relative tolerance 1e-9).
Run time on an M1 Pro: about 15 min download and extraction (2 parallel streams), 6 min build
2013-2015, 25 min build 2013-2016, 3 min analysis.
"""
import argparse, json, os, subprocess, sys, urllib.request, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable
ap = argparse.ArgumentParser()
ap.add_argument("--work", default=os.path.join(ROOT, "work", "rerun"))
ap.add_argument("--work2016", default="/tmp/pbq_rerun2016")
ap.add_argument("--skip-2016", action="store_true")
a = ap.parse_args()
hdrA = os.path.join(a.work, "hdr")
os.makedirs(hdrA, exist_ok=True)
months = [f"{y}-{m:02d}" for y in (2013, 2014, 2015) for m in range(1, 13)]
months16 = [f"2016-{m:02d}" for m in range(1, 13)]


def run(cmd, env=None):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, env={**os.environ, **(env or {})})


jobs = [(m, hdrA) for m in months] + ([] if a.skip_2016 else [(m, a.work2016) for m in months16])
# Two download streams at a time.
procs = []
for m, d in jobs:
    procs.append(subprocess.Popen(["bash", os.path.join(HERE, "fetch_month.sh"), m, d], env={**os.environ, "PY": PY}))
    if len(procs) == 2:
        for p in procs:
            assert p.wait() == 0
        procs = []
for p in procs:
    assert p.wait() == 0

sums = {}
with urllib.request.urlopen("https://database.lichess.org/standard/sha256sums.txt") as f:
    for line in f.read().decode().splitlines():
        h, name = line.split()
        sums[name] = h
bad = []
for m, d in jobs:
    got = open(os.path.join(d, f"{m}.sha256")).read().strip()
    if got != sums[f"lichess_db_standard_rated_{m}.pgn.zst"]:
        bad.append(m)
print("sha256 mismatches:", bad or "none", flush=True)
assert not bad

out = {}
pqA = os.path.join(a.work, "player_games_2013_2015.parquet")
run([PY, "-I", os.path.join(HERE, "build.py"), hdrA, pqA], {"DUCK_TMP": os.path.join(a.work, "duck_tmp")})
rA = os.path.join(a.work, "results.json")
run([PY, "-I", os.path.join(HERE, "analyze.py"), pqA, rA])
out["primary"] = json.load(open(rA))

if not a.skip_2016:
    pqB = os.path.join(a.work2016, "player_games_2013_2016.parquet")
    run([PY, "-I", os.path.join(HERE, "build.py"), hdrA + ":" + a.work2016, pqB],
        {"NFILES": "48", "END": "2016-12-30 23:59:59", "DUCK_TMP": os.path.join(a.work2016, "duck_tmp")})
    run([PY, "-I", os.path.join(HERE, "addendum.py"), pqB, os.path.join(a.work, "addendum")])
    out["addendum"] = json.load(open(os.path.join(a.work, "addendum", "addendum.json")))

exp = json.load(open(os.path.join(ROOT, "data", "expected.json")))
fails = []


def cmp(e, g, path):
    if isinstance(e, dict):
        for k in e:
            if k not in g:
                fails.append(f"{path}.{k}: missing")
            else:
                cmp(e[k], g[k], f"{path}.{k}")
    elif isinstance(e, list):
        if len(e) != len(g):
            fails.append(f"{path}: length {len(g)} != {len(e)}")
        for i, (x, y) in enumerate(zip(e, g)):
            cmp(x, y, f"{path}[{i}]")
    elif isinstance(e, float):
        if not math.isclose(e, g, rel_tol=1e-9, abs_tol=1e-12):
            fails.append(f"{path}: {g} != {e}")
    elif e != g:
        fails.append(f"{path}: {g} != {e}")


for key in out:
    cmp(exp[key], out[key], key)
print("mismatches:", len(fails))
for f in fails[:50]:
    print("  ", f)
print("RERUN", "PASS" if not fails else "FAIL")
sys.exit(1 if fails else 0)
