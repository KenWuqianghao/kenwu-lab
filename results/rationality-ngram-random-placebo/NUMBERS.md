# Numbers in the paper and their sources

Sources: `R` = `data/expected.json` (pre-registered analysis, `checks/analysis.py`).
`P` = `data/expected_posthoc.json` (`checks/posthoc.py`). `V` = `VERIFY.md` of the
verification stage (not rerun by CI). `T` = protocol text or code. Slopes in the paper
are per decade: 10 × the per-year value in `R`. Rounding: 3 decimals, or as shown.

| Number in the paper | Value in source | Source |
|---|---|---|
| Ratio correlation, eng / fiction | 0.9999679 / 0.9999507 | R `repro.r_ratio`, `repro.r_ratio_fiction` |
| Count ratios an, science, god, feel, data | 1.00699, 1.03664, 1.00938, 1.00155, 1.01774 | R `repro.words` |
| Recovery error of an injected hinge, 1e-16 | 9.7e-17, 6.9e-17 | R `power_eng_FPS.*.max_recovery_error` |
| Power 1.00 for d = g_obs and g_obs/2 | 1.0, 1.0 | R `power_eng_FPS` |
| eng b = +0.167, b+g = -0.281, g = -0.449, best hinge 1987 | 0.016719, -0.028149, -0.044869, 1987 | R `observed.eng` |
| fiction g = -0.253, hinge 1979 | -0.025346, 1979 | R `observed.fiction` |
| non-fiction g = -0.365, hinge 1986 | -0.036494, 1986 | R `observed.nonfiction` |
| Table 1, FPS eng: median -0.396, q05 -0.472, p 0.126, reversal 1.000, tau share 0.946 | -0.039573, -0.047202, 0.125787, 1.0, 0.9461 | R `tests.FPS.eng` |
| Table 1, FPS fiction: -0.251, -0.345, 0.484, 0.908, 0.565 | -0.025136, -0.034461, 0.484352, 0.9082, 0.5653 | R `tests.FPS.fiction` |
| Table 1, FPS non-fiction: -0.299, -0.372, 0.069, 1.000, 0.901 | -0.029918, -0.037234, 0.068693, 1.0, 0.9006 | R `tests.FPS.nonfiction` |
| Table 1, FP eng: -0.057, -0.173, 0.0001, 0.643, 0.227 | -0.005711, -0.017259, 9.999e-05, 0.6426, 0.2272 | R `tests.FP.eng` |
| Table 1, FP fiction: -0.039, -0.135, 0.0006, 0.376, 0.346 | -0.003887, -0.013501, 0.00060, 0.3758, 0.3465 | R `tests.FP.fiction` |
| Table 1, FP non-fiction: -0.041, -0.136, 0.0001, 0.575, 0.210 | -0.004076, -0.013620, 9.999e-05, 0.5748, 0.2103 | R `tests.FP.nonfiction` |
| Table 1, label shuffle: 0.000, -0.136, 0.0001, 0.394, 0.237 | 1.98e-05, -0.013575, 9.999e-05, 0.3941, 0.2365 | R `tests.label_shuffle.eng` |
| "lower 13%", "12.6% of the pairs" | share_g_le_obs 0.1257 | R `tests.FPS.eng` |
| Skew of A -1.40, B +0.68 | -1.39710, 0.67847 | R `features.A.S`, `features.B.S` |
| Skew FP pairs -0.56, -0.43; FPS pairs -1.34, +0.62 | -0.55626, -0.43453; -1.33650, 0.61530 | R `tests.FP.match`, `tests.FPS.match` |
| Distinct words FPS 1,663, FP 1,874 | 1663, 1874 | R `tests.*.match.distinct_words` |
| POS of A: 22 N, 2 V, 1 ADJ; B: 24 N, 7 V, 14 ADJ | same | R `features.A.pos`, `features.B.pos` |
| Pool 20,000 words, last word "spoiling" | 20000, "spoiling" | R `pool_size`, `pool_last_word` |
| Non-fiction subset check passed | true | R `nonfiction_subset_check` |
| Post hoc b share: 0.22%, 0.51%, 0.20% | 0.0022, 0.0051, 0.0020 | R `tests.FPS.*.posthoc_share_b_ge_obs` |
| Fiction share of tokens 4.1%, 2.4%, 33.4% | 0.04103, 0.02422, 0.33378 | P `fiction_share_of_tokens` |
| Null sd 0.047, excess 0.053, 12% of g_obs | 0.04733, -0.05295, 0.1180 | P `detectable` |
| Detection shares f = 0.10..0.30: 0.252, 0.422, 0.609, 0.771, 0.885 | 0.252, 0.422, 0.6092, 0.7708, 0.8854 | P `detectable.power_extra_hinge` |
| "about 0.11 per decade" (25% of g_obs) | 0.25 × 0.4487 = 0.112 | arithmetic on R |
| Skew gap: observed -2.076, placebo -1.952 (sd 0.042), r = 0.31, adjusted p = 0.42 | -2.07556, -1.95179, 0.04152, 0.3116, 0.41686 | P `skew_gap` |
| K = 20: 0.219, 0.537, 0.114; K = 80: 0.075, 0.419, 0.050; FP p <= 0.0007 | 0.21898, 0.53725, 0.11419; 0.07529, 0.41856, 0.05029; max 0.0007 | P `K_sensitivity` |
| Neighbours of "data" and "soul" | lists | P `neighbours_FPS` |
| 419 numbers compared (332 + 87) | "compared 419 values; mismatches: 0" | output of `checks/rerun.py` |
| Rerun time 514 s (pre-registered part, clean clone) | 514 s | `checks/rerun_clean_clone.log` of the solve stage, `RESULT.md` |
| Viewer agreement 0.02% (eng), fiction 0.9989-1.0000, min 0.953 | as stated | V check 7 |
| Independent implementation p = 0.128-0.130, FP p <= 0.0004, p = 0.132 with "an" | as stated | V checks 8, 9 |
| K = 40, N = 10,000, seeds, threshold 0.05, protocol commit 1bd3e8c at 10:36 | as stated | T `PROTOCOL.md`, `git log` |
| Extractor thresholds 2,000 and 1,000 | `MINU 2000`, `MINT 1000` | T `checks/extract.c` |
| 7.3 GB streamed, 0.5 GB extract | as stated | `RESULT.md`; extract folder 522 MB |
| Source quotes (5% to 35% fiction; "likely an effect of rising proportion of fiction") | verbatim | PMC8713757 full text, fetched 2026-11-26 |

# Verify issues and where the paper fixes them

| Issue (`VERIFY.md`) | Fix |
|---|---|
| W1: the verdict is a non-rejection; give the detectable size | Abstract ("This is a non-rejection: ... 0.77"); Section 4 "What the test can detect" with the detection table; Limits, first item. The direct injection is computed by `posthoc.py` on the solver's pairs (0.771 at 25%; the verifier's pairs gave 0.79). |
| W2: the power 1.00 numbers are not informative | Section 4, last paragraph: they describe a hinge added on top of the register effect and are replaced by the detection table. |
| W3: not a refutation of the source; "composition is sufficient" too strong | Title ("same fiction skew"), abstract ("does not show that the turn is specific ... beyond their register"; "does not explain it alone"), the result box, Section 6 "Interpretation" (turn inside each sub-corpus; consistent with the source's broad PC2 pattern). |
| W4: cite what the source says about fiction | Introduction, third paragraph, with two verbatim quotes; "The new part here is the matched placebo test". |
| W5: Language Log post | Introduction, fourth paragraph, and reference [7] (Mair 2021). |
| W6: two filters not in the protocol | Table 2 "Two filters in the code that the protocol does not state"; `checks/README.md` step 1. |
| W7: matching quality, direction, K trend, post-hoc marking, nature of neighbours | Section 5 "Matching quality" and "Number of candidates K" (marked post hoc); Section 3, last paragraph (neighbours of "data" and "soul"). The K runs are now in `checks/posthoc.py` and `data/expected_posthoc.json`. |
| W8: b+g = -0.281; remove `__pycache__`; keep the post-hoc rise marked | Section 3 gives -0.281. `checks/__pycache__` removed from the repository and `__pycache__/` added to `.gitignore`. Section 5 "The rise before 1980 (post hoc)" and the abstract ("Post hoc, ..."). |
