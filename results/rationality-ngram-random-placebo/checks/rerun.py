"""Reproduce every number from the raw public data and compare with data/expected.json.
Usage: python checks/rerun.py [--workdir DIR] [--reuse]
  Streams the Google Books v3 eng + eng-fiction 1-grams (about 7.3 GB, not stored),
  clones the authors' repo (for the reproduction check), builds the table, runs the analysis.
  Then runs the post-hoc script (checks/posthoc.py) and compares with data/expected_posthoc.json.
  --reuse: skip the download if DIR/ext already holds complete extracts."""
import argparse, json, os, subprocess, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ap = argparse.ArgumentParser(); ap.add_argument("--workdir", default=os.path.join(ROOT, "work", "rerun"))
ap.add_argument("--reuse", action="store_true"); a = ap.parse_args()
W = a.workdir; os.makedirs(W, exist_ok=True); py = sys.executable
def run(*cmd, **kw):
    print("+", " ".join(cmd), flush=True); subprocess.run(cmd, check=True, **kw)
run("cc", "-O2", "-o", os.path.join(W, "extract"), os.path.join(HERE, "extract.c"))
env = dict(os.environ, EXTRACT_BIN=os.path.join(W, "extract"))
ext = os.path.join(W, "ext")
if not a.reuse:
    run("bash", os.path.join(HERE, "fetch_extract.sh"), ext, "eng", *map(str, range(24)), env=env)
    run("bash", os.path.join(HERE, "fetch_extract.sh"), ext, "eng-fiction", "0", env=env)
repo = os.path.join(W, "authors_repo")
if not os.path.isdir(repo):
    run("git", "clone", "-q", "--depth", "1", "https://github.com/jbollen/rise_and_fall_of_rationality_in_language", repo)
tab = os.path.join(W, "table.npz"); out = os.path.join(W, "results.json")
run(py, "-I", os.path.join(HERE, "build.py"), ext, tab)
run(py, "-I", os.path.join(HERE, "analysis.py"), tab, out, repo)
out_ph = os.path.join(W, "posthoc.json")
run(py, "-I", os.path.join(HERE, "posthoc.py"), tab, out_ph)
bad = []; n = 0
def cmp(e, g, path):
    global n
    if isinstance(e, dict):
        for k in e: cmp(e[k], g.get(k) if isinstance(g, dict) else None, path + "/" + k)
    elif isinstance(e, list):
        if not isinstance(g, list) or len(g) != len(e): bad.append(path); return
        for i, (x, y) in enumerate(zip(e, g)): cmp(x, y, f"{path}[{i}]")
    elif isinstance(e, float):
        n += 1
        if not isinstance(g, (int, float)) or not math.isclose(e, g, rel_tol=1e-9, abs_tol=1e-12): bad.append(f"{path}: {e} vs {g}")
    else:
        n += 1
        if e != g: bad.append(f"{path}: {e} vs {g}")
got = json.load(open(out))
cmp(json.load(open(os.path.join(ROOT, "data", "expected.json"))), got, "")
cmp(json.load(open(os.path.join(ROOT, "data", "expected_posthoc.json"))), json.load(open(out_ph)), "/posthoc")
print(f"compared {n} values; mismatches: {len(bad)}")
for b in bad[:20]: print("  ", b)
print("PRIMARY", got["primary"])
sys.exit(1 if bad else 0)
