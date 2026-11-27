"""Write lean/Solution.lean from checks/certificate.json (exact, standard library only).

The 8008 dual vectors are integerized (y -> L*y). For each pair a < b of columns, a short
list D_a_b of codes covers every 6-subset {a < b < c < d < e < f}. A code is
mask + 2^16 * sum_i (y_i + 2) 5^i, where mask is the set of columns j with
7 (U^T y)_j >= 3 |y|_1."""
import itertools, json, sys
from fractions import Fraction as F
from math import lcm

cert_path, head_path, out_path = sys.argv[1:4]
d = json.load(open(cert_path))
U = [[1 if ch == "+" else -1 for ch in r] for r in d["U"]]
rows = [sum(1 << j for j, ch in enumerate(r) if ch == "+") for r in d["U"]]

def integer(y):
    L = 1
    for v in y:
        L = lcm(L, v.denominator)
    return [int(v * L) for v in y]

def mask(y):
    s = sum(abs(v) for v in y)
    return sum(1 << j for j in range(16) if 7 * sum(y[i] * U[i][j] for i in range(15)) >= 3 * s)

code_of = {}
for e in d["subset_certificates"]:
    y = integer([F(v) for v in e["y"]])
    assert all(-2 <= v <= 2 for v in y)
    m = mask(y)
    code_of.setdefault(m, m + (sum((v + 2) * 5 ** i for i, v in enumerate(y)) << 16))
masks = list(code_of)

chunks = {}
for a in range(16):
    for b in range(a + 1, 12):
        T = [(1 << a) | (1 << b) | sum(1 << j for j in s) for s in itertools.combinations(range(b + 1, 16), 4)]
        unc, D = set(T), []
        while unc:
            best = max(masks, key=lambda m: sum(1 for t in unc if m & t == t))
            D.append(code_of[best]); unc = {t for t in unc if best & t != t}
        chunks[(a, b)] = D

out = [open(head_path).read().rstrip() + "\n"]
out.append("/-! ## The matrix U and the certificate data -/\n")
out.append("/-- Row `i` of `U`, as a bit mask: bit `j` is set if and only if `U i j = 1`. -/")
out.append("def Urows : List ℕ := [" + ", ".join(map(str, rows)) + "]\n")
out.append(open(head_path.replace("head", "mid")).read())
for (a, b), D in chunks.items():
    out.append(f"def D_{a}_{b} : List ℕ :=\n  [" + ",\n   ".join(
        ", ".join(map(str, D[i:i + 6])) for i in range(0, len(D), 6)) + "]\n")
    out.append(f"theorem all_{a}_{b} : D_{a}_{b}.all valid = true := by decide +kernel\n")
    out.append(f"theorem any_{a}_{b} : ∀ c d e f : Fin 16, ({b} : Fin 16) < c → c < d → d < e → e < f →\n"
               f"    D_{a}_{b}.any (fun p => covers p {a} {b} c d e f) = true := by decide +kernel\n")
out.append(open(head_path.replace("head", "tail")).read())
# dispatch: interval_cases a <;> interval_cases b gives the 256 goals in order (a, b).
cases = []
for a in range(16):
    for b in range(16):
        if (a, b) in chunks:
            cases.append(f"  · exact fun _ c d e f h1 h2 h3 h4 => cover_of all_{a}_{b} (any_{a}_{b} c d e f h1 h2 h3 h4)")
        elif a >= b:
            cases.append("  · intro h; exfalso; simp [Fin.lt_def] at h")
        else:
            cases.append("  · intro _ c d e f h1 h2 h3 h4; exfalso; have := f.isLt; simp only [Fin.lt_def] at *; omega")
txt = "\n".join(out).replace("  -- CASES --", "\n".join(cases))
open(out_path, "w").write(txt)
print(len(chunks), sum(len(D) for D in chunks.values()), file=sys.stderr)
