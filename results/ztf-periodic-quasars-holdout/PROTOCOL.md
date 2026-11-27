# Pre-registered protocol: forward test of the Chen et al. (2024) ZTF periodic-quasar candidates

Date: 2026-11-24. Stage: solve. This file is committed before any test-window score of a real light curve is computed.

## 1. Claim under test

Chen et al. (2024, MNRAS 527, 12154; arXiv:2206.11497) find 86 quasars with significant sinusoidal periodicity (periods about 500-950 d) in ZTF DR11 r-band light curves, with the single power-law (SPL) red-noise model as the null ("86 (SPL) candidates"). Three of them (SDSS J083111, SDSS J155304, SDSS J135830) are also periodic in extended archival light curves.

If a candidate is truly periodic, the sinusoid fitted to the DR11 data predicts the light curve after DR11. If the periodicity is red noise, the prediction has no more skill than for red-noise mocks that were selected in the same way.

Question: do the frozen DR11-window sinusoids predict the post-DR11 ZTF light curves better than red noise does?

## 2. Data

- Candidates: the 86 SPL candidates, names from the Appendix C figures of the arXiv source (`prior_art/appendixC_candidate_names.txt`). 85 SDSS names give J2000 positions. `2QZJ131914+0027` is the 2QZ object J131914.8+002709 (unique 2QZ catalogue entry in the box allowed by the truncated name). Redshift and PSF r magnitude come from SDSS DR14Q (`DR14Q_v4_4.fits`) for the 85 SDSS objects and from the 2QZ catalogue for the 2QZ object. Table: `data/candidates.csv`.
- Placebo: 4 DR14Q quasars per candidate (344 in total), drawn without replacement with seed 20261124 from DR14Q quasars with |r - r_cand| < 0.3 mag, |z - z_cand| < 0.3, r <= 20, Dec > -28 deg, and more than 10 arcsec from every candidate. Table: `data/placebo.csv`. The placebo is not selected for periodicity.
- Light curves: ZTF r band (`filtercode = zr`) from the IRSA light-curve API (`nph_light_curves`, `CIRCLE ra dec 0.000833`, that is 3 arcsec, the paper's radius), all object IDs inside the circle, accessed 2026-11-24. This is the current public release (epochs to about MJD 60968, October 2025). Keep only `catflags == 0` and `magerr > 0`.

## 3. Windows

- Training window (the DR11 public selection, from the DR11 release notes of 2022-05-09): epochs with `programid == 1` and 58194.0 <= MJD <= 59647.0, plus epochs with `programid` in {2, 3} and 58194.0 <= MJD <= 59159.0.
- Test window: all epochs with MJD > 59647.0 (any programid).
- Epochs with `programid` in {2, 3} and 59159 < MJD <= 59647 are not used. They were not in DR11 and they are not after DR11.

## 4. Light-curve processing (each window separately)

1. Fit a 15th-order polynomial to the epochs. Remove points more than 3 standard deviations of the residuals from the fit (one pass). This is the paper's recipe.
2. Bin in 20-day bins on a fixed grid that starts at MJD 58194.0. Bin value = mean magnitude; bin error = standard error of the mean (the epoch error if the bin has one point); bin time = mean epoch time. Errors below 0.001 mag are set to 0.001 mag.
3. Exclusion: an object with fewer than 40 training bins (the paper's cut) or fewer than 10 test bins is excluded from all tests. The number of excluded objects is reported.

## 5. Training fit (frozen before the test window is used)

- Unweighted generalised Lomb-Scargle periodogram (offset plus sinusoid) of the training bins, frequency grid from 1/T_span to 1/50 d in steps of 1/(10 T_span), T_span = training time span. This is the paper's period range (50 d to T_span).
- P = period of the highest peak. Least-squares fit y = c + a cos(2 pi t/P) + b sin(2 pi t/P) at fixed P. xi = (a^2 + b^2) / (2 var(residuals)) (the paper's S/N).
- Frozen template: s(t) = a cos(2 pi t/P) + b sin(2 pi t/P).

## 6. Test score

- Primary score k: the ordinary least-squares slope of the test-window bin magnitudes on s(t) at the test bin times, with a free offset. k = 1 means the frozen sinusoid continues with the same amplitude and phase. k = 0 means no predictive skill. A free offset is used because quasar mean levels drift.
- Descriptive only: the phase shift and amplitude ratio of a sinusoid refitted to the test window at the frozen P.

## 7. Null distributions (per object)

- DRW null (primary): maximum-likelihood damped random walk (sigma_d, tau_d in [10, 20000] d, profiled mean) fitted to the training bins with their errors. Mocks: exact DRW draws at the training and test bin times, plus Gaussian noise with the bin errors, plus the training mean.
- SPL null (secondary): Timmer-Koenig power-law noise, PSD slope beta = 3.0 (typical of the paper's SPL slopes), 5 d grid, length 5 times the full span, random start, sampled at the bin times. Each mock is scaled so that its training-window standard deviation equals sqrt(var(training bins) - mean(error^2)). Plus noise and mean as above.
- Each mock goes through Sections 5 and 6 unchanged (its own GLS period and frozen template, then its own k).
- Conditioning on selection: a mock enters the null only if it looks at least as periodic as the object in training: xi_mock >= min(xi_obs, 4.0) and |P_mock/P_obs - 1| < 0.2. Mocks are drawn in chunks of 20,000 until at least 1,000 are accepted or 300,000 are drawn. If fewer than 200 are accepted, the object uses the unconditioned null (all of the first 20,000 mocks) and is flagged.
- Per-object p-value: p = (1 + number of null k >= k_obs) / (1 + number of null k). One-sided: only skill (k large) counts.

## 8. Primary tests and decision rule

Let n_C = number of analysed candidates, N_C = number of candidates with p_DRW < 0.05; n_P and N_P the same for the placebo.

- T1 (candidates against the DRW null): one-sided binomial test, P(X >= N_C) with X ~ Binomial(n_C, 0.05).
- T2 (candidates against the placebo): one-sided Fisher exact test that the fraction N_C/n_C is larger than N_P/n_P. The placebo goes through the identical pipeline, so T2 does not depend on the null model being right.

Decision:
- **Supported** (the candidate population shows forward predictive periodicity): T1 p < 0.01 and T2 p < 0.01.
- **Not supported** (null result): T1 p >= 0.01. In this case we also report the 95% upper limit on the fraction f of candidates that are strict sinusoids at their fitted training amplitude (Section 9).
- **Inconclusive**: T1 p < 0.01 and T2 p >= 0.01 (the placebo shows the DRW null is miscalibrated).

## 9. Controls and secondary analyses (reported, not used for the decision)

1. Placebo calibration: fraction of placebo with p_DRW < 0.05 (expected 0.05 if the DRW null is calibrated); same for p_SPL.
2. Alternative-hypothesis power per candidate: 2,000 mocks = frozen sinusoid + DRW fitted to the training residuals + noise, through the same pipeline. Power_i = fraction of alternative k above the 95th percentile of that object's null. Expected N_C if a fraction f is truly periodic: sum_i [f power_i + (1 - f) 0.05]. f_95 = the smallest f for which P(X <= N_C) <= 0.05 under a binomial with that mean. Caveat stated in advance: fitted training amplitudes are biased high by selection, so these powers are optimistic.
3. Real-data injection (known answer): add each candidate's frozen template to the raw epochs of its first matched placebo (all epochs, both windows), then run the full pipeline. Report the fraction with p_DRW < 0.05.
4. SPL null results (p_SPL, binomial and Fisher tests in the same form). Blind checks on 5 candidates before this commit showed near-zero power for the beta = 3 SPL null, so a null SPL result carries little information.
5. Stouffer Z of the per-object p-values, candidates and placebo.
6. Mann-Whitney test of k, candidates against placebo, and against the placebo subset with xi_obs > 4 and N_cycle > 1.5 (placebo that pass the paper's first GLS cut).
7. Named candidates SDSS J083111.23+123107.8, SDSS J155304.40+240255.1, SDSS J135830.46-012255.7: k, p_DRW, p_SPL, phase shift, each reported. A named object counts as forward-confirmed if p_DRW < 0.05/3.
8. Period check: refit P against the 5 published P_GLS values of candidates in the arXiv Table 1 excerpt (J002500.42 788.8 d, J002504.53 736.2 d, J003858.53 736.2 d, J004039.79 626.6 d, J004744.03 688.6 d).

## 10. What was seen before this commit

- The 86 candidate light curves were downloaded. For 5 candidates (C01-C05) the training-window fit, DRW fit, null distributions and alternative power were computed in a blind mode that does not score the real test window. Refit periods: 783, 740, 739, 630, 698 d against published 788.8, 736.2, 736.2, 626.6, 688.6 d. DRW power 0.25-0.98; SPL power 0.0.
- Synthetic known-answer checks on C01's sampling: a 700 d sinusoid (0.1 mag) gave k = 1.08, p_DRW = 0.003; a pure DRW curve gave k = 0.62, p_DRW = 0.09.
- No real test-window score (k, phase or p-value) was computed for any object.

## 11. Code and reproduction

- `checks/fetch_data.py` downloads DR14Q, the 2QZ catalogue and the ZTF light curves and builds the samples.
- `checks/qpo.py` has the methods; `checks/analysis.py` runs the per-object test; `checks/summarize.py` computes the tests in Sections 8 and 9; `checks/rerun.py` runs everything and compares with `data/expected.json`.
- Random seeds: per object, derived from the object ID; placebo draw seed 20261124.
