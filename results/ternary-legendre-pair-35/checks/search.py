"""Rerun the multiplier-orbit search at length 35 and compare with data/expected.json.

Run from the result folder:  python3 -I checks/search.py [g ...]
With no arguments it runs every group in data/expected.json. A C compiler (cc) is needed.
For each g, the search takes the sequences that are constant on the orbits of <g> in Z_35
and have composition (11, 12, 12), and counts the ordered pairs (A, B) of such sequences
with PAF(A, s) + PAF(B, s) = -2 for s = 1, ..., 17.
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = HERE / "search"
expected = json.loads((ROOT / "data/expected.json").read_text())["search_35"]

cert = {}
for line in (ROOT / "data/lp35.txt").read_text().splitlines():
    if line and not line.startswith("#"):
        k, w = line.split()
        cert[k] = w

with tempfile.TemporaryDirectory() as build:
    exe = pathlib.Path(build) / "mitm"
    subprocess.run(["cc", "-O2", "-o", str(exe), str(SRC / "mitm.c")], check=True)
    groups = sys.argv[1:] or list(expected)
    bad = 0
    for g in groups:
        want = expected[g]
        orbits = subprocess.run([sys.executable, "-I", str(SRC / "orbits.py"), "35", g],
                                check=True, capture_output=True, text=True).stdout
        t = time.time()
        run = subprocess.run([str(exe)], input=orbits, capture_output=True, text=True, check=True)
        dt = time.time() - t
        seqs = int(re.search(r"sequences: (\d+)", run.stderr).group(1))
        pairs = int(re.search(r"pairs found \(ordered\): (\d+)", run.stderr).group(1))
        ok = (seqs, pairs) == (want["sequences"], want["pairs"])
        if g == "6":
            # The certificate must be among the pairs that the search prints.
            ok = ok and f"A {cert['A']} B {cert['B']}" in run.stdout.splitlines()
        print(f"{'PASS' if ok else 'FAIL'}  H = <{g}>: {seqs} sequences, {pairs} ordered pairs "
              f"(expected {want['sequences']}, {want['pairs']}); {dt:.0f} s")
        bad += not ok
print("SEARCH MATCHES data/expected.json" if not bad else f"{bad} SEARCH RUN(S) DIFFER")
sys.exit(1 if bad else 0)
