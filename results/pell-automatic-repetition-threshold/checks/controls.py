"""Negative controls for checks/decide.py.

Usage: python3 -I checks/controls.py data/PSQ.txt

Changes one transition of the PSQ DFAO at a time, in all 33 possible ways (the loop
delta(0,0) = 0 stays). For each changed DFAO that has a square in its first 4000 letters
(brute force), decide.py must report FOUND, and the reported (i, n) must be a real square.
The last line is a JSON object for ci.sh."""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    d, out, q = {}, {}, None
    for l in open(path):
        t = l.split()
        if not t or t[0] == "msd_pell":
            continue
        if "->" in t:
            d[q][int(t[0])] = int(t[2])
        else:
            q = int(t[0])
            d[q] = [None] * 3
            out[q] = int(t[1])
    return d, out


P = [1, 2]
while P[-1] < 10**6:
    P.append(2 * P[-1] + P[-2])


def word(d, out, N):
    X = []
    for n in range(N):
        q = 0
        for w in reversed(P):
            c = n // w
            n -= c * w
            q = d[q][c]
        X.append(out[q])
    return X


def write(d, out, path):
    with open(path, "w") as f:
        f.write("msd_pell\n\n")
        for s in sorted(d):
            f.write("%d %d\n" % (s, out[s]))
            for c in range(3):
                f.write("%d -> %d\n" % (c, d[s][c]))
            f.write("\n")


def main():
    base, out = load(sys.argv[1])
    results, skipped, wide = [], 0, 0
    with tempfile.TemporaryDirectory() as tmp:
        for q in sorted(base):
            for a in range(3):
                for t in sorted(base):
                    if (q, a) == (0, 0) or base[q][a] == t:
                        continue
                    d = {k: list(v) for k, v in base.items()}
                    d[q][a] = t
                    X = word(d, out, 4000)
                    f = next(((i, n) for n in range(1, 300) for i in range(3400)
                              if X[i:i + n] == X[i + n:i + 2 * n]), None)
                    if f is None:
                        skipped += 1
                        continue
                    path = os.path.join(tmp, "mut.txt")
                    write(d, out, path)
                    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "decide.py"), path, "square"],
                                       capture_output=True, text=True, timeout=1800).stdout
                    m = re.search(r"FOUND i=(\d+) n=(\d+)", r)
                    ok = False
                    if m:
                        i, n = int(m.group(1)), int(m.group(2))
                        Y = word(d, out, i + 2 * n + 1)
                        ok = n >= 1 and Y[i:i + n] == Y[i + n:i + 2 * n]
                        wide += ok and n >= 2
                    print("change delta(%d,%d)=%d: brute force square %s; decide.py %s; real square: %s"
                          % (q, a, t, f, m.group(0) if m else "no witness", ok), flush=True)
                    results.append(ok)
    print(json.dumps({"controls_run": len(results), "controls_detected": sum(results),
                      "controls_period_ge_2": wide, "controls_no_square_in_prefix": skipped}))


if __name__ == "__main__":
    main()
