"""Shared helpers for the checks: the value t by the turn identity, the Odd Sum test, list readers.

Turn identity (positions 0-indexed, n = len(p)):
  t(p) = sum_{m=3}^{n} C(n, m) + sum_{a<b<c} turn(a, b, c) * 2^a * 2^(n-1-c),
where turn(a, b, c) = 1 if p[b] is larger than both p[a], p[c] or smaller than both.
The paper proves this identity (Lemma 1); checks/validate_bb.py and checks/check_lists.py compare it
with the definition of Ahmed and Snevily (checks/t_definition.py)."""
from math import comb


def t_turn(p):
    n = len(p)
    s = sum(comb(n, m) for m in range(3, n + 1))
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                if (p[b] > p[a]) == (p[b] > p[c]):
                    s += (1 << a) * (1 << (n - 1 - c))
    return s


def odd_sum(p):
    """Conjecture 2.4 condition: for n = 2k+1, p_j + p_{n-j+1} odd for 1 <= j <= k;
    for n = 2k, p_j + p_{n-j+1} = 2k + 1 for 1 <= j <= k."""
    n = len(p)
    if n % 2:
        return all((p[j] + p[n - 1 - j]) % 2 == 1 for j in range(n // 2))
    return all(p[j] + p[n - 1 - j] == n + 1 for j in range(n // 2))


def complement(p):
    return tuple(len(p) + 1 - v for v in p)


def read_list(path):
    """A data list: one permutation per line, entries separated by spaces; '#' lines are comments."""
    return [tuple(map(int, line.split())) for line in open(path) if line.strip() and not line.startswith("#")]


def read_obb(text, n):
    """Permutations of length n that oddsum_bb.c prints after its 'BEGIN n=<n>' line."""
    out, live = [], False
    for line in text.splitlines():
        if line.startswith("BEGIN"):
            live = line.startswith(f"BEGIN n={n} ")
        elif line.startswith("ML[") or line.startswith("=="):
            live = False
        elif live and line.startswith("t="):
            a, b = line.split()
            out.append((int(a[2:]), tuple(map(int, b.split(",")))))
    return out


def read_v2(text):
    """Permutations that independent/v2_bb.c prints ('PERM t=<t> : v1 v2 ...')."""
    out = []
    for line in text.splitlines():
        if line.startswith("PERM"):
            out.append((int(line.split()[1][2:]), tuple(map(int, line.split(":")[1].split()))))
    return out


def summary(text):
    """The key=value fields of the SUMMARY lines."""
    rows = []
    for line in text.splitlines():
        if line.startswith("SUMMARY"):
            rows.append(dict(f.split("=", 1) for f in line.split()[1:]))
    return rows
