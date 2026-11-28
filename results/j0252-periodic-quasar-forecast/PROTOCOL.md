# PROTOCOL (pre-registered): forward test of the 4.4-yr periodicity of SDSS J025214.67-002813.7 on held-out ZTF data

Written 2026-11-28, before any held-out ZTF data were compared with the model.
What I saw before this commit: the ZTF light-curve file (IRSA, all epochs) was downloaded once.
I printed only the number of points per object and filter, the median magnitude per filter
(zg 21.25, zr 20.88, zi 20.60) and the first and last MJD. I did not plot it and did not compare it with any model.

## Claim
Liao et al. 2021, MNRAS 500, 4025, arXiv:2008.12317 (abstract): "we report discovery of a periodicity (P=1607±7 days)
at 99.95% significance [...] in the optical light curves of a redshift 1.53 quasar, SDSS J025214.67-002813.7 [...]
The light curves are best fit by a bursty model predicted by hydrodynamic simulations of circumbinary accretion disks."
Sec. 6: "The significance of a real periodicity should increase as more cycles are covered."
Table 2: r band, q=0.11 bursty model, P = 1466 (+64/-12) d.
Third party: Covino, Tobar & Treves 2022 (MNRAS 513, 2841, doi:10.1093/mnras/stac596): "it was conjectured that the quasar
SDSS J025214.67−002813.7 has a periodicity of ∼4.4 yr [...] the possibility that this is a chance result cannot be ruled out."

## Prediction under test
The paper gives no phase in numbers. I take the phase and shape from the paper's own best-fit model curve:
the thick r-band curve (q=0.11 bursty model, red-noise background) in Fig. 1 (arXiv source file
`burst_fit_J0252_rednoise_new-eps-converted-to.pdf`). `checks/digitize_model.py` digitizes it
(`data/model_r_digitized.json`, MJD 50909-58889). The template is the median of the digitized curve
in 50 phase bins, folded at P = 1466 d (Table 2, r band), with its mean removed. The prediction for
t > 58927 is template(phase(t)), so the paper's model continued at its own period.

## Data
ZTF public light curves, IRSA API `nph_light_curves`, POS=CIRCLE 43.061125 -0.470472 0.0006 deg (2.2 arcsec), CSV.
Held-out sample: filter zr, catflags = 0, MJD > 58927 (2020-03-19, the date of the accepted v8 manuscript; the paper's
data and plotted model end before this date). All ZTF object ids (oid) are used, each with its own free offset.
Secondary (descriptive only): zg with the same rules.

## Test statistic
T = weighted least-squares coefficient a in mag_i = c_oid + a * template(t_i) + noise, weights 1/magerr^2.
T = 1 means the data follow the predicted curve at full amplitude; T = 0 means no relation.

## Null and signal simulations (5000 each, fixed seed 20261128)
- Null: damped random walk (DRW) at the held-out epochs, tau = 716 d (Table 2, r band), plus Gaussian noise with each point's magerr.
  DRW rms sigma_D^2 = var(held-out mags) - mean(magerr^2), with a floor of 0.01^2. (This uses the data variance, not the template.)
- Signal: the same DRW plus template(t) at a = 1.
- p_null = fraction of null mocks with T_mock >= T_obs. p_sig = fraction of signal mocks with T_mock <= T_obs.

## Decision (fixed now)
- Support for the predicted periodicity: p_null < 0.01.
- Refutation of the prediction at its published amplitude and phase: p_sig < 0.01.
- Otherwise: inconclusive.
- Power check (known-answer injection): report the fraction of signal mocks with p_null < 0.01.
  If this power is below 0.5, I report that the held-out data cannot support the claim at this threshold.

## Placebo
Phase scan: T for the template shifted by phi*P, phi = 0, 0.05, ..., 0.95. Report the rank of phi = 0 among the 20 values
and the phase with the largest T. Descriptive, not part of the decision.

## Known limits (stated before the result)
- The template comes from a digitized raster figure; digitization error is about 0.01 mag and a few days.
- ZTF magnitudes are not on the DES system; the free offset absorbs a constant shift, not a color term.
- The test covers only the q=0.11 bursty model in r band, not the sinusoidal model (its phase is not recoverable from the figure with confidence).

## Addendum 1 (2026-11-28, solve stage, round 2). Post hoc. Written before the computations below were run.

### Why
The verifier (`VERIFY.md`, round 1) found two problems with the noise model of the original test:
1. The quasar is at the ZTF detection limit. ZTF lists a point only when it is detected (S/N >= 4). The detected magnitudes
   follow the limiting magnitude. The original mocks have no censoring.
2. The original DRW rms (0.119 mag) comes from the variance of the held-out points. It is not varied.

### What I saw before this addendum
- The verifier's numbers in `VERIFY.md`: with censoring, median T at a = 1 is 0.3-0.75; p_sig <= 0.002 for DRW sigma <= 0.17
  and 0.006-0.017 at sigma = 0.25 (tau = 716 d); placebo T sd 0.31-0.42 on 52 nearby objects.
- The quasar's detection fraction per limiting-magnitude bin on its ZTF quadrant (about 28% of 348 good exposures).
- The ratio of the quasar's reported flux error to F(limitmag)/5 (median 1.43 on field 402).
- The paper's published DRW posterior for r band (Fig. "DRW model parameter estimates", source file `chain_4band.pdf`):
  sigma = 0.15 (+0.10/-0.03) mag, log10 tau = 2.9 (+0.7/-0.2). I digitized its 68% and 95% contours from the vector PDF
  (`checks/digitize_drw.py`, `data/drw_posterior_r.json`). At tau = 716 d the 95% contour spans sigma 0.117-0.177.
- I did not run the censored model below on the quasar before this commit.

### Censored forward model (fixed now)
- Epochs: all post-cutoff zr exposures of the two ZTF quadrants that contain the quasar (field 402 ccd 15 q 4 and field 1446
  ccd 5 q 4), from an IRSA cone of 0.08 deg, kept when at least 5 other objects have catflags = 0 on the exposure.
  Exposures where the quasar row has catflags != 0 are dropped. Each exposure has its `limitmag` (5-sigma).
- Flux noise at an exposure: s_i = k * F(limitmag_i) / 5, F(m) = 10^(-0.4 (m - 21)). k = median over the quasar's detections
  of magerr * F(mag) / (1.0857 * F(limitmag) / 5).
- A mock point: true mag mu_i = m0 + a * template(t_i) + DRW_i; measured flux f_i = F(mu_i) + s_i * N(0,1).
  The point is listed only if f_i / s_i >= 4. Its mag is -2.5 log10(f_i) + 21 and its magerr is 1.0857 s_i / f_i.
- m0 is not known. For each (a, sigma, tau), m0 is set so that the mean number of listed points equals the observed 97.
- Statistic: the same T as the protocol (weighted LS, one free offset per ZTF object), on listed points only.
- p_sig = fraction of a = 1 mocks with T <= T_obs. p_null = fraction of a = 0 mocks with T >= T_obs. 4000 mocks each.

### DRW parameters (fixed now)
- Grid at tau = 716 d: sigma = 0.10, 0.119, 0.13, 0.15, 0.17, 0.20, 0.25, 0.30.
- The paper's published r-band posterior: 24 points on the 95% contour and 12 on the 68% contour (equal steps along the path),
  plus the best fit (tau = 10^2.9 d, sigma = 0.15). This posterior is from the paper's DRW-only fit. It contains the variance of
  the periodic signal. So it overstates the DRW amplitude under "model + DRW", and the test is conservative.

### Decision (fixed now)
- Refuted (robust): p_sig < 0.01 at every point of the published 95% contour.
- Refuted (at the best fit only): p_sig < 0.01 at the best fit, but not on the whole 95% contour. Report the part of the contour
  where p_sig >= 0.01.
- Not refuted: p_sig >= 0.01 at the best fit.
- Power: the fraction of a = 1 mocks with p_null < 0.01, at the best fit.

### Model checks (fixed now)
- The mocks must reproduce the observed detection fraction per limitmag bin and the slope of mag against limitmag.
  I report both. A large mismatch is a stated limit; it does not change the decision rule.
- Placebo calibration: the verifier's 52 nearby objects (field 402, >= 40 held-out points, median mag 20.6-21.2). For each, the
  same censored model with sigma = 0 and m0 matched to its number of points gives the expected scatter of T. z = (T - median)/sd.
  If the robust sd of z (1.4826 MAD) is above 1.2, I multiply the deviation of each a = 1 mock T from its median by that factor
  and report p_sig again with this inflation. Both numbers are reported. The decision uses the inflated one if it is computed.
- Depth diagnostics on the data: corr and slope of mag against limitmag; T with limitmag as a covariate; T on limitmag > 21.3.
- Data-based sigma: the sigma at tau = 716 d for which the mocks give the observed sd of the listed magnitudes
  (after per-object means), under a = 0 and under a = 1. Descriptive only.

### Scope (fixed now)
The claim covers the r-band q = 0.11 fit continued in phase. Descriptive: p_sig with the censored model at the best-fit DRW
for the other Table 2 periods: 1454, 1476 (joint griz), 1506 (i), 1511 (g), 1530, 1562 (z), 1604 (joint upper 1 sigma), 1607 (GLS).

## Correction (2026-11-28, write stage)
Addendum 1 quotes the r-band DRW label as log10 tau = 2.9 (+0.7/-0.2). The r-band label of the paper's figure is
2.9 (+0.5/-0.2); +0.7/-0.2 is the z-band label (found by the verifier, `VERIFY.md` round 2, issue W1). No computation used
this error bar. The best fit (2.9, 0.15) and the digitized contours are correct. The addendum text above is not changed.
