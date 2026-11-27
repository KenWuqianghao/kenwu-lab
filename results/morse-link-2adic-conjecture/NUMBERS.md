# Numbers in the paper and their sources

Paths without a prefix are in this folder. Paths that start with `project:` are in the factory project repository (`problems/morse-link-2adic-conjecture`).

| Number in the paper | Value | Source |
|---|---|---|
| L^(2)_2, C_2, L^(2)_2 − C_2 | 82, 2, 80 = 2⁴·5 | `checks/certificate.py` (`data/expected.json`); hand count in Section 2; Lean lemma `val2` (valuation 4) |
| L^(2)_3, C_3, L^(2)_3 − C_3 | 57349, 5, 57344 = 2¹³·7 | `checks/certificate.py`; `project:RESULT.md`; VERIFY check 6; Lean lemma `val3` (valuation 13) |
| Terms of L^(2)_3 | 1 + 162 + 6561 + 50625 | hand count; b(0) = 1, b(1) = 81, b(2) = 625 |
| L^(2)_4 − C_4 | 2⁴·10127819 | `checks/certificate.py` |
| L^(2)_19 (90 digits), C_19 | 2620…6774, 1767263190 | `checks/certificate.py` (`data/expected.json`) |
| ξ₂(L^(2)_19 − C_19); odd part | 11; 87 digits | `checks/certificate.py`; Lean lemma `val19` |
| s₂(n) at n = 2, 3, 4, 19 | 1, 2, 1, 3 | `checks/certificate.py`; Lean (`norm_num [s2]`) |
| d(n) at n = 2, 3, 4, 19 | 3, 11, 3, 8 | `checks/certificate.py`; `checks/verify_k2.py`; `checks/independent_check.py`; `project:RESULT.md`; VERIFY check 5 |
| Forced c and α (Remark 3) | c = 3, α ≡ 3 + 2⁸ (mod 2⁹), first failure n = 19 | `checks/certificate.py` step 4 |
| Exhaustive test | α mod 2¹², c ≤ 3, n = 2, 3, 19: no solution | `checks/certificate.py` step 3 |
| k with no fit for n ≥ 2 (k ≤ 24, n ≤ 200) | 2, 6, 10, 14, 18, 22 | `data/survey_N200_K24.txt`; `project:checks/verifier_survey_N200_K24.txt`; VERIFY check 8; `ci.sh` pattern check |
| Fit for n ≥ 4, all k ≤ 24; c_k = ξ₂(k) + 2 | — | same as above |
| k = 2, n ≥ 4 fit | c₂ = 3, α₂ ≡ 1010110011₂ (mod 2¹⁰) | `checks/fit.py` (written in the write stage) |
| k = 1 fit | c₁ = 2, α₁ ≡ 101010111₂ (mod 2⁹) | `checks/fit.py`; agrees with …010111₂ in Conjecture 4.11 |
| Lean axioms | [propext, Classical.choice, Quot.sound] | `#print axioms` output, write-stage run (below) |
| Lean compile time | about 3 min (2 min 49 s measured) | write-stage run: `lake env lean GaoGu412.lean` under `run-heavy` |
| Survey time | about 17 s (17.3 s measured) | write-stage rerun; output identical to `data/survey_N200_K24.txt` |
| Number of pages | 5 | `pdfinfo paper/paper.pdf` |

## Open issues of the last VERIFY.md and where the paper fixes them

| Issue (VERIFY round 1) | Fix |
|---|---|
| 1. The disproof comes only from n = 3; the n ≥ 4 version is open; do not claim more than a range correction. | Abstract ("The failure comes from the index n = 3 alone. The version … for n ≥ 4 remains open"); Section 1 "Result"; Remark 3; Section 6 (Limits), item 2; README. |
| 2. The journal wording is not confirmed; cite arXiv v1 as the source of the quote. | Section 1 "The conjecture" ("quoted word for word from arXiv:1908.03914v1", "We did not read the journal text"); Section 6, item 5. |
| 3. Say that the result is computer-assisted with exact arithmetic, with no Lean proof. | Superseded in the write stage: a Lean proof now exists (`lean/GaoGu412.lean`, tier "Proved in Lean"). Section 4 says how Lean and the exact Python checkers check the result, that the proof uses kernel reduction and no `native_decide`, and that the Python programs are not formally verified. The n = 2, 3 values have hand proofs in Section 2. |
| 4. "Fails for all k ≡ 2 (mod 4)" and "c_k = ξ₂(k) + 2" are observations only. | Abstract ("These two statements are computed, not proved"); Section 5 ("These are observations for the stated range only. We do not prove them."); Section 6, item 3. |

## Write-stage runs

- `cd /Users/kenwu/research/factory/lean && run-heavy 590 lake env lean …/lean/GaoGu412.lean`: 2 min 49 s; output `'GaoGu.conjecture_4_12_false_k2' depends on axioms: [propext, Classical.choice, Quot.sound]` and the same for `GaoGu.conjecture_4_12_false`; no errors.
- Clean copy `/tmp/mlcheck/morse-link-2adic-conjecture`, new venv (Python 3.13): `bash checks/ci.sh` ends with `ci.sh: all checks passed` (28 s). With one exponent in `paper.tex` changed, it fails with `missing in paper.tex: ['$57344=2^{13}\\cdot 7$']`.
- `bin/lean-compare release/lean` and `bin/lean-compare lean` (identical files by `diff -r`): `Lean default kernel accepts the solution`, `Your solution is okay!`, exit 0.
- `bin/lean-audit release/lean/GaoGu412.lean`: `PASS lean/GaoGu412.lean: 85 declarations, no project axioms` (3 min 9 s).
- `python3 kenwu-lab/tools/check_result.py /tmp/mlcheck/morse-link-2adic-conjecture` (clean copy): `ok: 1 result(s)`.
