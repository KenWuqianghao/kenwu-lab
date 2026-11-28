# Numbers in the paper and their sources

`E` = `data/expected.json` (reproduced by `checks/rerun.py`; clean-copy CI run on 2026-11-28 printed `OK`).
`A` = `E["addendum1"]`. `V4` = output of `checks/verify/v4_censored_independent.py` (listed in `checks/README.md`).
`L` = Liao et al. 2021, arXiv source `bbh_v9.tex` (Table 2 at lines 571-572; abstract at line 192; Sec. 6 at line 826).
Rounding: p-values to the shown digits; T to 2 digits in the text, 3 in the abstract of the result.

## Data and template

| Number in the paper | Value | Source |
|---|---|---|
| GLS period quoted in the abstract of L; z = 1.53 | 1607 ± 7 d | L line 192 |
| q = 0.11 periods g / r / i / z / griz | 1511, 1466 +64/-12, 1506, 1562 +248/-99, 1476 +128/-5 | L line 572 |
| GLS periods | 1607 to 1632 d | L line 571 |
| DRW tau (r, Table 2) | 716 d | L Table 2 line 9 |
| DRW posterior labels, r band | sigma 0.15 +0.10/-0.03; log10 tau 2.9 +0.5/-0.2 | `chain_4band.pdf` labels, read by the verifier (VERIFY.md W1) |
| best fit used in mocks | tau 794.3 d (10^2.9), sigma 0.15 | A.best_fit_drw.tau, sigma |
| digitized span | MJD 50909-58889 | `data/model_r_digitized.json` min/max mjd (50908.86, 58888.92) |
| template peak-to-peak | 0.33 mag | E.zr.template_ptp_mag = 0.328 |
| trough spacing 1350-1650 d | 1350-1650 d | VERIFY round 1 (commit 518b9cb), RESULT.md "Scope"; descriptive |
| cutoff | MJD 58927 = 2020-03-19 | PROTOCOL.md |
| held-out points, objects | 97; 2 (91 + 6) | E.zr.n_points, n_oid; A.n_listed = 97; 91/6 from RESULT.md data table |
| date range | MJD 59061.44-60968.34 = 2020-07-31 to 2025-10-20 | E.zr.mjd_min, mjd_max |
| cycles | 1.3 | (60968.34 - 59061.44) / 1466 = 1.30 |
| good exposures | 345 (312 + 33); listed on 97 (28%) | A.n_epochs, n_epochs_402, n_epochs_1446, n_listed |
| k | 1.42 | A.k_noise = 1.416 |

## Observed statistic and robustness

| Number | Value | Source |
|---|---|---|
| T_obs | -0.664 | E.zr.T_obs, A.T_obs |
| phase rank, best shift, T at best shift | 19 of 20; 0.55; 1.03 | E.zr.phase_rank_of_zero, best_phase_shift, phase_scan_T[11] = 1.0309 |
| T with limitmag covariate | -0.53 | A.depth.T_with_limitmag_covariate |
| T on limitmag > 21.3, n | -0.57, 53 | A.depth.T_limitmag_gt_21.3, n_limitmag_gt_21.3 |
| T with last-cycle template | -0.91 | E.robustness.T_zr_last_cycle_template |
| corr, slope (mag vs limitmag) | 0.69, 0.57 | A.depth.corr_mag_limitmag, slope_mag_limitmag |
| zg: n, T | 34, -0.12 | E.zg.n_points, T_obs |
| positive control: n, T | 72, +1.72 | E.robustness.control_preCUT_zr_n, control_preCUT_zr_T |
| pre-cutoff ZTF span | 2018-07 to 2020-03, about 600 d | first zr epoch MJD 58319 (2018-07-20) in `work/ztf_raw.csv`; cutoff 58927 |

## Original protocol

| Number | Value | Source |
|---|---|---|
| DRW rms | 0.119 | E.zr.sigma_drw |
| p_null, p_sig, power | 0.949, 0 of 5000 (< 2e-4), 0.59 | E.zr.p_null, p_sig, power_at_0.01 |
| median T of signal mocks under censoring | about 0.6 | A.best_fit_drw.median_T_sig and A.grid_tau716 (0.50-0.64) |

## Censored model (Table 1)

| Row | p_sig / p_null / median T / power | Source |
|---|---|---|
| best fit | 0.0005 / 0.965 / 0.61 / 0.30 (text: "about 0.3"); sd T 0.36 | A.best_fit_drw |
| tau 716, sigma 0.10 ... 0.30 | as in the table | A.grid_tau716[i] (p_null rounded to 2 digits; p_sig 0.00075 -> 0.0008, 0.00475 -> 0.0048, 0.0165 -> 0.017, 0.03125 -> 0.031) |
| 68% contour | max p_sig 0.002; median T 0.56-0.63; power 0.23-0.45 | A.posterior_contours.c68 (median T 0.564-0.625; power 0.233-0.448) |
| 95% contour | max p_sig 0.035; median T 0.50-0.64; power 0.03-0.46 | A.posterior_contours.c95 (0.502-0.637; 0.028-0.462) |
| p_sig >= 0.01 on the 95% contour | 5 of 24 points, log10 tau >= 3.488, sigma >= 0.331 | A.posterior_contours.c95.rows |
| edge of the plotted 95% contour | log10 tau 3.84, sigma 0.47 | max of `data/drw_posterior_r.json` c95 (3.8447, 0.4724) |
| 95% contour at tau = 716 d | sigma 0.117-0.177 | `data/drw_posterior_r.json` c95, points with abs(log10 tau - log10 716) < 0.03: 0.1175-0.1766 |

## Model checks and calibration (Table 2)

| Number | Value | Source |
|---|---|---|
| slope in mocks | 0.62 | A.best_fit_drw.slope_mag_limitmag_mock_median |
| listed fraction, data / mocks | 0.03 0.14 0.43 0.63 0.65 / 0.01 0.10 0.40 0.66 0.92 | A.detfrac_by_limitmag_obs, A.best_fit_drw.detfrac_by_limitmag_mock |
| deepest bin | 23 exposures, 15 listed | V4 "deep exposures (limitmag > 21.6): 23 listed 15" |
| placebo z: n, median, robust sd, sd | 51, -0.01, 1.67, 2.07 | A.placebo |
| Spearman of abs(z) and abs(median sharp) | -0.12, p = 0.38 | `scipy.stats.spearmanr` on A.placebo.rows columns z and median_sharp, absolute values (run in the write stage: -0.1246, p 0.384) |
| placebo objects with T <= T_obs | 1 | A.placebo.rows (count of T <= -0.664); V4 also gives 1 |
| inflated p_sig, registered rule | 0.015 | A.best_fit_drw.p_sig_inflated |
| inflated x1.67, independent | 0.0175 | V4 "p_sig x1.67 0.0175" |
| inflated x2.07, independent | 0.043 | V4 "x2.07 0.0428" |
| quadrature calibration (25 objects) | 0.0105 | V4 "placebo with 70-130 points: n 25", "Gaussian p_sig 0.0105" |
| white-noise part only | 0.0015 | A.best_fit_drw.p_sig_inflated_white_part_only_posthoc |
| "1.7 to 2.1 times" (abstract) | 1.67, 1.75, 2.07 | A.placebo.z_robust_sd; V4 robust sd 1.748; A.placebo.z_sd |
| "0.01 to 0.04" | 0.0105-0.043 | rows of Table 2 except "none" and the white-only variant |
| independent implementation | k 1.416, T -0.6636, median T 0.61, robust sd 1.75 | V4 |

## Other periods (Table 3)

All values from A.other_periods.rows (T_obs, p_sig, p_null). T rounded to 2 digits.

## Prior-art counts

48 citing works of Liao et al., 90 of Chen et al. 2020, 19 of Covino et al. 2022: `PRIOR_ART.md` of the problem repository (OpenAlex, 2026-11-28).

## Commits named in the paper

f6a2c6d (protocol), 5f19203 (first comparison), a7f1e6f (Addendum 1), 01a9e44 (censored computation): problem repository `git log`.

# Open issues of VERIFY.md (round 2) and where the paper fixes them

| Issue | Fix |
|---|---|
| W1: r-band tau label is +0.5/-0.2, not +0.7/-0.2 | Paper Sec. 3.3 gives log10 tau = 2.9 +0.5/-0.2. `PROTOCOL.md` in this folder keeps the addendum text unchanged and has a dated correction line at its end. |
| W2: deepest bin has 23 exposures, 15 listed | Paper Sec. 4.4: "The deepest bin has 23 exposures, and the quasar is listed on 15." |
| W3: the 95% contour is cut at the axis edge | Paper Sec. 4.3 (after Table 1): "the value 0.035 is the maximum on the plotted part only"; Table 1 row "(plotted part)". |
| W4: the inflation factor is not sharp; give a range | Abstract ("0.01 to 0.04"), Table 2 (all calibrations), Sec. 4.5. 0.015 is named as the value of the registered rule in our mocks, not as an exact number. The paper never says "refuted" for the final decision and never says "removes the forecast". |
| W5: power to one digit | Abstract, Sec. 4.3, 4.5 and Limits say "about 0.3". Table 1 lists the computed values with a note in the caption. |
| W6: `problem.json` significance text is outdated | The paper and README use the round-2 claim: inconclusive by the registered rule, anti-phase sign, low power, positive T at 1604-1607 d (post hoc). `problem.json` belongs to the driver and is not edited. |

Round-1 issues (all fixed in the solve stage, VERIFY.md round 2): censored model (Sec. 3.3), DRW scan (Table 1, Fig. 2), scope (Sec. 1 last paragraph, Sec. 4.6, abstract), weak positive control (Sec. 4.1), "our continuation" wording (Sec. 2, abstract), small items (Sec. 7).
