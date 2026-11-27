# Numbers in the paper and their sources

Check outputs: `checks/expected/check.txt` and `checks/expected/extra.txt` (each equal to
a fresh run by `bash checks/ci.sh`), and the output of `vcheck.py --lp` (printed by
`ci.sh`). "Lean" names a theorem of `lean/Solution.lean`.

| Number in the paper | Source |
|---|---|
| n = 16, t = 6 | `checks/certificate.json` (`t`); `check.txt` ("(n=16, t=6)"); Lean `conjecture2_false : ¬ Conjecture2 4` (2^4 = 16) and `maxValD … 6` |
| max val_D(U_6) = −3/7 (upper bound) | `check.txt`; `vcheck.py` item 4; Lean `U_bound` |
| max val_D(U_6) = −3/7 (equality), S = {0,1,2,3,4,12}, w = (1,1,1,1,1,2)/7 | `extra.txt` line 3; `vcheck.py` item 7 (S = (0, 1, 2, 3, 4, 12), exact 3/7) |
| max val_D(Ĥ_6) ≥ −1/3, S₀ = {0,1,2,4,8,15}, uniform w | `check.txt`; `vcheck.py` item 3; Lean `H_bound`, `Hh_S0` |
| Row sums 1 + (4 − 2\|r\|) + (−1)^\|r\| = ±2 | `extra.txt` line 4 |
| 0.333333 (floating-point min over S for Ĥ at t = 6) | `vcheck.py` item 8 (0.3333333333333333) |
| 8008 = C(16,6) certificates | `checks/certificate.json`; `vcheck.py` item 4; `check.py` (assert) |
| Scaled entries in {−2,…,2}; 840 vectors with one nonzero entry; at most six nonzero entries | `checks/certificate.json` (count by `ci.sh`, which checks the sentence in `paper.tex`); `make_lean.py` asserts the range |
| 0 failures of the own LP duals | `vcheck.py` item 6 |
| 66 pairs, 2222 list entries | `make_lean.py` (stderr "66 2222"; `ci.sh` checks the sentence in `paper.tex`) |
| U = Had.16.3 without row 0; [1ᵀ; U] is a Hadamard matrix | `extra.txt` lines 1-2; `vcheck.py` item 1 ("[1;U] is Hadamard: True") |
| The 15 rows of U in the table | `checks/certificate.json` (`U`; `ci.sh` checks the table in `paper.tex`) |
| Five Hadamard matrices of order 16 up to equivalence (Had.16.0 to Had.16.4) | Sloane's library page, http://neilsloane.com/hadamard/ ("The five distinct Hadamard matrices of order 16") |
| Floating-point scan: 0.333333 for Had.16.0, .1, .2 and 0.428571 for Had.16.3, .4, all 16 rows | verify stage, problem folder `checks/verify/scan_t6_a.out` and `scan_t6_b.out` (80 lines; produced by `checks/verify/scan_t6.py`) |
| Source verified n = 2, 4, 8 and t ≤ n, and n − 2 ≤ t ≤ n; Theorem bound √(1/(2t)) for 1 ≤ t ≤ n/2 | source PDF http://proceedings.mlr.press/v30/Nie13.pdf, page 3 (`pdftotext -layout`) |
| PMLR 30:1076–1079; 26th COLT | https://proceedings.mlr.press/v30/Nie13.html (`citation_firstpage` 1076, `citation_lastpage` 1079, `citation_conference_sequence_num` 26) |
| One citing work in OpenAlex | `PRIOR_ART.md`; OpenAlex record W146899193 (`cited_by_count` 1, rechecked 2026-11-27) |
| arXiv:1901.10789 (2019) | arXiv API record (published 2019-01-30) |
| CADE 28, pages 625–635, 2021 | Crossref record of doi:10.1007/978-3-030-79876-5_37 |
| CPP 2020 | Crossref record of doi:10.1145/3372885.3373824 |
| Lean: compiles in about 20 minutes, up to about 6 GB | `lake env lean lean/Solution.lean` in the shared workspace under `run-heavy` with a 6 GB cap: real 19m47.7s, user 17m58.7s, exit 0. A first version with one kernel evaluation over all sets was stopped by a 4 GB cap. |
| Lean axioms: propext, Classical.choice, Quot.sound; lake comparator accepts | `bin/lean-compare lean` (real 38m16s, exit 0): `'HadamardBoosting.conjecture2_false' depends on axioms: [propext, Classical.choice, Quot.sound]`, `Lean default kernel accepts the solution`, `Your solution is okay!`; `bin/lean-audit lean/Solution.lean` (real 19m2.9s): `PASS lean/Solution.lean: 388 declarations, no project axioms` |
| 3 s (`check.py`), 36 s (`vcheck.py --lp`) | measured on the Steam Deck: verify stage 3.0 s for `check.py`; `vcheck.py --lp` real 35.8 s |

## Issues left open by VERIFY.md (round 1) and where the paper fixes them

| Issue | Fix |
|---|---|
| 1. State the Sylvester reading of "the n × n Hadamard matrix"; the title must not claim more. | Title names the Sylvester–Hadamard matrix. Section 2, paragraph "The Hadamard matrix"; Theorem 1 says "let H be the Sylvester Hadamard matrix"; Remark 1 (readings "every" and "some"); Section 6, first item; abstract, last sentence before the disclaimer; Lean `sylvester`, `hhat` and `STATEMENT.md`. |
| 2. Use the full t = 6 scan (all 16 rows of Had.16.3 and Had.16.4 give 3/7), marked as floating point, or omit it. | Remark 1 gives the full scan result for all 5 classes and 16 rows and marks it "in floating point … information only". The partial-scan sentence of `RESULT.md` is not used. |
| 3. State max val_D(U_6) = −3/7 exactly; say "≥ −1/3" for Sylvester or mark equality as floating point. | Theorem 1 states "≥ −1/3 > −3/7 =". Section 3, paragraph "The upper bound for U", last paragraph (equality case). Section 3, paragraph "The Sylvester side": equality 0.333333 is marked as floating point. |
| 4. Say that the result is computer-assisted with exact arithmetic and has no Lean check; state the limits of the citation search. | Superseded in part: this stage added a Lean proof (Section 4), so the tier is "Proved in Lean". Section 5 lists the exact Python checks. Section 6, item "Novelty": Semantic Scholar HTTP 429, OpenAlex one citing work, Google Scholar not searched, thesis not readable. |

## Reruns from a clean copy (2026-11-27)

`release/` copied to `$TMPDIR/colt-ci2/colt-hadamard-boosting-gap`, new venv (Python 3.13):

- `python3 /home/deck/research/factory/lab-repo/tools/check_result.py <copy>`: `ok: 1 result(s)`.
- `bash checks/ci.sh`: exit 0, real 1m25.7s; last lines `make_lean: output equals lean/Solution.lean (66 pairs, 2222 list entries)`, `figures equal a fresh drawing`, `paper numbers match the check output`, `ci.sh: all checks passed`.
- `python3 -I checks/check.py checks/certificate.json`: the two lines of `checks/expected/check.txt`, real 2.0 s.
- `python3 -I checks/check_extra.py checks/certificate.json checks/had.16.3.txt`: the four PASS lines of `checks/expected/extra.txt`, real 0.05 s.
- Negative controls: one changed certificate entry makes `check.py` fail (`AssertionError: (0, 1, 2, 4, 9, 10)`); a changed number in `paper.tex` (2223 for 2222) makes `ci.sh` fail (`missing in paper.tex: …`).
