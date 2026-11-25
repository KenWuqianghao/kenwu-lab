# Numbers in the paper and their sources

`S` = `data/summary.json` (equal to `data/expected.json`; checked by `checks/rerun.py`). `T` = `data/results_table.csv`. `V` = `VERIFY.md` of the verify stage (independent code in `checks/independent/`). `R` = `RESULT.md` of the solve stage. `P` = `PROTOCOL.md`. Each value was compared with its source by a script (see the end of this file).

| Number in paper | Where | Source |
|---|---|---|
| 143,700 quasars; 86 SPL and 106 DRW candidates; three named | Abstract, Sect. 1 | Chen et al. 2024, arXiv:2206.11497v2 abstract (`ms.tex` line 74) |
| 3.6 years of new data | Abstract, Sect. 1, README | (60969.55 − 59647.0)/365.25 = 3.62 yr; last epoch MJD 60969.55 (R) |
| median 1.42 cycles | Abstract, Sect. 4, Sect. 7 | S `candidate_training.median_ncyc_test` = 1.4207 |
| 7 of 86; chance 4.3; binomial p = 0.139 | Abstract, Sect. 4 table, README | S `primary_drw.N_cand_sig`, `n_cand`; 0.05 × 86 = 4.3; `T1_binom_p` = 0.13895 |
| 29 of 273 (10.6%); Fisher p = 0.81 | Abstract, Sect. 4, Sect. 5 | S `primary_drw.N_plac_sig`, `n_plac`, `frac_plac` = 0.10623, `T2_fisher_p` = 0.80708 |
| 8.1% | Sect. 4 table, Sect. 5 | S `primary_drw.frac_cand` = 0.08140 |
| named p-values 0.26, 0.81, 0.40 (0.257, 0.812, 0.399) | Abstract, Sect. 4 table | S `named.*.p_drw` |
| named P 885, 886, 746 d; k 0.24, −0.30, 0.11; phase −0.000, +0.45, +0.22; amplitude ratio 0.24, 0.32, 0.29; power 0.85, 0.96, 0.90 | Sect. 4 table, Fig. 2 | S `named.*` |
| 65 (65.4) passes if all strict sinusoids; mean power 0.76 | Abstract, Sect. 4 | S `power.expected_N_if_all_periodic_drw` = 65.449, `mean_power_drw` = 0.761 |
| 14% (0.138) | Abstract, Sect. 4, Sect. 7 | S `power.f95_upper_drw` |
| 36% (0.363), post hoc | Abstract, Sect. 4, Sect. 7 | S `post_hoc.f95_upper_injection_power` |
| 0.194 with placebo chance rate | Sect. 4 | S `post_hoc.f95_upper_injection_power_placebo_alpha` |
| 14 of 86 candidates on the unconditioned null | Sect. 3 | S `n_cand_unconditioned_null_drw` |
| 273 of 344 placebo analysed; 71 excluded, 5 with no r data | Sect. 4 | S `status_counts.plac`; 5 empty light curves (R, Controls) |
| periods 601 to 1030 d, median 872 d | Sect. 4 | S `candidate_training.P_range`, `median_P` |
| refit periods 783, 740, 739, 630, 698 d; published 788.8, 736.2, 736.2, 626.6, 688.6 d; within 1.4% | Sect. 4, Sect. 7 | S `period_check`; maximum relative difference 1.34% (J004744.03) |
| median 40.5 test bins | Sect. 4 | S `candidate_training.median_n_test_bins` |
| median k 0.10, 0.02, 0.37; Mann-Whitney p = 0.16 | Sect. 4 | S `k_distribution.median_k_cand`, `median_k_plac`, `median_k_inj`, `mw_cand_vs_plac_p` = 0.1638 |
| injection pass rate 0.32 (22 of 69); 17 hosts too few bins | Sect. 4, Sect. 5 | S `injection.N_sig_drw`, `n`, `frac_sig_drw` = 0.3188; `status_counts.inj.too_few_bins` |
| amplitude ratio median 0.46 | Sect. 4 | S `k_distribution.median_amp_ratio_cand` = 0.4646 |
| phase within ±0.125: 25.6% (candidates), 30.8% (placebo) | Sect. 4 | S `k_distribution.frac_cand_abs_dphi_lt_0p125`, `frac_plac_abs_dphi_lt_0p125` |
| smallest p 0.0029 (SDSS J132457.51+325145.9); Bonferroni 0.00058 | Sect. 4 | S `post_hoc.min_p_drw_cand`, `bonferroni_threshold`; `sig_candidates_drw` |
| the 7 nominal passes (names) | Sect. 4 | S `sig_candidates_drw[*].name` |
| unconditioned DRW null: 15 of 273 (5.5%) placebo, 3 of 86 candidates | Sect. 5 | S `secondary_drw_unconditioned` |
| 1 placebo with xi > 4 and > 1.5 cycles | Sect. 5 | S `k_distribution.n_plac_xi4` |
| host DRW amplitude 0.117 mag; injected amplitude 0.115 mag; residual DRW 0.028 mag | Sect. 5 | S `post_hoc.median_amp_inj_host_drw_sigma`, `median_amp_cand`, `median_alt_drw_sigma_cand` |
| injected period recovered within 10% in 46%; median k 0.67 and 0.07 | Sect. 5 | V check 16 |
| power-law null: 1 of 86, 4 of 273; mean power 0.08 | Sect. 5 | S `secondary_spl.N_cand_sig`, `N_plac_sig`; `power.mean_power_spl` = 0.0806 |
| 164 numbers reproduced | Sect. 6, README | `checks/rerun_clean_clone.log` (solve), `checks/verify/rerun_verify.log` (verify), clean-copy CI run of this stage |
| 359 analysed objects; P to 4.5e-5; k median 7e-6 | Sect. 6 | V check 11 |
| independent named p 0.260, 0.389, 0.787; 21 objects | Sect. 6 | V check 14 |
| 58.1% k > 0 (p = 0.080); Wilcoxon p = 0.122; Mann-Whitney on correlation p = 0.172 | Sect. 6 | V check 15; S `k_distribution.frac_cand_k_gt_0` = 0.5814 |
| C43, C46 p 0.046 and 0.044; independent 0.050 and 0.052; N_C 5 to 7 | Sect. 6 | S `sig_candidates_drw` (0.04570, 0.04376); V issue W2 |
| T1 needs N_C ≥ 11; N_C = 10 gives 0.0107 | Sect. 6 | `scipy.stats.binomtest(10, 86, 0.05, alternative="greater")` = 0.01074; N = 11 gives 0.00373 |
| 17 of 359 objects, k moves by at most 0.056; 5 candidates p 0.15 to 1.0 | Sect. 6 | V check 11 and issue W8 |
| 74% of refits with xi > 4 | Sect. 7 | S `candidate_training.frac_xi_gt4` = 0.7442 |
| 25 and 47 citing works | Sect. 8 | `PRIOR_ART.md` searches 1 and 2 |
| DR11 limits MJD 58194.0, 59647.0 (2022-03-09), 59159.0; test end 60970.0 | Sect. 3 | P Sect. 3; `checks/qpo.py`; V check 4 |
| protocol commit 2026-11-24 22:53 (+01:00) | Sect. 3 | commit `28e9bb9` of the problem repository; V check 5 |
| 4 placebo per candidate, 344; Δr < 0.3, Δz < 0.3, r ≤ 20, Dec > −28°, 10 arcsec | Sect. 2 | P Sect. 2; `checks/fetch_data.py` |
| 20,000 / 1,000 / 300,000 / 200 mocks; 2,000 power mocks; 20% period window | Sect. 3 | P Sect. 7, 9; `checks/analysis.py` |

## Issues left open by `VERIFY.md` and where they are fixed

| Issue | Fix |
|---|---|
| W1: the source already says the candidates are mostly not strictly periodic | Paper Sect. 1 quotes the abstract of Chen et al. ("instead of being strictly periodic ...") and states that the result is an out-of-sample check of their conclusion, not a refutation of a claim about all 86. Abstract last sentence; Sect. 7 first item; Sect. 8 last sentence. README introduction. |
| W2: N_C depends on the Monte Carlo seed | Paper Sect. 6 "Sensitivity" (N_C between 5 and 7; T1 needs N_C ≥ 11). `checks/README.md` "Known sensitivities". |
| W3: the rerun does not regenerate the sample tables | `checks/README.md` "Sample tables"; docstring of `checks/rerun.py`. Paper Sect. 6 states that the verification stage rebuilt both tables. |
| W4: the placebo is not selected for periodicity; exclusions | Paper Sect. 2 "Placebo" (matched in magnitude and redshift only); Sect. 5 (1 placebo passes the first cut; T2 compares with unselected quasars); Sect. 4 "Population" (0 of 86 candidates and 71 of 344 placebo excluded). Abstract says "not selected for periodicity". |
| W5: null calibration | Paper Sect. 5 "Placebo and null calibration": conditioned 10.6%, unconditioned 5.5%; exact T1 p not reliable; conclusion rests on T2 and on the direction of the bias; cause not found. |
| W6: wording of the main claim | Abstract and Sect. 1 box: "we find no evidence"; upper limit given as 14% (pre-registered, simulated power) to 36% (post hoc, injection power); Sect. 7: quasi-periodic signals and individual candidates not excluded; 1.42 cycles. |
| W7: low injection power | Paper Sect. 5 "Injection": host red noise 0.117 mag against amplitude 0.115 mag; period recovered in 46%; median k 0.67 and 0.07. |
| W8: polynomial conditioning; tracked `.pyc` files | Paper Sect. 6 "Sensitivity"; `checks/README.md`. The `.pyc` files were removed from the problem repository (commit `274764d`) and `__pycache__/` is in `.gitignore`. |

## Check of this file

A disposable script read each `S` key above, rounded it as in the paper and compared it with the paper text. Output is in `LOG.md` of the problem repository (write stage).
