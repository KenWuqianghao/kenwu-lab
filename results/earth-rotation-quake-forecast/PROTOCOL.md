# Pre-registered protocol: scoring the 2017 Bilham–Bendick forecast of more global M≥7 earthquakes

Written 2026-11-25, stage solve, before any earthquake catalog was downloaded or counted in this session.
The git commit time of this file is the evidence of pre-registration.

## 0. Disclosure of prior exposure

- The prior_art session saw informal annual counts (USGS statistics table and Wikipedia) of M≥7 events:
  2018: 17, 2019: 10, 2020: 9, 2021: 19, and a long-term mean of about 16 per year (USGS FAQ).
- `problem.json` records an unchecked subagent count: 66 M≥7 events in ComCat for 2018–2022 and 73 for 2013–2017.
- So the direction of the headline result is foreseeable: the 2018–2022 rate looks near or below average.
- In this session, before this protocol, I downloaded and looked at the predictor only: the Earth-rotation
  (LOD) series. The annual-mean C02 LOD increases in each year 2011–2016 and decreases in 2017–2022.
  This agrees with the "deceleration episode that commenced in 2011" in the source. I did not look at any
  earthquake data in this session.
- The decision rules below do not depend on these numbers. The tests are fixed so that a +25 % rate
  could have given "supported", and the power of each test is reported (known-answer injection).

## 1. The claim

Source: Bilham & Bendick, GSA Annual Meeting 2017, Paper 300667 (doi:10.1130/abs/2017AM-300667).

- C1 (forecast): "the world has now entered a period of enhanced global seismic productivity with a
  duration of at least five years", where "enhanced" refers to the "25-30% increase in annual numbers of
  Mw≥7 earthquakes" in the same abstract. Press reports (Science, 2017-10-30) give the forecast as about
  17 to 20 events per year from 2018.
- C2 (mechanism statistic): Earth's angular deceleration (d[LOD]/dt > 0) precedes global M≥7
  seismic productivity by 5–6 years.

## 2. Data

- Catalog: USGS ComCat, FDSN event service `https://earthquake.usgs.gov/fdsnws/event/1/query`,
  `format=csv&eventtype=earthquake&minmagnitude=7&orderby=time-asc`, worldwide, all depths,
  1900-01-01T00:00:00 to 2026-01-01T00:00:00 UTC. Magnitude = the ComCat preferred `mag` field. Queried on
  the date recorded in `THIRD_PARTY.md`. A snapshot (id, time, lat, lon, depth, mag, magType) is stored in
  `data/`. Years are UTC calendar years of the origin time.
- LOD: Paris Observatory EOP C02 (`https://hpiers.obspm.fr/eoppc/series/longterm/eopc02.1830-now`),
  column LOD (s), 100-day steps. Linear interpolation to 1-day steps, then calendar-year mean.
  Cross-check: IERS EOP 20 C04 daily LOD annual means 1962–2024 (correlation reported).
- Deceleration mask: M(y) = 1 if the annual-mean LOD of year y is larger than that of year y−1 (Earth
  slowed down during year y), else 0.

## 3. Primary test P1: the five-year forecast (decides the verdict for C1)

- Baseline rate λ0 = number of M≥7.0 events in 1900–2017 divided by 118.
- Overdispersion: fit a negative binomial (NB) to the 118 annual counts by the method of moments,
  var = μ + μ²/k. If var ≤ mean, use Poisson (k = ∞).
- Forecast level λF = 1.25 λ0 (the lower end of the stated 25–30 %).
- Window W = 2018-01-01 to 2022-12-31 (5 years). N = number of M≥7.0 events in W.
- Model of a 5-year sum with annual rate λ: NB with mean 5λ and size 5k (independent years).
- p_refute = P(X ≤ N), X ~ NB(mean 5λF, size 5k).
- p_support = P(X ≥ N), X ~ NB(mean 5λ0, size 5k).
- Verdict for C1:
  - REFUTED (the stated size of the increase) if p_refute < 0.05.
  - SUPPORTED if p_support < 0.05.
  - INCONCLUSIVE otherwise.
- Also reported: N/5 versus λ0, the ratio (N/5)/λ0 with a 95 % interval (NB), and the counts per year.

### Secondary analyses for P1 (reported, they do not change the primary verdict)

1. Poisson instead of NB.
2. Threshold M≥7.1 (the completeness level of Bendick & Bilham 2017 GRL).
3. Declustered catalog (Gardner–Knopoff windows applied within the M≥7 set: process events by
   decreasing magnitude; remove each smaller event within the distance window
   d = 10^(0.1238 M + 0.983) km and within the time window t = 10^(0.032 M + 2.7389) days,
   before or after the larger event). Baseline, dispersion and N are all recomputed on the declustered set.
4. Baseline 1973–2017 (modern instrumental era) instead of 1900–2017.
5. Window 2017–2021 instead of 2018–2022.
6. Forecast level 17 per year (press figure) instead of 1.25 λ0.
7. Autocorrelation-robust check: the empirical distribution of all 114 sliding 5-year sums S in 1900–2017.
   Report the fraction of windows with 1.25·S ≤ N (empirical p_refute) and with S ≥ N (empirical p_support).
8. Comparison with the preceding window 2013–2017 (conditional binomial test of the two counts, reported
   only as a description).

### Controls for P1

- Placebo windows: apply the P1 rule (with the 1900–2017 baseline and k) to every historical 5-year window
  that starts in 1900–2013. Report the fraction classified REFUTED and SUPPORTED. This shows how often a
  random past window would get each verdict.
- Known-answer injection: simulate 10 000 windows with NB annual counts (rate λ0·r, size k) for
  r = 1.00 and r = 1.25 (and r = 1.30). Report the fraction classified REFUTED and SUPPORTED for each r.
  This gives the false-verdict rates and the power of P1.

## 4. Test P2: held-out lag statistic (decides the verdict for C2 on new data)

- Held-out years: 2018–2025 (8 complete years after the source). Lag L = 5 (primary), L = 6 (secondary).
- Predicted-enhanced years: years y in 2018–2025 with M(y − L) = 1.
- Statistic D = mean annual M≥7 count in predicted-enhanced years minus mean in the other held-out years.
  Also the rate ratio and the share of events in predicted-enhanced years (the "binary mask" percentage)
  versus the share of years.
- p-value: exact one-sided permutation test over all assignments of the same number of "enhanced"
  labels to the 8 years (large D is evidence for C2).
- Verdict for C2 on held-out data: SUPPORTED if p < 0.05 at L = 5. NOT SUPPORTED otherwise.
  If every assignment gives p ≥ 0.05 by construction (too few years), report that the test has no power.
- Power: known-answer injection with NB annual counts (rate λ0, size k) and a ×1.25 rate in
  predicted-enhanced years; 10 000 simulations; report P(p < 0.05).
- Secondary: declustered catalog; M≥7.1.

## 5. Test P3: in-sample re-run, 1900–2017 (description, no verdict)

- For L = 0..9: share of 1900–2017 M≥7 events in years with M(y − L) = 1, and the rate ratio.
- Null 1 (circular-shift placebo): shift the mask series M over 1900−L..2017−L circularly by every offset
  s with 10 ≤ s ≤ 108 years; report the one-sided percentile of the true lag statistic.
- Null 2 (random catalogs): 10 000 catalogs with the same number of events, years drawn uniformly over
  1900–2017; report the mean and SD of the share and the percentile of the observed share.
- The same for the declustered catalog.
- Max-over-lags: report the percentile of max over L = 0..9 against the circular-shift null of the max.
- Known-answer check of the code: a synthetic catalog with an injected ×1.25 rate at lag 5 must show a
  peak at L = 5.

## 6. Reproduction

- `checks/rerun.py` downloads ComCat and C02 (and C04), recomputes every number, and compares with
  `data/expected.json`. Counts are compared exactly. If ComCat changes the catalog later, the script reports
  the difference.
- Random seeds are fixed.

## 7. What each outcome means

- P1 REFUTED: the 2018–2022 M≥7 rate is significantly below the forecast +25 % level. This refutes the
  forecast at its stated size. It does not refute every possible link between Earth rotation and seismicity.
- P1 SUPPORTED: the 2018–2022 rate is significantly above the 1900–2017 baseline. This is an
  association; it does not prove the mechanism.
- P1 INCONCLUSIVE: the data in one 5-year window cannot separate the two levels.
- P2 is a small held-out test (8 years). A NOT SUPPORTED result with low power is weak evidence.

## Addendum 1 (2026-11-25, write stage, after all results were known)

- Deviation found by the verify stage (VERIFY.md, W1). §4 states 10 000 simulations for the P2 power.
  The solve-stage code used 2000 simulations for the P2 power (0.172) and for the false-positive rate (0.028).
  The reason is not recorded. It was an implementation error, not a decision.
- Correction. The released `checks/rerun.py` also runs the P2 power and the false-positive rate with
  10 000 simulations, with a separate random generator (seed 20261125), so that no other number changes.
  Result: power 0.170, false-positive rate 0.034. The paper reports these values as the pre-registered
  computation and gives the 2000-simulation values only as the solve-stage run.
- No decision rule changed. The P2 verdict does not depend on the power.
- The write stage also added descriptive computations that the protocol does not list: the P1 decision
  thresholds in N, p_refute for other forecast levels, and the P2 lag-5 test with a mask from C04. They
  are labelled as additions in the paper and do not change any verdict.
