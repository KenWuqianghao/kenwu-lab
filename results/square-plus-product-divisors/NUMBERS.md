# Numbers in the paper and their sources

Paths without a prefix are in this folder. Paths that start with `project:` are in the factory project repository (`problems/square-plus-product-divisors`). `<factory>` is the factory root.

| Number in the paper | Value | Source |
|---|---|---|
| S(N) for N = 6, 14, …, 118 (Table 1, README) | 4, 8, 16, 16, 16, 32, 28, 20, 40, 32, 36, 52, 40, 32, 52 | `checks/check_statement.py 3000` (`checks/expected/statement.txt`); `ci.sh` checks the table rows in `paper.tex` |
| Control: S(N) mod 4 at N = 2, 10, 18, 26 | 1, 0, 3, 2 | `checks/check_statement.py`; `project:checks/RUN.md` (sprint run) |
| Classes mod 16 with S(N) ≡ 0 (mod 4) for all 1 ≤ N ≤ 3000 | 6 and 14 only | `checks/check_statement.py` (residue table) |
| Direct check | 375 values N ≡ 6 (mod 8), N ≤ 3000, 0 failures | `checks/check_statement.py 3000`; `project:VERIFY.md` check 7 (verifier's own code, N < 3000) |
| Step-by-step check | 500 values N ≡ 6 (mod 8), N ≤ 4000, 0 failures | `checks/check_lean_route.py 4000`; `project:VERIFY.md` check 8 |
| Sieve | N ≤ 3·10⁶; 187 500 values in each class 6, 14 (mod 16); 0 failures | `checks/sieve.py 3000000` (write session; same counts as the sprint C sieve in `project:checks/RUN.md`: `tested=187500 bad=0` for 16n + 6) |
| Classes mod 16, 32, 64 to 3·10⁵ | exactly the B with B ≡ 6 (mod 8) | `checks/sieve.py`; the sprint C sieve reported the same (`project:checks/RUN.md`) |
| ν2 check | N ≡ 6 (mod 8), N ≤ 700, 0 failures | `checks/check_nu2.py 700`; `project:checks/RUN.md` |
| σ1(N)/2 ≡ 0 (mod 4) for N ≡ 14 (mod 16) | hand proof in Section 4; 0 failures for N ≤ 3000 | `checks/check_statement.py` |
| Example N = 22 | \|X\| = 16, X1< = {(1,1,21),(1,3,7),(3,1,13)}, \|X1\| = 6, \|Z\| = 7, F = 1 at (3,3,1,1), Xb has 5 points, \|X0\| = 10, fixed point (2,3,6) | `checks/check_statement.py`; `ci.sh` checks each value in `paper.tex` |
| Pairs (A, B) of Theorem 1 of the source; N < 100,000 | (16,14), (36,30), (72,42), (196,70), (252,114) | `project:work/src/2604.25394.txt` (arXiv v1 text); `project:STATEMENT.md`; `project:VERIFY.md` check 1 |
| Keith's progressions (36,30), (72,42), (196,70), (252,114) | — | `project:work/src/keith.txt` (arXiv:1502.00366v4, Theorem 1) |
| Lean file length; declarations | 492 lines; 151 declarations | `wc -l lean/Solution.lean`; `lean-audit` output (below) |
| Lean axioms | [propext, Classical.choice, Quot.sound] for both theorems | `#print axioms` in the write-session compile (below) |
| Lean compile time | about 1 min (41 s measured) | write-session run (below) |
| Check times (README, `checks/README.md`) | about 10 s, 9 s, < 1 s, 25 s; `ci.sh` about 1 min (61 s and 51 s measured) | write-session runs on the Steam Deck |
| Number of pages | 6 | `pdfinfo paper/paper.pdf` |

## Open issues of the last VERIFY.md (round 2) and where they are fixed

| Issue | Fix |
|---|---|
| 1. Paths in `RESULT.md` and `checks/RUN.md` are for another machine; the recorded times are the solver's run. | `project:RESULT.md` and `project:checks/RUN.md` now write `<factory>/…` and say that their times are from the MacBook runs of the sprint and solve sessions. The release uses only paths relative to the result folder (README "Check it", `checks/README.md`). The write-session times on the Steam Deck are below. |
| 2. Scope of novelty: the new part is N ≡ 6 (mod 16); N ≡ 14 (mod 16) is the (16, 14) case of Theorem 1 of the source; the ν2 consequence depends on Theorem 4 of the source, not checked, not in Lean. | Abstract ("The class N ≡ 14 (mod 16) is their case (16, 14), so for that class our proof is a new proof of a known result"; "This consequence is not checked in Lean"); Section 1 "Result"; Section 4, last paragraph; Section 6 (Limits), items 2 and 3; README "Result". |
| 3. Appendix A (Jacobi route) is not machine-checked; keep it apart or omit it. | Omitted. Remark 5 says only that a first proof used Jacobi's four-square formula, that it is not checked in Lean, and that the paper does not give it. `check_proof.py` and `verify_independent.py`, which check that route, are not in the release. |
| 4. The "Theorem 386" citation of Hardy–Wright is not confirmed. | Moot: the paper does not cite Hardy–Wright and gives no theorem number for Jacobi's formula. |

## References: how each one was confirmed

| Reference | Confirmation |
|---|---|
| Jirattikansakul et al., arXiv:2604.25394v1 | Full text read (`project:work/src/2604.25394.txt`); abs and HTML pages fetched in verify rounds 1 and 2. |
| Keith, IJNT 13 (2017) 229–241; arXiv:1502.00366v4 | Full text read (`project:work/src/keith.txt`); journal data from Crossref (`api.crossref.org/works/10.1142/S1793042117500130`) in the write session. |
| DeWitt–Keith, arXiv:2507.13566v1; IJNT 22 (2026) 1075–1084 | Full text read (`project:work/src/dk.txt`); journal data from Crossref (10.1142/S1793042126500569). |
| Hooley, Math. Z. 69 (1958) 211–227 | Cited in the source; title, journal, volume, pages and DOI 10.1007/BF01187402 from Crossref. The paper uses it only for the remark that the source attributes to it. |
| Zagier, Amer. Math. Monthly 97 (1990) 144 | Crossref (10.2307/2323918): title, journal, volume 97, issue 2, page 144. The involution formula was compared with the Wikipedia article "Fermat's theorem on sums of two squares" (revision 1379511825); the paper's case conditions x + z < y and y < x + z are the same as x < y − z and y − z < x. The Lean proof checks the involution directly. |
| Lean, Mathlib | Project URLs. |

## Write-session runs (2026-11-27, Steam Deck)

- `cd <factory>/lean && run-heavy 1800 lake env lean …/release/lean/Solution.lean`: 41 s; output `'sum_card_divisors_mod_four' depends on axioms: [propext, Classical.choice, Quot.sound]` and `'conjecture_7' depends on axioms: [propext, Classical.choice, Quot.sound]`; exit 0.
- `run-heavy 2400 <factory>/bin/lean-audit …/release/lean`: `PASS …/release/lean/Solution.lean: 151 declarations, no project axioms`, 37 s, exit 0.
- `run-heavy 3600 <factory>/bin/lean-compare …/release/lean`: `Lean default kernel accepts the solution`, `Your solution is okay!`, 2 min 52 s, exit 0.
- `diff -r` of the clean copy's `lean/` and `project:lean/`: identical.
- Clean copy: `git clone` of the project at commit ba8a772, `release/` copied to `$TMPDIR/write-spd/square-plus-product-divisors`, new venv (Python 3.13): `bash checks/ci.sh` ends with `ci.sh: all checks passed` (51 s).
- Negative control: with one value of Table 1 changed (36 → 37) in `paper.tex`, `ci.sh` prints `missing in paper.tex: $S(N)$ & 40 & 32 & 36 & 52 & 40 & 32 & 52 & \\` and exits 1.
- "Check it" commands in the clean copy: `check_statement.py 3000` prints `N=6 mod 8, N<=3000: 375 values, failures: 0`; `check_lean_route.py 4000` prints `checked 500 values N=8n+6 <= 4000; failures: 0 []`.
- `python3 <factory>/lab-repo/tools/check_result.py $TMPDIR/write-spd/square-plus-product-divisors`: `ok: 1 result(s)`.
- The PDF was built with Tectonic 0.15.0 (`tectonic -X compile paper.tex`), because this machine has no `latexmk`. The build gives no TeX warnings.
