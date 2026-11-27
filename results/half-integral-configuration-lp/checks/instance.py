"""Builds the counterexample instance to Conjecture 10 of arXiv:2609.19967.

12 machines (c, t), c in {0,1,2} (copy), t in {0,1,2,3}; machine index 4c + t.
Point jobs P(c,k), k in {0,1,2,3}, size 1, allowed on machines (c, t) with t != k.
Filler jobs F(f), f in {0..7}, size 3; machine i is allowed fillers 2i mod 8 and 2i+1 mod 8.
T = 3.
Fractional point: x = 1/3 on {points of copy c except k=t} for machine (c,t), and
x = 1/3 on each single-filler configuration of each machine.
"""
import json
from fractions import Fraction


def build():
    m, T = 12, 3
    p, M, names = [], [], []
    for c in range(3):
        for k in range(4):
            names.append(f"P{c}{k}"); p.append(1)
            M.append(sorted(4 * c + t for t in range(4) if t != k))
    for f in range(8):
        names.append(f"F{f}"); p.append(3)
        M.append(sorted(i for i in range(m) if f in (2 * i % 8, (2 * i + 1) % 8)))
    x = []
    third = str(Fraction(1, 3))
    for i in range(m):
        c, t = divmod(i, 4)
        line = [4 * c + k for k in range(4) if k != t]  # job index of P(c,k) is 4c+k
        x.append([i, line, third])
        for f in (2 * i % 8, (2 * i + 1) % 8):
            x.append([i, [12 + f], third])
    return {"p": p, "M": M, "m": m, "T": T, "names": names, "x": x}


if __name__ == "__main__":
    print(json.dumps(build()))
