# Numbers in the paper and their sources

`E` = `data/expected.json` (reproduced by `checks/rerun.py`; clean-copy CI run on 2026-11-28 printed `OK`). `A` = `E["addendum1"]`. `W` = `A["refit_worlds"]`.
`V` = verification-stage output in the problem repository (`verify/indep3.out`, `verify/VERIFY_round1.md`, `VERIFY.md` round 2); not in this folder.
`Z` = arXiv source of Zheng et al. 2016, `ms.tex`. `X` = arithmetic shown in the row (inputs from `E` or `A`; the CRTS mean epoch 55009.5 is the mean of the 252 CRTS MJDs that `rerun.crts_points` returns).

## Claim and data

| Number in the paper | Value | Source |
|---|---|---|
| formula | V = 0.1 sin(2π(t − 53413.09)/741) + 16.59 | Z line 303 |
| two signals, 8.1-year light curve, P > 99% | 741 d, 1500 d | Z line 65 (abstract) |
| z | 0.217 | Z lines 64, 244 |
| quasars searched | 347 | Z line 230 |
| DRW tau of the paper | 210 d | Z line 302 |
| ACF period | 1497 d | Z lines 305, 324 |
| CRTS end of the paper | MJD 56591 | `PROTOCOL.md`; Z Fig. 1 |
| citing works read | 38 | `PRIOR_ART.md` |
| ZTF points, per band, objects | 2448; 998 g, 1450 r; 7 | E.n_points, n_points_per_band, n_oid |
| ZTF span | MJD 58298.5-60969.3 = 2018-06-29 to 2025-10-21 | E.mjd_min, mjd_max (date conversion from MJD) |
| median mag | 17.37 g, 17.08 r | E.median_mag |
| cycles after last CRTS point | 2.3 to 5.9 | X: (58298.45 − 56571.32)/741 = 2.33; (60969.34 − 56571.32)/741 = 5.94 |
| cycles after T0 | 6.6 to 10.2 | X: (58298.45 − 53413.09)/741 = 6.59; (60969.34 − 53413.09)/741 = 10.20 |
| CRTS points, span | 252; MJD 53648.4-56571.3 = 2005-10-05 to 2013-10-06 | A.crts_n_points, crts_mjd_range |
| green-curve check | 751 vertices, 0.0004 mag | A.green_curve_n_vertices, green_curve_max_abs_dev_from_formula_mag = 0.00037 |
| CRTS end 20 d before the paper | 56591 − 56571 = 20 | X |

## Registered test (Table 1)

| Number | Value | Source |
|---|---|---|
| sigma_D | 0.089 | E.sigma_drw = 0.0889 |
| T_obs | -0.589 (abstract: -0.59) | E.T_obs |
| T g, T r | -0.54, -0.61 | E.T_zg_only = -0.545, T_zr_only = -0.614 |
| null T quantiles, tau 210 / 500 | -0.70/0.00/0.72; -0.53/0.00/0.55 | E.tau210/tau500.null_T_q01_q50_q99 |
| signal T quantiles | 0.30/1.00/1.72; 0.47/1.00/1.55 | E.tau210/tau500.sig_T_q01_q50_q99 |
| p_null | 0.971; 0.995 | E.tau210.p_null = 0.9714; tau500.p_null = 0.9946 |
| p_sig | 0 of 5000 (< 2e-4) | E.tau210.p_sig = 0, tau500.p_sig = 0 |
| power | 0.82; 0.97 | E.tau210.power_at_0.01 = 0.8192; tau500 = 0.9744 |
| Gaussian p_sig of the verifier | 2e-7 | V `verify/indep3.out`: "analytic p_sig 2.2e-07" (0.10 mag, tau 210) |
| phase rank, best shift, T there | 17 of 20; 0.60; 0.70 | E.phase_rank_of_zero, best_phase_shift, phase_scan_T[12] = 0.6952 |
| free-phase amplitude, phase | 0.060 mag; 0.49 cycle | E.free_phase_P741 = 0.0598, 0.487 |
| period scan peak | 1445 d, 0.100 mag | E.period_scan_best |

## Post hoc tests

| Number | Value | Source |
|---|---|---|
| T_CRTS all / clean | 0.50 / 0.48 | A.T_crts_all = 0.502, T_crts_clean = 0.484 |
| outliers removed | 1 | A.crts_n_outliers |
| CRTS amplitude at 741 d, phase | 0.050 mag; 0.010 cycle | A.crts_free_phase_P741 |
| CRTS best period, amplitude | 736 d, 0.051 mag | A.crts_refit.P, amplitude_mag = 0.0508 |
| RSS best / 741 / constant | 0.6196 / 0.6199 / 1.0070 | A.crts_refit.rss, rss_at_741, rss_const |
| residual rms, intra-night rms, sigma_c | 0.050, 0.036, 0.035 | A.crts_refit.resid_rms = 0.0497, intra_night_rms = 0.0356, sigma_drw_crts = 0.0347 |
| C_obs | -1.12 | A.C_obs = -1.1196 |
| Table 2 rows | as in the table | W[...].sd_P_hat, C_q01_q50_q99, p_persist (rounded) |
| p_persist range | 0.0055 to 0.0975 (abstract: 0.6% to 9.8%) | A.p_persist_min_max |
| CRTS-amplitude worlds | 0.064 to 0.098 | W A0.051_*: 0.0975, 0.081, 0.085, 0.064 |
| refit-period scatter | 15 to 72 d | W sd_P_hat over the 8 signal worlds: 15.2 to 72.1 |
| null world | 0.204 (20%) | W A0.000_sigc0.035_tau210.p_persist |
| Monte Carlo error column | sqrt(p(1-p)/2000) | X: 0.0135 -> 0.0026; 0.0055 -> 0.0017; 0.073 -> 0.006; 0.054 -> 0.005; 0.0975 -> 0.007; 0.081 -> 0.006; 0.085 -> 0.006; 0.064 -> 0.005; 0.204 -> 0.009 |
| mock counts | 11 and 27 of 2000 | X: 0.0055 × 2000; 0.0135 × 2000 |
| verifier second seed | 0.0153, 0.0077, 0.080, 0.057 | V `verify/indep3.out` (seed 4242, 3000 mocks) |
| Delta t in cycles | 4.4 to 8.0 | X: (58298.45 − 55009.50)/741 = 4.44; (60969.34 − 55009.50)/741 = 8.04 |
| phase error, sigma_P = 15 d | 0.09 to 0.17 cycle | X: 4.44 × 15.21/741 = 0.091; 8.04 × 15.21/741 = 0.165 |
| phase error, sigma_P = 72 d | 0.43 to 0.78 cycle (abstract: 0.1 to 0.8) | X: 4.44 × 72.12/741 = 0.432; 8.04 × 72.12/741 = 0.783 |
| period scan (Table 3) | as in the table | A.refit_scan_P_C_rss_amp |
| RSS 5% to 8% above minimum at 780-790 d | 0.6501/0.6196 = 1.049; 0.666/0.6196 = 1.075 | X |
| template at CRTS amplitude | a = 0.51; power 0.25; p_sig 0.0002 (1 of 5000) | A.preregistered_at_crts_amp: 0.508, 0.2478, 0.0002 |
| free-phase null fraction | 19% | E.posthoc.free_phase_amp_P741_p_null_tau210 = 0.188 |
| random-phase fractions | 7.6% (0.1 mag), 48% (0.051 mag) | A.ztf_free_amp_frac_le_obs_random_phase = 0.0755, 0.482 |
| verifier CRTS agreement | 0.0005 d, 0.00005 mag | V `VERIFY.md` check 6 |
| quote line | 303 | V `VERIFY.md` check 1; Z |
| run time of ci.sh | 56 s | clean-copy run, write stage, 2026-11-28 (2 threads) |

## Open issues of the last VERIFY.md (round 2) and where the paper fixes them

| Issue | Fix |
|---|---|
| W1. Do not use the `problem.json` significance sentence ("removes the sinusoidal half of the evidence"). | The sentence is not used anywhere in `release/`. Abstract, Section 5.2 and the Conclusion state the supported reading: the formula does not continue, and ZTF neither refutes nor supports a persistent 741 d signal. |
| W2. Title and abstract give both parts; the second part is marked post hoc; "refuted" only for the literal formula. | Title: "... fails on held-out ZTF data; post hoc, a weaker persistent 741-day signal is not excluded". Abstract: "Post hoc, we also tested ..."; "refuted" applies only to "the formula at its published amplitude, period and phase". Same in `README.md` and `result.json`. |
| W3. The published amplitude already disagrees with the CRTS points; the new ZTF information is the sign; p_sig = 0.0002 at the CRTS amplitude. | Abstract ("A part of this failure is not new ... The new information from ZTF is the sign of T"); Section 5.1, second paragraph (a = 0.51, p_sig = 0.0002, power 0.25). |
| W4. Monte Carlo error of p_persist; 11 and 27 mocks; second seed. | Table 2, column "error"; Section 5.2, paragraph after Table 2 (11 and 27 of 2000 mocks; verifier values 0.0153, 0.0077, 0.080, 0.057; one of eight worlds below 0.01 with both seeds). |
| W5. Do not use "0.14 cycle"; derive the phase error from sd_P with the arithmetic shown. | "0.14" is not used. Section 5.2, paragraph "The scatter of the refitted period ...": formula Δt σ_P/P², Δt = 4.4 to 8.0 cycles from the mean CRTS epoch, results 0.09-0.17 and 0.43-0.78 cycle. Arithmetic in this file above. |
| W6. Keep the limits of `RESULT.md`. | Section 7 (Limits): CRTS from the figure, unweighted, 20 d shorter; refit model is not GLSdeDRW; g and r are not V; one DRW for both bands; post hoc status; ZTF release name not confirmed; 1497 d signal not tested. ADS full-text search not run: Section 6, item "Prior work". |

## Changes in the write stage

- `checks/rerun.py`: added `MJD_END = 60970.0` to the ZTF filter, so that new ZTF epochs do not change the result. No point of the 2026-11-28 data is removed; the comparison with `data/expected.json` gives `OK`.
- `checks/plot.py`: new two-panel figure (CRTS and ZTF). Descriptive only.
