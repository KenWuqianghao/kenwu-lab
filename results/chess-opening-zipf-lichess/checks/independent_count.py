"""Independent count (written by the verifier, round 2) of the shallow tree (depth 1..DMAX) on all 36 months.

Usage: python -I independent_count.py RAW_DIR TMP_DIR OUT.json
Does not use the solver's parser, sort/LCP code, or estimator.
Reads the raw PGN text, takes SAN moves with a regular expression, hashes each d-ply prefix to 64 bits (process-independent hash),
counts node weights per depth with numpy.unique over all months, and fits alpha_d with a
log-binned least-squares estimator written from PROTOCOL.md section 3.
"""
import glob, hashlib, json, math, os, re, subprocess, sys
from array import array
import numpy as np

DMAX = 12
SAN = re.compile(r"(?:O-O(?:-O)?|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?)[+#]?$")
COMMENT = re.compile(r"\{.*?\}")
MASK = (1 << 64) - 1
TOK = {}

def month(path, out):
    z0 = subprocess.Popen(["zstd", "-dc", path], stdout=subprocess.PIPE)
    z = subprocess.Popen(["grep", "-v", "-E", r"^(\[|[[:space:]]*$)"], stdin=z0.stdout, stdout=subprocess.PIPE, text=True,
                         encoding="utf-8", errors="replace", env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"})
    z0.stdout.close()
    rows = array('Q'); nrow = 0; odd = 0; nomove = 0
    for line in z.stdout:
        if line[:1] == "[" or not line.strip():
            continue
        if "{" in line:
            line = COMMENT.sub(" ", line)
        hs = []; h = 1469598103934665603
        for t in line.split(None, 4 * DMAX)[:4 * DMAX]:
            if t[0].isdigit() or t == "*":
                continue
            t = t.rstrip("!?")
            if not SAN.match(t):
                odd += 1
                continue
            ti = TOK.get(t)
            if ti is None:
                ti = TOK[t] = int.from_bytes(hashlib.blake2b(t.encode(), digest_size=8).digest(), "little")
            h = ((h ^ ti) * 1099511628211 + 0x9E3779B97F4A7C15) & MASK
            h ^= h >> 29
            hs.append(h)
            if len(hs) == DMAX:
                break
        if not hs:
            nomove += 1
            continue
        rows.extend(hs + [0] * (DMAX - len(hs))); nrow += 1
    if z.wait() not in (0, 1) or z0.wait():
        raise SystemExit("zstd or grep failed " + path)
    H = np.frombuffer(rows, dtype=np.uint64).reshape(-1, DMAX)
    np.save(out, H)
    return nrow, odd, nomove

def alpha(v, c, N):
    edges = []
    k = 0
    while True:
        e = int(math.floor(2 ** (k / 2)))
        if not edges or e != edges[-1]:
            edges.append(e)
        if e > 2 * N:
            break
        k += 1
    xs, ys = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        if hi - 1 > N / 100:
            continue
        cnt = int(c[(v >= lo) & (v < hi)].sum())
        if cnt < 5:
            continue
        xs.append(math.log10(math.sqrt(lo * (hi - 1)))); ys.append(math.log10(cnt / (hi - lo)))
    if len(xs) < 4:
        return float("nan")
    xs, ys = np.array(xs), np.array(ys)
    xm, ym = xs.mean(), ys.mean()
    return float(-((xs - xm) * (ys - ym)).sum() / ((xs - xm) ** 2).sum())

def main(raw, tmp, out):
    files = sorted(glob.glob(os.path.join(raw, "*.pgn.zst")))
    assert len(files) == 36, len(files)
    tot = 0; meta = {}
    for f in files:
        o = os.path.join(tmp, os.path.basename(f)[:-8] + ".npy")
        if not os.path.exists(o):
            n, odd, nm = month(f, o + ".tmp.npy"); os.rename(o + ".tmp.npy", o)
            print(os.path.basename(f), n, odd, nm, flush=True)
            meta[os.path.basename(f)] = [n, odd, nm]
    res = {"per_month": {}, "alpha_d": {}, "n_nodes": {}, "n_games_ge_d": {}}
    arrs = [np.load(os.path.join(tmp, os.path.basename(f)[:-8] + ".npy"), mmap_mode="r") for f in files]
    for f, a in zip(files, arrs):
        res["per_month"][os.path.basename(f)] = int(a.shape[0])
    N = sum(a.shape[0] for a in arrs); res["N"] = int(N); res["odd_nomove"] = meta
    ad = {}
    for d in range(1, DMAX + 1):
        cp = os.path.join(tmp, f"depth_{d}.npz")
        if not os.path.exists(cp):
            col = np.concatenate([np.asarray(a[:, d - 1]) for a in arrs])
            col = col[col != 0]
            _, w = np.unique(col, return_counts=True)
            del col
            np.savez(cp + ".tmp.npz", w=w); os.rename(cp + ".tmp.npz", cp)
        w = np.load(cp)["w"]
        v, c = np.unique(w, return_counts=True)
        ad[d] = alpha(v, c, N)
        res["alpha_d"][d] = ad[d]; res["n_nodes"][d] = int(len(w)); res["n_games_ge_d"][d] = int(w.sum())
        print(d, len(w), int(w.sum()), ad[d], flush=True)
    dcr = float("nan")
    for d in range(2, DMAX + 1):
        if ad[d] >= 2:
            dcr = (d - 1) + (2 - ad[d - 1]) / (ad[d] - ad[d - 1]); break
    res["d_cr"] = dcr
    json.dump(res, open(out, "w"), indent=1)
    print("N", N, "d_cr", dcr)

main(*sys.argv[1:4])
