"""Parse one Lichess monthly PGN.zst into fixed 40-ply token keys.

Usage: python -I parse_month.py IN.pgn.zst OUT.npz

Output arrays (one row per game with at least one move):
  tok   (n, 40) uint16  month-local token id per ply, 0 = no move (game ended)
  L     (n,)    uint8   number of plies, capped at 40
  speed (n,)    uint8   0 bullet, 1 blitz, 2 classical, 3 correspondence, 4 other
  elo   (n,)    uint16  mean of WhiteElo and BlackElo (0 if one is missing)
  vocab (V,)    str     SAN string of token id k is vocab[k-1]
SAN suffixes "!" and "?" are removed; "+" and "#" are kept. Comments in braces are removed.
"""
import re
from array import array
import subprocess
import sys

import numpy as np

D = 40
COMMENT = re.compile(r"\{[^}]*\}")
RESULTS = {"1-0", "0-1", "1/2-1/2", "*"}
PAD = [0] * D
SPEEDS = {"Bullet": 0, "Blitz": 1, "Classical": 2, "Correspondence": 3}


def main(inp, out):
    z = subprocess.Popen(["zstd", "-dc", inp], stdout=subprocess.PIPE)
    p = subprocess.Popen(["grep", "-E", r"^(\[Event |\[WhiteElo |\[BlackElo |1\. )"], stdin=z.stdout,
                         stdout=subprocess.PIPE, bufsize=1 << 20, env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"})
    z.stdout.close()
    vocab = {}
    toks, Ls, speeds, elos = array('H'), array('B'), array('B'), array('H')
    speed, we, be = 4, 0, 0
    for raw in p.stdout:
        c = raw[:1]
        if c == b"[":
            if raw.startswith(b"[Event "):
                ev = raw.decode("utf-8", "replace")
                speed = 4
                for k, v in SPEEDS.items():
                    if k in ev:
                        speed = v
                        break
                we = be = 0
            elif raw.startswith(b"[WhiteElo "):
                s = raw[11:-3]
                we = int(s) if s.isdigit() else 0
            elif raw.startswith(b"[BlackElo "):
                s = raw[11:-3]
                be = int(s) if s.isdigit() else 0
            continue
        if not raw.startswith(b"1. "):
            continue
        line = (raw if b"{" in raw else raw[:700]).decode("utf-8", "replace")
        if "{" in line:
            line = COMMENT.sub(" ", line)
        row = []
        for t in line.split():
            if "." in t or t in RESULTS:
                continue
            t = t.rstrip("!?")
            i = vocab.get(t)
            if i is None:
                i = len(vocab) + 1
                vocab[t] = i
            row.append(i)
            if len(row) == D:
                break
        n = len(row)
        if n == 0:
            continue
        Ls.append(n)
        toks.extend(row)
        if n < D:
            toks.extend(PAD[: D - n])
        speeds.append(speed)
        elos.append((we + be) // 2 if (we and be) else 0)
    p.wait()
    z.wait()
    if z.returncode or p.returncode not in (0, 1):
        raise SystemExit("zstd or grep failed")
    if len(vocab) >= 65535:
        raise SystemExit("vocabulary too large for uint16")
    v = [None] * len(vocab)
    for k, i in vocab.items():
        v[i - 1] = k
    np.savez(out, tok=np.frombuffer(toks, dtype=np.uint16).reshape(-1, D), L=np.frombuffer(Ls, np.uint8),
             speed=np.frombuffer(speeds, np.uint8), elo=np.frombuffer(elos, np.uint16), vocab=np.array(v))
    print(inp, len(Ls), "games", len(vocab), "tokens")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
