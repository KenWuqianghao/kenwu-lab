"""Finite checks of PSQ and h(PSQ) with exact integer arithmetic.

Usage: python3 -I checks/prefix.py data/PSQ.txt [N_PSQ] [N_H]

1. Reads the 4-state Pell DFAO for PSQ.
2. Computes PSQ(0..N-1) in two ways and compares them:
   (a) from the greedy msd-first Pell representation of each n;
   (b) as the coding of the fixed point of the non-erasing substitution of the paper
       (Section 4): A(q) -> A(d(q,0)) C(d(q,1),d(q,2)),
       C(q,r) -> A(d(q,0)) C(d(q,1),d(q,2)) A(d(r,0)), coding A(q),C(q,r) -> out(q).
   It also compares (a) and (b) for 200 random 4-state Pell DFAOs (fixed seed).
3. PSQ(0..N_PSQ-1) has no square.
4. h(PSQ)(0..N_H-1) has largest exponent exactly 7/3; the first factor of exponent
   7/3 starts at position 8, length 7, period 3.
5. Controls: one changed letter of PSQ gives a square; the Thue-Morse prefix has
   largest exponent 2.
The last line is a JSON object with the numbers that ci.sh compares."""
import json
import random
import sys
from fractions import Fraction

import numpy as np

H = ["011010011001001101001", "100101100100110010110",
     "100101100110110010110", "011010011011001101001"]  # ARS Lemma 5


def load(path):
    lines = [l.split() for l in open(path) if l.strip()]
    assert lines[0] == ["msd_pell"]
    delta, out, q = {}, {}, None
    for l in lines[1:]:
        if "->" in l:
            delta[(q, int(l[0]))] = int(l[2])
        else:
            q = int(l[0])
            out[q] = int(l[1])
    return delta, out


def pell_rep(n):
    """Greedy msd-first representation over the weights 1, 2, 5, 12, 29, ..."""
    P = [1, 2]
    while P[-1] <= n:
        P.append(2 * P[-1] + P[-2])
    d = []
    for w in reversed(P):
        d.append(n // w)
        n -= d[-1] * w
    assert n == 0 and d[-1] in (0, 1)
    assert all(not (a == 2 and b != 0) for a, b in zip(d, d[1:]))
    return d


def word_greedy(delta, out, N):
    x = []
    for n in range(N):
        q = 0
        for c in pell_rep(n):
            q = delta[(q, c)]
        x.append(out[q])
    return x


def word_subst(delta, out, N):
    """Coding of the fixed point of the substitution, started at A(0)."""
    def sigma(letter):
        if letter[0] == "A":
            q = letter[1]
            return [("A", delta[(q, 0)]), ("C", delta[(q, 1)], delta[(q, 2)])]
        q, r = letter[1], letter[2]
        return [("A", delta[(q, 0)]), ("C", delta[(q, 1)], delta[(q, 2)]), ("A", delta[(r, 0)])]
    w = [("A", 0)]
    lengths = [1]
    while len(w) < N:
        w = [b for a in w for b in sigma(a)]
        lengths.append(len(w))
    assert lengths[:6] == [1, 2, 5, 12, 29, 70]
    return [out[a[1]] for a in w[:N]]


def longest_runs(z, pmax):
    """For each period p in 1..pmax: (r, start), r = longest run of z[j] == z[j-p]."""
    z = np.asarray(z, dtype=np.int8)
    res = {}
    for p in range(1, pmax + 1):
        eq = np.concatenate(([False], z[p:] == z[:-p], [False])).astype(np.int8)
        d = np.diff(eq)
        starts, ends = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
        if len(starts) == 0:
            res[p] = (0, None)
            continue
        k = int(np.argmax(ends - starts))
        res[p] = (int(ends[k] - starts[k]), int(starts[k]))  # factor starts at index starts[k]
    return res


def max_exponent(z):
    """Exact largest exponent of a factor of z, and the first such factor (start, length, period)."""
    best, wit = Fraction(1), None
    runs = longest_runs(z, len(z) // 2 + 1)
    for p, (r, s) in runs.items():
        e = Fraction(r + p, p)
        if e > best:
            best, wit = e, (s, r + p, p)
    return best, wit


def first_square(z):
    for p, (r, s) in longest_runs(z, len(z) // 2).items():
        if r >= p:
            return (s, p)
    return None


def first_at_least(z, e):
    """Smallest start of a factor with exponent >= e (scan of all periods)."""
    best = None
    z = np.asarray(z, dtype=np.int8)
    for p in range(1, len(z) // 2 + 1):
        need = int(np.ceil(e * p)) - p
        if need <= 0 or need > len(z) - p:
            continue
        eq = (z[p:] == z[:-p]).astype(np.int64)
        c = np.concatenate(([0], np.cumsum(eq)))
        ok = np.flatnonzero(c[need:] - c[:-need] == need)
        if len(ok):
            s, L = int(ok[0]), need + p
            if best is None or (s, L, p) < best:
                best = (s, L, p)
    return best


def main():
    path = sys.argv[1]
    n_psq = int(sys.argv[2]) if len(sys.argv) > 2 else 50000
    n_h = int(sys.argv[3]) if len(sys.argv) > 3 else 200000
    delta, out = load(path)
    assert delta[(0, 0)] == 0
    res = {}

    y = word_greedy(delta, out, max(n_psq, 100000))
    ys = word_subst(delta, out, len(y))
    res["subst_equals_greedy_letters"] = len(y) if ys == y else -1
    rng = random.Random(20261127)
    agree = 0
    for _ in range(200):
        d = {(q, c): rng.randrange(4) for q in range(4) for c in range(3)}
        d[(0, 0)] = 0
        o = {q: rng.randrange(2) for q in range(4)}
        agree += word_greedy(d, o, 3000) == word_subst(d, o, 3000)
    res["random_dfaos_agree"] = agree
    res["psq_prefix60"] = "".join(map(str, y[:60]))
    print("PSQ prefix:", res["psq_prefix60"])
    print("substitution route = greedy route on", res["subst_equals_greedy_letters"], "letters")
    print("random 4-state DFAOs where both routes agree (3000 letters):", agree, "of 200")

    y = y[:n_psq]
    res["psq_square_free_prefix"] = n_psq if first_square(y) is None else -1
    print("first square in PSQ prefix of length", n_psq, ":", first_square(y))

    z = [int(c) for a in y for c in H[a]][:n_h]
    e, wit = max_exponent(z)
    res["h_prefix_length"] = n_h
    res["h_max_exponent"] = f"{e.numerator}/{e.denominator}"
    first73 = first_at_least(z[:1000], Fraction(7, 3))
    res["h_first_73_factor"] = list(first73)
    res["h_prefix24"] = "".join(map(str, z[:24]))
    print("largest exponent in h(PSQ) prefix of length", n_h, ":", e, "first factor with it:", wit)
    print("first factor of exponent >= 7/3 (start, length, period):", first73)

    bad = list(y)
    bad[n_psq // 2] = (bad[n_psq // 2] + 1) % 4
    res["control_changed_letter_square"] = first_square(bad) is not None
    tm = [bin(n).count("1") % 2 for n in range(20000)]
    et, _ = max_exponent(tm)
    res["control_thue_morse_max_exponent"] = f"{et.numerator}/{et.denominator}"
    print("control: PSQ with one changed letter has a square:", res["control_changed_letter_square"])
    print("control: largest exponent in Thue-Morse prefix of length 20000:", et)
    print(json.dumps(res, sort_keys=True))


if __name__ == "__main__":
    main()
