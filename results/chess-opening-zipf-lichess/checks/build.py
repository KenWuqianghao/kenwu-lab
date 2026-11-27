"""Merge parsed months into one sorted key set.

Usage: python -I build.py PARSED_DIR OUT_DIR MONTH [MONTH ...]
Writes OUT_DIR/col_XX.npy (global token columns, original order) and OUT_DIR/sorted.npz with
lcp, L, speed, elo, month (all in sorted order) and perm (sorted -> original index).
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zipflib import D, sort_lcp


def main(pdir, odir, months):
    t0 = time.time()
    os.makedirs(odir, exist_ok=True)
    sizes = []
    for m in months:
        with np.load(os.path.join(pdir, m + ".npz")) as z:
            sizes.append(len(z["L"]))
    n = int(sum(sizes))
    cols = [np.lib.format.open_memmap(os.path.join(odir, f"col_{c:02d}.npy"), "w+", np.uint16, (n,)) for c in range(D)]
    L = np.empty(n, np.uint8); speed = np.empty(n, np.uint8); elo = np.empty(n, np.uint16); mon = np.empty(n, np.uint8)
    vocab = {}
    pos = 0
    for mi, m in enumerate(months):
        with np.load(os.path.join(pdir, m + ".npz")) as z:
            lv = z["vocab"]
            remap = np.zeros(len(lv) + 1, np.uint16)
            for i, s in enumerate(lv.tolist()):
                remap[i + 1] = vocab.setdefault(s, len(vocab) + 1)
            tok = remap[z["tok"]]
            k = len(tok)
            for c in range(D):
                cols[c][pos:pos + k] = tok[:, c]
            L[pos:pos + k] = z["L"]; speed[pos:pos + k] = z["speed"]; elo[pos:pos + k] = z["elo"]; mon[pos:pos + k] = mi
            pos += k
        print(m, k, "games", f"{time.time() - t0:.0f}s", flush=True)
    assert len(vocab) < 65535
    for c in cols:
        c.flush()
    del cols
    colpath = [os.path.join(odir, f"col_{c:02d}.npy") for c in range(D)]
    perm, lcp = sort_lcp(lambda c: np.load(colpath[c]), n)
    print("sorted", f"{time.time() - t0:.0f}s", flush=True)
    np.savez(os.path.join(odir, "sorted.npz"), lcp=lcp, L=L[perm], speed=speed[perm], elo=elo[perm],
             month=mon[perm], perm=perm, months=np.array(months), vocab_size=len(vocab))
    print("N", n, "vocab", len(vocab), f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
