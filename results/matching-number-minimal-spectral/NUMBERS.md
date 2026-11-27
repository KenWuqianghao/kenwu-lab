# Numbers in the paper and their sources

Paths without a prefix are in this folder. Paths that start with `project:` are in the factory project repository (`problems/matching-number-minimal-spectral`).

| Number in the paper | Value | Source |
|---|---|---|
| c for n = 2k, k ≥ 3 | 3 | Proof step 1 (hand); Lean `hc` in `lean/Solution.lean`; `checks/verify.py` output `c=3` for k = 3..8 |
| Solutions (d_i, f_i) of 2d_i + f_i ∈ {3, 4} | (0,3), (0,4), (1,1), (1,2), (2,0) | Proof step 2 (hand enumeration); Lean `hterm` (`omega`) |
| Least order built for n = 2k | 2k + 1 | Proof step 4; `checks/verifier_check.py` Part A: `min order built=7, 9, 11, 13, 15` for k = 3..7; VERIFY check 9 |
| Ceiling reading: c and least order | c = 3 (k = 3), 4 (k ≥ 4); 2k + 3 | Remark 5 (hand); `checks/verifier_check.py` Part A `c[ceil]`: min order 11, 13, 15, 17 for k = 4..7 |
| (6,3) is the only pair with n = 2k, k ≥ 3, k ∣ (n − 3) | — | Remark 4: k ∣ 2k − 3 ⇒ k ∣ 3 (hand) |
| k = 1, n = 2: c = 1, f_1 = 1; k = 2, n = 4: c = 2, f = (1, 0) | — | Remark 3 (hand); `data/search20.json` rows (2,1), (4,2); `checks/verifier_check.py` control `P4 in T'_(4,2): True` |
| Checker ranges | verify.py k = 3..8; verifier_check.py k = 3..7 (Part A), 3..6 (Part B); matching number of P_{2k} for k = 3..10 | `checks/ci.sh` arguments; outputs in `project:results/verify.txt`, `project:results/verifier_check.txt` |
| Pairs (n, k) with 2 ≤ n ≤ 20 | 100 | `data/search20.json`; `checks/compare_search.py`; `data/expected.json` |
| Pairs with a minimiser outside T'_{n,k} | 8: (2k, k), k = 3..10 | same |
| Pairs with all minimisers inside | 92 = 90 (n ≥ 2k + 1) + 2 ((2,1), (4,2)) | same |
| Tied minimisers (tolerance 10⁻⁹) | (13,4): 3, (17,4): 3, (18,6): 4, (19,4): 2 | same |
| ρ(P_{2k}), Table 1 | 1.801938, 1.879385, 1.918986, 1.941884, 1.956295, 1.965946, 1.972723, 1.977662 | `data/search20.json` `rho_min`; equal to 2 cos(π/(2k+1)) within 10⁻⁹ (`checks/compare_search.py`) |
| Tie tolerance | 10⁻⁹ | `checks/search.py` |
| arXiv dates of the source | v1 13 Jul 2026, v2 17 Jul 2026 | arXiv abstract page of 2607.11061 (submission history), fetched in the write stage |
| Journal record | Linear Algebra Appl. 755 (2027) 151–163 | Crossref record of doi:10.1016/j.laa.2026.10.032, fetched in the write stage |
| Liu–Lou–Trevisan journal record | Linear Algebra Appl. 746 (2026) 88–110 | Crossref record of doi:10.1016/j.laa.2026.05.011, fetched in the write stage |
| Lean axioms | [propext, Classical.choice, Quot.sound] | `#print axioms` in `lean/Solution.lean`; write-stage `lean-audit` run (below) |
| Number of pages | 6 | `pdfinfo paper/paper.pdf` |

## Open issues of the last VERIFY.md and where the paper fixes them

| Issue (VERIFY round 1) | Fix |
|---|---|
| 1. The journal version is not checked; the range of Construction 9 changed between v1 and v2; "paywall" is not accurate. | Abstract (last sentences before the AI statement); Section 1, paragraph "Versions of the source" (v1 range n ≥ 2k − 1, v2 range n ≥ 2k, journal text not read, "the publisher blocked our automated access, and its full-text interface gave only metadata"); Section 6, item 2; reference [2] ("full text not read"); README. The write stage tried again: the Elsevier full-text API returned only metadata, and ScienceDirect returned HTTP 403. "Paywall" is replaced in `project:STATEMENT.md` and `project:PRIOR_ART.md`. |
| 2. State the boundary nature in the title, abstract and first paragraph. | Title ("of order 2k … T'_{2k,k}"); abstract ("The failure is at the boundary n = 2k …", "The result does not touch the range n ≥ 2k+1"); Section 1 "Result" ("a defect at the boundary … It is not a new spectrally minimal graph"); Section 6, item 1; README "Result" and the paragraph after the figure. The paper does not use the word "disprove". |
| 3. State what Lean checks. | Abstract ("Lean 4 with Mathlib checks the counting step … the facts about P_{2k} are … checked by hand and by computer for small k"); Section 5 "Lean" (the statement in full, and "Lean does not build the tree itself, and it does not define the matching number, the spectral radius or G_{n,k}"); Section 6, item 3; tier "Computer-assisted" in `result.json`. |
| 4. The search is a floating-point diagnostic; the Collatz–Sinogowitz attribution is not confirmed. | Abstract ("a floating-point search"); Section 4 ("These results are computed in floating point, with a tolerance for ties. They are evidence, not a proof."); the restricted question is stated as Question 6, open; last paragraph of Section 4 ("usually attributed to Collatz and Sinogowitz. We did not read their paper, and we do not use this fact"); Section 6, item 4. No citation to Collatz–Sinogowitz is given. |

## Write-stage runs

- `bin/lean-audit release/lean/Solution.lean` (under `run-heavy`): `PASS release/lean/Solution.lean: 8 declarations, no project axioms`, exit 0.
- `bin/lean-compare release/lean` (under `run-heavy`): `Lean default kernel accepts the solution`, `Your solution is okay!`, exit 0. `release/lean/` and `project:lean/` are identical (`diff -r`).
- `cd factory/lean && lake env lean release/lean/Solution.lean`: exit 0 in 12 s; output `'construction9_no_tree_of_order_two_mul' depends on axioms: [propext, Classical.choice, Quot.sound]`.
- Clean copy of `release/` renamed `matching-number-minimal-spectral`, new venv (Python 3.13.18): `bash checks/ci.sh` ends with `ci.sh: all checks passed` (133 s, with the package install). `python3 -I checks/verify.py 8` in the same copy: `ALL OK`.
- `python3 kenwu-lab/tools/check_result.py <clean copy>`: `ok: 1 result(s)`.
- Corruption tests: a search JSON with one changed row makes `compare_search.py` exit 1; the value 1.956295 changed to 1.956296 in `paper.tex` makes the paper-number check exit 1 (`missing in paper.tex`); one changed label in `data/figure.svg` makes `draw_figure.py --check` exit 1.
- Paper: built with Tectonic 0.17.0 (this machine has no `latexmk`), no TeX warnings, 6 pages.
