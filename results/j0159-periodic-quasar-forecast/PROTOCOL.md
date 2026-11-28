# PROTOCOL (pre-registered): forward test of the 741-day sinusoid of the quasar SDSS J0159+0105 on ZTF data

Written 2026-11-28, before any ZTF data for this object were downloaded.

## Claim
Zheng, Butler, Shen et al. 2016, ApJ 827, 56, arXiv:1512.08730, Sect. 4.1:
"Only the sinusoidal signal, which can be fitted as $V$ = 0.1 $\times$ sin (2$\pi$(t - 53413.09 )/741) + 16.59
(see Fig.~\ref{ppn129lc}-a), is also confirmed by the additional ACF analysis ($P$\,$>$\,99\%)."
Abstract: "we detect two significant (at $P>99\%$) periodic signals at $\sim$\,741 day and $\sim$\,1500 day
from the 8.1-year Catalina V-band light curve of this quasar."
Object: SDSS J015910.058+010514.53 (RA 29.791908, Dec +1.087369 deg), z = 0.217. The CRTS data end at MJD 56591.
t is MJD. The paper gives no period uncertainty for the 741 d signal.

## Prediction under test
template(t) = 0.1 * sin(2*pi*(t - 53413.09)/741) mag (the paper's own fit, continued). All ZTF data are
after MJD 58190, so they are 1600+ days after the last CRTS point and fully held out.

## Data
ZTF public light curves, IRSA API `nph_light_curves`, POS=CIRCLE 29.791908 1.087369 0.0006 deg (2.2 arcsec), CSV,
the newest release that IRSA serves on the download date. Filters zg and zr. Keep catflags == 0 points.
Each ZTF object id (oid; one filter, one field/CCD) gets its own free offset. zi is not used.

## Test statistic (primary)
T = weighted least-squares coefficient a in mag_i = c_oid + a * template(t_i) + noise, weights 1/magerr^2,
on the zg and zr points together. T = 1: data follow the published curve at full amplitude and phase. T = 0: no relation.

## Null and signal simulations (5000 each, numpy seed 20261128)
- Null: damped random walk (DRW) at the observed epochs, tau = 210 d (paper Sect. 4.1, "covariance time scale tau_0 ~ 210 day"),
  one DRW shared by both filters, plus Gaussian noise with each point's magerr.
  DRW rms: sigma_D^2 = var(residual mags after the per-oid means are removed) - mean(magerr^2), floor 0.01^2.
- Signal: the same DRW plus template(t) at a = 1.
- p_null = fraction of null mocks with T_mock >= T_obs. p_sig = fraction of signal mocks with T_mock <= T_obs.
- Robustness (descriptive): repeat both with tau = 500 d.

## Decision (fixed now)
- Support for the predicted sinusoid: p_null < 0.01.
- Refutation of the prediction at its published amplitude and phase: p_sig < 0.01.
- Otherwise: inconclusive.
- Power (known-answer injection): fraction of signal mocks with p_null < 0.01. If power < 0.5, I report that the data
  cannot decide at this threshold.

## Placebo and descriptive checks
- Phase scan: T for template(t - phi*741), phi = 0, 0.05, ..., 0.95. Report the rank of phi = 0 among the 20 values.
- Free-phase fit at P = 741 d: amplitude and phase of the best sinusoid (per-oid offsets). Descriptive.
- Period scan: free-phase sinusoid amplitude for P in 300..1500 d. Descriptive only, no significance claim.

## Known limits (stated before the result)
- ZTF g and r are not CRTS V. A quasar's amplitude is usually larger in g than in r. The free offsets absorb constant shifts only.
- A period error of 1% (7 d) moves the phase by about 0.1 cycle over the 10 cycles to the ZTF epochs. The phase scan and
  the free-phase fit show this case.
- This tests only the 741 d sinusoid, not the 1497 d ACF signal (the paper gives no ephemeris for it).

## Addendum 1 (2026-11-28, solve stage after verify round 1). Written after the results were seen.

What I saw before I wrote this addendum: the primary result (T_obs = -0.589, p_sig < 2e-4, `RESULT.md`), and all
numbers in `VERIFY.md` and `verify/*.out`. These include the CRTS amplitude 0.050 mag from the figure points, the
ZTF coefficient C_obs = -1.12 on the continued CRTS refit, and refit-world fractions of 0.03 to 0.28.
So every test in this addendum is post hoc. The pre-registered rule and its decision above do not change.

The addendum adds these computations to `checks/rerun.py`. They are fixed here so that the rerun is exact.

A1. CRTS data (positive control). Download the arXiv source of arXiv:1512.08730 and read `lc.eps` (Fig. 1a).
Take the 252 open diamonds of panel (a) (the raw CRTS V points). Axis calibration from the tick marks:
x = 4554 is MJD 54000, x = 8431 is MJD 54500; y = 12839 is V 16.7, y = 14437 is V 16.2. Check the calibration on the
green curve of panel (a): its vertices must follow the published formula. Compute on CRTS (unweighted, one offset):
T_CRTS = coefficient on the published template; the free-phase amplitude and phase at 741 d; the best period in 600-900 d.
Remove points more than 0.3 mag from the median (one point) for the fits A1 to A3. Report T_CRTS with and without it.

A2. Refit forward test. Statistic C = weighted least-squares coefficient of the ZTF data (per-oid offsets) on the
continued CRTS refit. The CRTS refit is the least-squares sinusoid with free amplitude, phase and offset, at the
period with the smallest residual sum of squares on the grid 600, 602, ..., 900 d. C = 1: ZTF follows the CRTS refit.
World "persistent sinusoid": V(t) = A sin(2 pi (t - 53413.09)/741) at all times, plus a DRW (one realization for CRTS and
an independent one for ZTF, because the 1700 d gap is many tau) plus white noise.
- CRTS noise: DRW rms sigma_c and white noise rms w. w = rms of the residuals inside a night (pooled over nights with
  2 or more points). sigma_c^2 = var(CRTS refit residuals) - w^2. Also sigma_c = sigma_D(ZTF) = 0.089 mag.
- ZTF noise: DRW with sigma_D (ZTF) and each point's magerr, as in the main test.
- Grid: A in {0.1 mag, A_CRTS (the A1 refit amplitude)}, sigma_c in {from CRTS, 0.089 mag}, tau in {210, 500} d.
  2000 mocks per world, numpy seed 20261129.
- p_persist = fraction of mocks with C_mock <= C_obs.
- Rule: if p_persist < 0.01 in all 8 worlds, a persistent sinusoid at the published period and phase is refuted.
  Otherwise it is not refuted by these data.
- Null control: the same refit chain with A = 0 (DRW only), sigma_c from CRTS, tau 210 d; report the fraction with C_mock <= C_obs.

A3. Period scan with a CRTS refit at each period (replaces the post hoc scan with T0 fixed): for P = 680, 690, ..., 810 d,
fit the CRTS points at that fixed P (free amplitude, phase, offset), continue to ZTF, report C and the CRTS RSS.

A4. Power of the pre-registered test at the CRTS amplitude: the signal mocks with the template scaled to a = A_CRTS/0.1.
Report the fraction with T_mock >= the 99% null quantile, and p_sig at that amplitude.

A5. ZTF free-phase amplitude at 741 d against a random-phase sinusoid (amplitude 0.1 mag and A_CRTS) plus DRW (tau 210 d,
2000 mocks): fraction with amplitude <= the observed amplitude.

A6. Data versions. Store the SHA-256 of the IRSA CSV and of `lc.eps` in `data/expected.json`. If the IRSA download
has a different checksum, `rerun.py` prints that the ZTF release changed; it then compares the numbers as before.
