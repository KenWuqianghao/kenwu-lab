"""Download the raw public data, recompute every number, compare with data/expected.json.

Usage: .venv/bin/python -I checks/rerun.py [workdir]   (default workdir: work/rerun)
Needs numpy, scipy, skyfield. Full run: about 30-40 min on one M1 core (see RESULT.md).
"""
import hashlib
import json
import os
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
work = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "work", "rerun")
raw, cache = os.path.join(work, "raw"), os.path.join(work, "cache")
os.makedirs(raw, exist_ok=True)
URLS = {"ghcnd_hcn.tar.gz": "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd_hcn.tar.gz",
        "ghcnd-stations.txt": "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt",
        "ghcnd-version.txt": "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-version.txt",
        "de440s.bsp": "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp"}
for fn, url in URLS.items():
    p = os.path.join(raw, fn)
    if not os.path.exists(p):
        print("download", url, flush=True)
        urllib.request.urlretrieve(url, p)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    print(f"{fn} sha256 {h}")
print(open(os.path.join(raw, "ghcnd-version.txt")).read().splitlines()[0])
out = os.path.join(work, "results.json")
subprocess.run([sys.executable, "-I", os.path.join(HERE, "run_all.py"), raw, cache, out], check=True)
outx = os.path.join(work, "exploratory.json")
subprocess.run([sys.executable, "-I", os.path.join(HERE, "exploratory.py"), cache, outx], check=True)
outt = os.path.join(work, "timing.json")
subprocess.run([sys.executable, "-I", os.path.join(HERE, "timing.py"), raw, cache, outt], check=True)

got = json.load(open(out))
got["exploratory"] = json.load(open(outx))
got["timing"] = json.load(open(outt))
exp = json.load(open(os.path.join(ROOT, "data", "expected.json")))
TOL = exp.pop("_tolerance")
bad = 0


def get(d, path):
    for k in path.split("/"):
        d = d[int(k)] if isinstance(d, list) else d[k]
    return d


for path, want in exp.items():
    have = get(got, path)
    if isinstance(want, bool) or isinstance(want, str):
        ok = have == want
    else:
        ok = abs(have - want) <= TOL.get(path.split("/")[-1], 0) + 1e-12
    bad += not ok
    print(f"{'OK  ' if ok else 'FAIL'} {path}: expected {want}, got {have}")
print(f"{len(exp) - bad}/{len(exp)} match")
sys.exit(1 if bad else 0)
