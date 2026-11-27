# Protocol: Hektor and Ganymed on Harvard plates before their first observation

Written and committed before any cutout of these plates was downloaded or seen. The commit time is the evidence.

## Claims under test
- (624) Hektor: JPL SBDB `first_obs` 1907-02-11. Earliest known image of any Jupiter Trojan: (12126) Chersidamas,
  1904-09-13 (SBDB `first_obs`, lowest of all TJN objects, checked 2026-11-27).
- (1036) Ganymed: JPL SBDB `first_obs` 1924-10-23.
Question: does a source appear at the predicted position on DASCH plates taken before these dates?

## Plates (fixed)
`src/plates.py`: 5 Hektor plates (b series, Arequipa, 1899-1901) and 6 Ganymed plates (i and ac series, Cambridge,
1898-1899). Selection rule in that file; it was applied to DASCH coverage lists before any image was seen.

## Predictions (fixed)
`data/predictions.json` from `src/predict.py`: JPL Horizons astrometric RA/Dec, topocentric for MPC site 800
(Arequipa) or 802 (Cambridge), every 5 min from DASCH midpoint -2 h to +2 h. Sun altitude at all midpoints < -24 deg.

## Measurement and decision (fixed)
`src/measure.py`, as committed here. Search region: predicted track within +-1 h of the DASCH midpoint, buffer 10"
(Hektor) or 15" (Ganymed); catalogued ATLAS stars masked. Statistic S = max of the noise-normalised z image in the region.
Pass: S >= 6 (Hektor), S >= 10 (Ganymed). Null rate p0 per plate from 300 copies of the region at random offsets
of 90"-420" on the same cutout. An object is "detected" if at least 2 plates pass and the Poisson-binomial
probability of at least that many passes under p0 is below 0.001. Otherwise "not detected".
Reported without a rule: peak offset along and across the track, astrometric fit quality.

## What counts
- Detected: the earliest passing plate is a candidate earliest image; it needs expert examination of the plate.
- Not detected: report the S values and p0; no claim.
Any change after the data are seen goes into a dated addendum that says what was seen first.

## Addendum 1 (2026-11-27, after the pre-registered run; nothing in the rules above was changed)
What the pre-registered run gave (`data/results.json`, commit after this addendum):
- Ganymed: 3 of 6 plates pass (i21050 S=23.3, i21576 S=33.1, i21780 S=16.0); P_null = 5.1e-4 -> "detected".
  Earliest passing plate: i21050, 1898-08-14 07:12 UT, peak 1.2" from the predicted midpoint position.
- Hektor: 2 of 5 pass, both 1901 (b28276 S=7.8, b28503 S=6.3); P_null = 0.029 -> "not detected".
  Both 1899 plates fail (b23074 S=3.2; b23499 S=-0.3, prediction 14.6" from a catalogued B=12.7 star, masked).
Post hoc, exploratory (`src/stamps.py`, `src/shapes.py`): z within 4" of the prediction vs 2000 random points
(`data/posthoc_position_test.json`); source shapes match the star shapes on the same plates (PSF, not trails);
image stamps in `data/stamps.png`. These do not change the verdicts above.

## Round 2 (2026-11-27, pre-registered before any round-2 image was downloaded or seen)
Question: is Hektor at its predicted position on DASCH plates before 1907-02-11 that round 1 did not use?
Plates: `PLATES2` in `src/plates.py` (8 plates, 1897-1905; rule in that file). Predictions: `data/predictions2.json`
(`src/predict.py 2`; site 800 Arequipa for the a and b series).
Measurement: `src/measure2.py` as committed here. Primary statistic per plate: z5 = max z within 5" of the predicted
midpoint position after the astrometric refit; p from 2000 random unmasked points on the same cutout. A plate whose
predicted point lies in a catalogued-star mask is "not measurable".
Decision: Fisher combination of p over measurable plates. "Detected" if p_comb < 0.001 and at least 2 plates have
p < 0.01. Record relevance: a plate before 1904-09-13 with p < 0.01 is a candidate for the earliest Jupiter Trojan image.
Note: `src/measure2.py` was tested on the round-1 Hektor plates (already seen) before this commit; that run
(p_comb 1.3e-6, b23074 p = 0.009, b28276 p = 0.0025, b28503 p = 0.0005, b23499 not measurable) is a code test with a
statistic chosen after round 1. It is not evidence and is not part of the round-2 decision.

## Addendum 2 (2026-11-27, after the round-2 run)
Changes after the pre-registration commit, before measurement: `src/fetch.py` skips a plate when DASCH returns 422
("plate a06535 solnum 0 does not overlap the target region"), and `src/measure2.py` records such a plate as
"not covered". The coverage list had been made at a mid-window position, so a06535 does not contain Hektor.
Result (`data/results2.json`): 6 measurable plates, p_comb = 0.0028, no plate with p < 0.01 -> "not detected".
Smallest p: b26258 (1900-09-21) and b28302 (1901-08-24), both 0.0145. b23969 is inside a catalogued-star mask.

## Addendum 3 (2026-11-27, after both decisions; no decision changed)
- `src/astrometry.py`: positions of the source on the five Ganymed plates (a measurement, not a test), tied to ATLAS
  stars. Its first run used only stars lim-4 < m < lim and an affine fit for any number of stars; on i21576 and i21780
  only 2 stars were found, so the 6-parameter fit was underdetermined (O-C 34" and 99"). The final version uses
  lim-6 < m < lim+0.3 and a shift on the DASCH grid when fewer than 6 stars are found.
- `PRECOVERY_DATA` lets every script read and write a separate data directory, for `checks/rerun.py`. No logic changed.

## Addendum 4 (2026-11-27, solve round 2, after the verifier's report `VERIFY.md`; no pre-registered rule changed)
What the verifier saw first: `src/predict.py` dropped every Horizons row with a rise/transit/set mark. For i21780 the
dropped row was the midpoint row (02:12 UT), so the committed `data/predictions.json` gave the 02:17 UT position
(5.5" away), and the round-1 search window for i21780 was 01:17-03:17 UT instead of 01:12-03:12 UT.
Cause: such a row has one CSV field less ("tm" fills both flag columns). The pre-registered code removed it as a
"row that does not parse sanely".
Changes:
- `src/hz.py` parses these rows (one field inserted); a row with a wrong field count now stops the run.
  `src/predict.py` keeps all rows and stops if no row is at the DASCH midpoint.
- The pre-registered files are kept unchanged in `data/prereg/` (`predictions.json`, `predictions2.json`,
  `results.json`, `results2.json`, the i21780 cutout of round 1). The round-1 decision of record is the one in
  `data/prereg/results.json` (Addendum 1).
- With the corrected predictions, all 19 tracks gain the formerly dropped row; only the i21780 midpoint moves.
  `src/fetch.py` centres each cutout on the midpoint position, so i21780 has a new cutout (5.5" shift of the grid).
  Corrected round 1 (`data/results.json`): i21780 S = 16.0, p0 = 0.030, pass; Ganymed 3 of 6, P = 5.07e-4,
  "detected"; Hektor unchanged (2 of 5, P = 0.029). Round 2 (`data/results2.json`): identical to the pre-registered
  run. No decision changed.
- `src/astrometry.py` (a measurement, not a test) now gives two centroid methods: "region" (the whole region above
  half maximum, so a trail is measured as a whole; reference stars brighter than lim - 1) and "box" (the earlier
  method). I chose "region" as the main method after I saw that on i21050 the region centroid of bright stars is
  offset by about 13" from the faint ones (asymmetric images), and that the result on i21050 depends on the method.
  The region method has two free choices. `data/astrometry_variants.json` gives the O-C for all 6 combinations
  (star match tolerance 4, 8 or 12 px; reference stars to lim + 0.3 or to lim - 1). Both kept methods are reported.
- `src/shapes.py` measures the region shapes of the source, of the predicted trail and of stars (`data/shapes.json`).

## Round 3 (2026-11-27, pre-registered before any round-3 image was downloaded or seen)
Question: is (624) Hektor on Heidelberg (HDAP) plates of 1895-1907? Set A (plates before 1904-09-13) tests the
Trojan record; G2281-G2283 (1901-08-23 evening) are on the same date as the Harvard round-1 candidate b28276.
Plates: `data/hdap/hektor_cover.csv` (`src/hdap_cover.py`: all 3857 HDAP plates of 1895-1907 with a coverage polygon;
18 contain Hektor), minus the plates with Hektor < 0.1 deg from the plate edge (G965, G962, G2720): 15 plates.
Predictions: `data/hdap/predictions.json` (`src/hdap.py predict`; Horizons, site 024).
Measurement and decision: `src/hdap.py measure` as committed here (docstring). Trail-matched statistic with a
time-shift search of +-60 min, because the HDAP times are uncertain: on plate G2392 the header UT gives a local
sidereal time 45 min later than the header ST, and the header ST agrees with the header hour angle.
Decision for each set: "detected" if the Fisher p_comb < 0.001 and at least 2 plates have p < 0.01.
Code test before this commit: plate G2392 (a Pluto-field plate, already seen, no Hektor) with a synthetic 53" trail:
no injection p = 0.10; injected peak 0.25 x pixel noise p = 0.0005.

## Addendum 5 (2026-11-27, round 3, before any round-3 measurement result was seen)
The first `hdap.py measure` run stopped with a NaN error before it printed any result. Cause: `hdap.py predict` kept
the Horizons meridian-transit row (shifted CSV fields; for example RA 19.0004, V 8.243 on G963), which projects to NaN.
Fix: drop rows more than 1 mag from the median V, as `predict.py` already does. The fix removed exactly one row from 12
of the 15 tracks; no midpoint position changed. B262a: the SODA service returned HTTP 204 (no data), so it has no cutout.

## Addendum 6 (2026-11-27, round-3 result)
`data/hdap/results.json`: set A (before 1904-09-13): 5 measurable plates, p_comb = 1.5e-5, 3 plates with p < 0.01
(G2281 0.0015, G2282 0.0050, G2283 0.0065; all 1901-08-23 evening) -> "detected". Set B (all 14 measurable):
p_comb = 3.2e-6 -> "detected". The 1904 plates (after the record date) give no plate with p < 0.01.
Not measurable or no data: B262a (no cutout). G963 and G1139 had fewer than 3 matched stars (plate WCS used).
Across the three Hektor rounds, round 3 is the only one that passes; with a factor 3 for the three rounds, 4.5e-5.
Post hoc (`src/motion_check.py`, `src/stamps_1901.py`, `data/hektor_1901-08-23.png`): on b28276 and on G2281-G2283,
the signal is at each plate's own-epoch position and absent at the other observatory's epoch position (326" away).
The three Heidelberg plates are from one night (two simultaneous exposures with the two lenses of the double
astrograph, and one later exposure). Each Heidelberg signal is weak (trail-mean z 1.4-3.0).

Note on numbering: round 3 was done in a separate copy of this repository at the same time as the solve round 2
of the Ganymed claim. Its addenda were numbered 4 and 5 there; here they are 5 and 6, after the solver's Addendum 4.

## Addendum 7 (2026-11-27, round 3 merged into this repository, after the round-3 result)
Addendum 5 dropped Horizons rows more than 1 mag from the median V in `src/hdap.py predict`. These were the rows with a
rise/transit/set mark, the same defect as in Addendum 4. With the `src/hz.py` fix of Addendum 4 the filter is
removed: `src/hdap.py` keeps all rows and stops if a row has no V. Effect: 11 of the 15 tracks gain one row (2-min
steps throughout; `checks/rerun.py` checks the largest step). No midpoint changed. All 15 p values are identical;
the S values change by less than 3e-4. Set A p_comb = 1.49e-5 and set B p_comb = 3.23e-6, as before.
`src/motion_check.py` now also writes `data/hdap/motion_check.json`. No decision changed.
