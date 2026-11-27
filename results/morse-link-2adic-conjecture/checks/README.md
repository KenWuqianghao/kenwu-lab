# Checking guide

Run every command from the result folder. All arithmetic is exact (Python integers). The Python checks use only the standard library.

| Command | What it checks | Time (one M1 Pro core) |
|---|---|---|
| `python3 -I checks/certificate.py` | The certificate (below) | about 1 s |
| `python3 -I checks/verify_k2.py` | The solver's checker: L^(2)_n by three methods, the values at n = 2, 3, 4, 19, and the first proof (with n = 4) | about 4 s |
| `python3 -I checks/independent_check.py` | The verifier's checker, written without reading the solver's code: d(n) for k = 1, 2 and n ≤ 40, and the feasible c for n ≥ 2 and n ≥ 4 | < 1 s |
| `python3 -I checks/survey.py 200 24` | The survey of Section 5 for k ≤ 24, n ≤ 200; output equals `data/survey_N200_K24.txt` | about 17 s |
| `python3 -I checks/fit.py` | The 2-adic digits of the fits in Section 5 | < 1 s |
| `bash checks/ci.sh` | All of the above, the numbers in `paper/paper.tex`, and the pattern in the survey file | about 30 s |
| `lake env lean lean/GaoGu412.lean` (from a Lean project on Mathlib v4.36.0) | The Lean theorems and their axioms | about 3 min |

## The certificate (`certificate.py`)

1. It computes L^(2)_n = C^b_n with b(x) = (2x+1)⁴ and C_n by the height recursion f₀(h) = [h = 0], f_{m+1}(h) = b(h) f_m(h+1) + f_m(h−1), C^b_n = f_{2n}(0). It compares the recursion with brute-force enumeration of all Dyck paths for n ≤ 10.
2. It compares L, C, ξ₂(L − C), the odd part, s₂(n) and d(n) = ξ₂(L − C) − s₂(n) at n = 2, 3, 4, 19 with `data/expected.json`.
3. It tests every residue of α modulo 2¹² and every c ≤ 3 at n = 2, 3, 19, and finds no solution. The test is exhaustive: c > 3 fails at n = 2, and for c ≤ 3 the identity needs ξ₂(n − α) ≤ 11 at these n, so α mod 2¹² decides it.
4. It checks Remark 3 of the paper: n = 2, 3 force c = 3 and α ≡ 3 + 2⁸ (mod 2⁹), and then the first failing index is n = 19.
5. Positive control: for k = 1 and c = 2, residues of α fit all 2 ≤ n ≤ 40, as Postnikov's conjecture predicts.

## The survey (`survey.py`, `consistency.py`, `explore_lib.py`)

For each k and each parity of α, the values of d at the indices of the other parity must all equal c. At the indices of the same parity, the conditions α ≡ n + 2^m (mod 2^(m+1)) with m = d(n) − c must agree. This test is exact for the finite range. The results for other k are observations for k ≤ 24 and n ≤ 200 only. They are not proved.

## Lean

`lean/GaoGu412.lean` imports only Mathlib. It defines Dyck paths as lists of steps, the weight, `weightedCatalan`, `L`, `C`, the binary digit sum `s2` and `Conjecture412 k`, as in the source. It proves `GaoGu.conjecture_4_12_false_k2 : ¬ Conjecture412 2` and `GaoGu.conjecture_4_12_false : ¬ ∀ k, 0 < k → Conjecture412 k`. The proof derives the height recursion from the path definition by induction, evaluates it with a list of 40 heights, and checks the three valuations with `decide +kernel` (kernel reduction; no `native_decide`). The file ends with `#print axioms`, which prints `[propext, Classical.choice, Quot.sound]`. `lean/Challenge.lean` repeats the definitions and the statements with `sorry`; `lake comparator` with `lean/comparator.json` checks that the proof file proves exactly these statements.

The Python programs are not formally verified. The Lean proof does not depend on them.
