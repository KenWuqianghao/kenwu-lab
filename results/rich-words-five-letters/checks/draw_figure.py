#!/usr/bin/env python3
"""Draw data/exponents.svg and paper/exponents.pdf from data/prefix_check_A.txt.

The input is the output of `prefix_check A 3000000` (largest exponent of a repetition
in each dyadic band of periods). This script is not part of the proof.
"""
import os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
rows = []
for line in open(os.path.join(root, "data", "prefix_check_A.txt")):
    m = re.match(r"band p in \[2\^(\d+),2\^\d+\): best (\d+)/(\d+) = ", line)
    if m:
        rows.append((int(m.group(3)), int(m.group(2)) / int(m.group(3))))
rows = [r for r in rows if r[0] < 2**21]  # the last band is cut by the end of the prefix
ESTAR = 2.0592854489537
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.plot([p for p, _ in rows], [e for _, e in rows], "o-", color="#1f5fa8", ms=4,
        label="largest exponent, best period in each band")
ax.axhline(ESTAR, color="#b03020", lw=1, ls="--", label=r"$E^*(u_9)\approx 2.0592854$")
ax.set_xscale("log", base=2)
ax.set_xlabel("period of the repetition")
ax.set_ylabel("exponent")
ax.set_ylim(1.995, 2.065)
ax.legend(loc="lower right", fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(root, "data", "exponents.svg"))
fig.savefig(os.path.join(root, "paper", "exponents.pdf"))
print("wrote data/exponents.svg and paper/exponents.pdf from", len(rows), "bands")
