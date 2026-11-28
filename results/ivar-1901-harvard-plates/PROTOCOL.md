# Protocol: (1627) Ivar on Harvard plates before its first observation (1929-09-25)

Pre-registered 2026-11-28 before any plate image (cutout) was downloaded or seen. The commit time is the evidence.
Only plate metadata (DASCH `/queryexps`) and JPL Horizons ephemerides were used before this commit.

## Claim under test
JPL SBDB `first_obs` of (1627) Ivar is 1929-09-25 (discovery by E. Hertzsprung, Johannesburg). The MPC observation
file has no earlier line. Question: is a source at the JPL Horizons position of Ivar on DASCH DR7 plates taken
before 1929-09-25?

## Data
DASCH DR7 (Harvard College Observatory plate scans), public API `https://api.starglass.cfa.harvard.edu/public/dasch/dr7`
(`/queryexps`, `/cutout`, `/querycat` with the ATLAS-REFCAT2 reference catalogue). JPL Horizons, orbit solution
current on 2026-11-28 (the Horizons header is kept in `data/hz_cache`).

## Plates (fixed by rule)
`src/coverage.py` (rule in its docstring): bright apparitions 1901 May-Oct, 1906 Aug, 1929 May-Sep; series a, b
(Arequipa, MPC 800), i, ac, me (Cambridge, MPC 802); solution 0; limMagAtlas present; Sun altitude < -12 deg; object
altitude > 15 deg; lim - (V + 0.8 + 2.5 log10(max(1, trail/30"))) >= 0.3. If more than 30 plates pass, the 30 with
the largest margin are used (`src/predict.py`). The list is `data/coverage.json` and `data/predictions.json`.

## Predictions (fixed)
`src/predict.py`: Horizons astrometric RA/Dec of 1627, topocentric for the series site, every 5 min from the DASCH
midpoint -2 h to +2 h. The series-to-site map is an assumption (as in the Ganymed paper).

## Measurement (fixed)
`src/measure.py`, copied from the factory paper `ganymed-1898-harvard-plates` (method by that paper), with BUFFER 15"
and THRESH 10 for Ivar. Statistic S = max of the noise-normalised z image within 15" of the predicted track,
midpoint +-1 h, catalogued ATLAS stars masked. Placebo: the same region at 300 random offsets of 90"-420" on the
same cutout gives the per-plate null pass rate p0.
A plate whose cutout request returns 422 ("does not overlap") is "not covered" and is not counted.

## Decision (fixed)
- Ivar is "detected" if at least 2 plates pass (S >= 10) and the Poisson-binomial probability of at least that many
  passes under the per-plate p0 is below 0.001. Otherwise "not detected".
- The same rule is applied to two sets: set E = plates of 1901 and 1906 (the record claim: an image 23 or more
  years before discovery) and set A = all plates. Set E is the primary claim. A detection only in set A from 1929
  plates is a partial result (same apparition).
- Detected: the earliest passing plate is a candidate earliest image; it needs expert examination of the plate.
- Not detected: report S and p0; no claim. A null result is a valid result.

## Positive control
The same pipeline detected Ganymed on 1898 i and ac plates (`ganymed-1898-harvard-plates`, P = 5.1e-4). No new
injection test is pre-registered here, for time reasons.

Any change after the data are seen goes into a dated addendum that says what was seen first.

## Addendum 1 (2026-11-28 01:13 CET, after the pre-registered run; no rule changed)
Result of record (`data/results.json`, `data/decision.json`): b27808 "not covered" (cutout 422). Set E: 4 of 4
plates pass (b27907 S=28.6, b28342 S=31.9, b28520 S=62.7, b28598 S=42.8); P_null = 1.2e-6 -> "detected". Earliest
passing plate: b27907, 1901-07-18 09:46 UT. Set A adds ac27730 (1929-09-12), which fails (S=4.3; the astrometric
refit found no star, fit "none"). Peak distances from the predicted midpoint position: 58.6" (b27907, on the
146" predicted trail, -0.42 h), 4.0", 2.5", 0.5".
Note added with Addendum 1: commit 7c3db31 (01:04:21, before any image) made `src/measure.py` skip a plate with no
cutout, which implements the "not covered" rule above. After the run, `src/*.py` gained an optional
`PRECOVERY_DATA` directory for `checks/rerun.py`; no logic changed.
