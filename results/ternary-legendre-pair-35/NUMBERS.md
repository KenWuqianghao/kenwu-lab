# Numbers in the paper and their sources

Paths without a prefix are in this folder. Paths that start with `project:` are in the factory project repository (`problems/ternary-legendre-pair-35`), which holds the full records.

## Length 35

| Number in the paper | Value | Source |
|---|---|---|
| Exponent word A | `02021220020100021222201110110121211` | `data/lp35.txt`; `lean/TernaryLP35.lean` (`eA`); `checks/check.py` item 1 |
| Exponent word B | `01222010111021021121200221100200122` | `data/lp35.txt`; `lean/TernaryLP35.lean` (`eB`); `checks/check.py` item 1 |
| Combined counts at every lag s = 1..34 | (22, 24, 24) | `checks/check.py`; Lean lemma `counts_ok` |
| Composition of each word | (11, 12, 12) | `checks/check.py` |
| Component sum | −1 = 11 + 12ξ + 12ξ² | arithmetic from the composition |
| h for ℓ = 35 | 12 (ℓ = 3h − 1) | arithmetic |
| Multiplier | j ↦ 6j (mod 35); not invariant under j ↦ −j | `checks/check.py` |
| Fixed points of ×6 | 0, 7, 14, 21, 28; all entries 0 there | `data/lp35.txt` (entries 0, 7, 14, 21, 28 of A and B); figure |
| Orbits of ⟨6⟩ | 5 of size 1, 15 of size 2 (20 in total) | `checks/search/orbits.py 35 6` (prints `35 20`) |
| ⟨34⟩ | 5 717 712 words, 0 pairs | `RESULT.md`; VERIFY check 11; ci run (below) |
| ⟨6⟩ | 42 042 000 words, 2400 ordered pairs | `project:search/run_35_H6.log`; VERIFY check 10; ci run |
| ⟨29⟩ | 130 162 032 words, 0 pairs | VERIFY issue 2 (verifier run); write-stage rerun `project:search/write_reruns/run_35_H29.log` (286 s, 2.08 GB); ci run |
| ⟨11⟩, ⟨8⟩, ⟨13⟩, ⟨3⟩ | 87 150; 14 840; 1 400; 2 words; 0 pairs each | `RESULT.md`; VERIFY check 11; ci run |
| Run time of ⟨6⟩ | about 85 s | `project:search/run_35_H6.log` (84.85 s); write-stage run 96 s |
| Subgroups of Z₃₅* other than {1} | 15; each contains ⟨34⟩, ⟨6⟩, ⟨29⟩ or ⟨11⟩; only ⟨6⟩ contains none of ⟨34⟩, ⟨29⟩, ⟨11⟩ | `checks/check.py` item 6 |
| Lean axioms | [propext, Classical.choice, Quot.sound] | `#print axioms` output; write-stage run below |
| Lean run times | 151 s, 60 s, 56 s | `project:checks/RUNS.md` (solver); VERIFY check 4; write-stage run |
| Mutation tests in Lean | 2, both rejected by `decide` | `project:checks/RUNS.md` section 3; VERIFY check 6 |
| Floating-point cross-check error | 7.3e−15 | `checks/check_pair_zw.py` output |
| Single-entry changes rejected | 140 of 140 | `checks/check.py` |
| Source pairs accepted | lengths 5, 11, 14, 17, 20, 23, 29, 32 | `checks/check.py`; pairs copied from `project:source/2611.31067v1.txt` |

## Facts quoted from the source (arXiv:2611.31067v1)

| Fact | Place in the source |
|---|---|
| ℓ ≡ −1 (mod k) for prime k | Theorem 1 |
| Composition (h − 1, h, h) after normalization | Theorem 4 and Section 4 |
| H(2p, 2ℓ + 2) from every p-ary pair | Corollary 6 |
| m-sequence lengths 3^r − 1 (2, 8, 26) | Section 2.3 and Section 4 |
| Pairs of lengths 5, 11, 14, 17, 20, 23, 29, 32 | Section 4, Appendix A |
| Half-frequency cases at ℓ = 38: (3,75), (21,57), (39,39) | Section 4.4 |
| Smallest undecided binary length 115 | Section 1 |
| "The smallest open cases are then ℓ = 35 and ℓ = 38." | Section 1 |
| Conjecture 10; "The next open cases are 35 and 38." | Section 4.4 |
| Combined counts (2h − 2, 2h, 2h) | Appendix A |
| Quaternary history (Kotsireas–Winterhof, Jedwab–Pender, Kotsireas–Koutschan–Winterhof ℓ ≤ 40, Lebedev 7 lengths, Verma 64) | Section 1 |

## Length 38 (27 runs, all 0 pairs)

Sources: `project:search/run_38_H37.log`, `project:search/runs38/batch1.log`, `batch2.log`, `batch3.log`; family sizes in `project:search/twisted_38.txt`.

| Run | Sizes A / B | Log | Rerun by |
|---|---|---|---|
| (27,0,1,0) with itself | 180 / 180 | batch1 | verifier |
| (31,0,1,0) with itself | 180 / 180 | batch1 | verifier |
| (7,1,−1,0) with itself | 480 / 480 | batch1 | verifier |
| (11,1,−1,0) with itself | 480 / 480 | batch1 | verifier |
| (27,1,−1,0) with itself | 480 / 480 | batch1 | verifier |
| (31,1,−1,0) with itself | 480 / 480 | batch1 | verifier |
| (7,0,1,0) with itself | 69 300 / 69 300 | batch1 | verifier |
| (11,0,1,0) with itself | 69 300 / 69 300 | batch1 | verifier |
| (37,0,−1,0) with itself | 70 189 056 / 70 189 056 | batch1 | verifier |
| (37,0,−1,0) with (37,0,1,0) | 70 189 056 / 34 306 272 | batch1 | verifier |
| (37,0,1,0) with itself | 34 306 272 | run_38_H37 | write stage (`project:search/write_reruns/run_38_H37.log`: 34 306 272 words, 0 pairs) |
| (7,0,1,0) with (37,0,−1,0), (37,1,−1,0), (37,0,1,0) | 69 300 / 70 189 056, 222 265 344, 34 306 272 | batch2 | verifier |
| (7,1,−1,0) with the same 3 | 480 / same | batch2 | verifier |
| (27,0,1,0) with the same 3 | 180 / same | batch2 | verifier |
| (37,0,1,0) with (37,1,−1,0) | 34 306 272 / 222 265 344 | batch2 | not rerun |
| (1,19,−1,0) with itself, 5 parts | 43 275 730, 43 742 066, 46 779 026, 41 400 810, 47 067 712 / 222 265 344 | batch3 | not rerun |
| (37,0,1,0) with (1,19,−1,0) | 34 306 272 / 222 265 344 | batch3 | not rerun |

Count: 10 (batch1) + 1 (run_38_H37) + 10 (batch2) + 6 (batch3) = 27 runs. Rerun: 19 by the verifier, 1 by the write stage; 7 not rerun. Self-runs: 10 families plus (1,19,−1,0). Combinations of two different families: 1 + 10 + 1 = 12.

## Issues from VERIFY.md and where they are fixed

| # | Issue | Fix |
|---|---|---|
| 1 | Seven ℓ = 38 runs not rerun; present ℓ = 38 as secondary and negative; keep "says nothing about existence" | Paper Section 5 names the 19 verifier reruns, the 1 write-stage rerun and the 7 runs that were not rerun, and keeps the sentence "They say nothing about whether a ternary Legendre pair of length 38 exists." Abstract: "our searches in some structured families of length 38 found no pair". Table above. |
| 2 | State the searched groups exactly, with ⟨29⟩ | Paper Table 1 lists ⟨34⟩, ⟨6⟩, ⟨29⟩, ⟨11⟩, ⟨8⟩, ⟨13⟩, ⟨3⟩. Paper Proposition 3 and the paragraph before it give the subgroup coverage. The write stage reran ⟨29⟩ (130 162 032 words, 0 pairs); `checks/search.py` reruns all 7. |
| 3 | Calibration statement and "only multiplier groups of order 2, 3, 6" statement have no recorded run | Both are left out of the paper and the README. |
| 4 | Lean run time not stable | Paper Section 4 and Section 6, README and `checks/README.md` say "about 1 to 3 minutes" and give the three measured times. |
| 5 | `checks/__pycache__/*.pyc` committed | Removed from git in the project repository; `__pycache__/` added to `.gitignore`. `release/` has no `__pycache__`. |

## Write-stage runs (2026-11-25)

- `python3 -I checks/check.py` (clean copy): ALL CHECKS PASSED, < 1 s.
- `lake env lean lean/TernaryLP35.lean` (copy of `lean/TernaryLP35.lean`, shared workspace, Lean v4.36.0, Mathlib v4.36.0): exit 0, 56 s, axioms [propext, Classical.choice, Quot.sound].
- `python3 -I checks/search.py 6` (clean copy): 42 042 000 words, 2400 ordered pairs, certificate among the printed pairs, 96 s, peak 0.67 GB.
- `bash checks/ci.sh` (clean copy, new Python 3.13 venv made with `uv venv --seed`): exit 0, 391 s, peak 2.08 GB. Output: all 19 quick checks PASS; figure files match; ⟨34⟩ 5717712/0 (14 s), ⟨6⟩ 42042000/2400 (96 s), ⟨29⟩ 130162032/0 (280 s), ⟨11⟩ 87150/0, ⟨8⟩ 14840/0, ⟨13⟩ 1400/0, ⟨3⟩ 2/0; "paper numbers match data/expected.json"; "ci.sh: all checks passed".
- Mutation test of the paper-number step of `ci.sh`: with 130\,162\,032 changed to 130\,162\,033 in a copy of `paper/paper.tex`, the step prints `missing in paper.tex: ['130162032']` and exits 1.
- `python3 /Users/kenwu/research/kenwu-lab/tools/check_result.py <copy named ternary-legendre-pair-35>`: `ok: 1 result(s)`.
