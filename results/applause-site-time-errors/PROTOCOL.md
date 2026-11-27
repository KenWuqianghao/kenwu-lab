# PROTOCOL (pre-registered 2026-11-27 ~09:25 CET, before any Sun altitude or time statistic was computed)

## Claim under test
APPLAUSE DR4 (Archives of Photographic PLates for Astronomical USE, https://www.plate-archive.org,
DOI 10.17876/plate/dr.4) documents, in its TAP schema (`tap_schema.columns`, read 2026-11-27):
- `applause_dr4.plate.site_longitude`: "East longitude of the observing site, in decimal degrees"
- `applause_dr4.plate.site_latitude`: "Latitude of the observing site, in decimal degrees"
- `applause_dr4.exposure.ut_mid`: "UT date and time at the mid-point of sub-exposure"

## What I saw before this protocol (metadata only)
A group-by query on `plate` (archive_id, site_name, site_longitude, site_latitude) shows:
- archive 208, "Dr. Remeis-Observatory, Bamberg, Germany": longitude 49.8845, latitude 10.8881 (18,681 plates).
  Bamberg is at about 49.88 N, 10.89 E. The two values are swapped.
- archive 208, Davos / Muottas Muragl sites: longitude 46.5217 / 46.8014, latitude 9.9025 / 9.8147. Swapped.
- archive 205, "Observatorio de Fisica Cosmica, San Miguel, Argentina": longitude -34.5567, latitude -58.7317
  (870 plates). San Miguel is at about 34.56 S, 58.73 W. Swapped.
No Sun position, solar time or daylight statistic was computed before this commit.

## Question
Q1 (descriptive, settled by geography): which DR4 site records have longitude and latitude swapped?
Q2 (pre-registered test): did the swapped longitude enter the computation of `ut_mid`?
If APPLAUSE derived UT from logged local mean time with the wrong longitude, then
true UT = ut_mid + (lon_recorded - lon_true)/15 h. For Bamberg: +2.5998 h. For San Miguel: +1.6117 h.
If the logs were in zone time or UT, the swap has no effect on `ut_mid`.

## Data
`checks/fetch.sh` downloads `plate` (plate_id, archive_id, site_name, site_longitude, site_latitude) and
`exposure` (exposure_id, plate_id, archive_id, jd_mid, ut_mid, exptime, time_orig_start, time_orig_end, flag_time),
all rows, anonymous TAP sync, access date 2026-11-27.

## Sample
Timed exposure: `jd_mid` not null, `time_orig_start` not null and not empty, `exptime` > 0 or null allowed? -> required > 0.
Unit of test ("block"): one archive_id at one site, with at least 50 timed exposures.
Site coordinates used for the Sun: the recorded values, except for the swapped records of Q1, where the two values
are exchanged ("true site").

## Quantities (Sun from a Meeus low-precision solar ephemeris, error < 0.02 deg; no refraction)
- h: Sun altitude at jd_mid at the true site.
- D6: fraction of timed exposures with h > -6 deg (Sun above civil twilight limit). Primary.
- D0: fraction with h > 0 deg. Reported.
- M: circular mean of local apparent solar time at jd_mid, minus 24:00 (hours, in (-12, 12]). Night programmes give M near 0.
- Shifted versions D6', M' at jd_mid + Delta/24, with Delta from Q2 (Bamberg 2.5998 h, San Miguel 1.6117 h, Davos sites
  (lon_rec - lat_rec)/15 h each).

## Controls
- Negative controls: every other block (Hamburg, Potsdam, Bonn, Tartu, Tautenburg, Vatican, Boyden, Mt John, ESO, Calar Alto)
  with recorded coordinates. Expectation: D6 < 3 % and |M| < 1 h.
- Placebo: D6 at jd_mid + U(-12 h, 12 h), 200 draws, seed 20261127, for each block (the value of D6 for times with no
  relation to the night).
- Known-answer injection: add +2.5998 h to the times of the Hamburg archive 101 block. The test must flag it
  (D6 rises to >= 5 % and M moves by more than 1.5 h). If not, the test is invalid ("failed").

## Decision rules (for each swapped block with >= 50 timed exposures)
- "Swap entered UT" (supported) if: D6 >= 5 %, D6' <= D6/3, exact one-sided sign test on discordant exposures
  (b = h>-6 at raw and h<=-6 at shifted; c = the reverse) P(Bin(b+c,1/2) >= b) < 0.01, and |M + Delta| < 1 h
  (i.e. the raw night is centred about Delta hours early).
- "Swap did not enter UT" (refuted) if: D6 < 3 % and |M| < 1 h at the true site.
- Otherwise: "inconclusive", report the numbers.
The Q1 list itself is the main descriptive finding and does not depend on Q2.

## Addendum 1 (2026-11-27, after the pre-registered run)
What I saw: the pre-registered run (`data/results.json`) gave "refuted" for Q2 at Bamberg and San Miguel and
"inconclusive" at Muottas Muragl (n = 93). The known-answer injection was detected. The negative-control expectation
|M| < 1 h failed in 11 of 21 control blocks (M from -1.7 h to -0.98 h): night programmes are centred before
local midnight, so the M criterion is too strict. D6 was > 3 % in control blocks 1 (Potsdam), 4, 5, 102, 110 and 501
(Vatican, D6 = 40.8 %). The targets of the daylight exposures in 4, 5 and 501 are stars and star fields.
Then, post hoc, I tested two fixed rules (`checks/explore_rules.py`, `data/explore_rules.txt`). For archive 501, rule
H_B ("logged local sidereal time was read as clock time") moves 222 daylight exposures to night and 1 night exposure
to day (D6 40.8 % -> 0.2 %). This test is exploratory, because I chose it after I saw the data.

## Addendum 2 (2026-11-27, pre-registered before the computation below)
Confirmatory test of H_B for archive 501 with a statistic that I have not computed: the hour angle
HA = wrap(o - RA) of the plate centre, with o the logged midpoint value (time_orig_start + exptime/2) and RA = `ra_orig`
of the exposure (fall back to `ra_icrs`), in hours, wrapped to (-12, 12].
- If the logged value is local sidereal time (H_B), plates are taken near the meridian and |HA| is small.
- If the logged value is clock time, HA is spread over the day.
Decision: H_B confirmed if at least 70 % of the 501 exposures with an RA have |HA| < 3 h and the median |HA| < 2 h.
H_B rejected if fewer than 40 % have |HA| < 3 h. Control: the same statistic for Hamburg archive 101, where APPLAUSE
already treats the logged value as sidereal time (H_B changes 0 night exposures to day there), must give >= 70 %.
Placebo: the same statistic with o replaced by the clock time of `ut_mid` in hours (UT + lon/15) must give < 40 % for 501 under H_B.

## Addendum 3 (2026-11-27, pre-registered before the computation below)
What I saw in Addendum 2 (`data/hourangle.json`): archive 501 gives 70.2 % with |o - RA| < 3 h (median 1.98 h), which meets
the Addendum 2 thresholds, but its placebo also gave 72.2 %. That placebo was mis-specified: for archive 501, `ut_mid` is
computed from o itself, so its clock time is o plus a constant and is not independent of o. By the Addendum 2 rules the
test is therefore not valid. I replace the placebo with the correct comparison:
- HA_APP = wrap(LST(ut_mid, site) - RA): the hour angle of the plate centre if the APPLAUSE midpoint is correct.
- HA_HB = wrap(o - RA): the hour angle if o is local sidereal time (H_B).
Decision for archive 501: H_B confirmed if frac(|HA_HB| < 3 h) - frac(|HA_APP| < 3 h) >= 0.25 and an exact two-sided
sign test on exposures where exactly one of the two is < 3 h gives p < 0.001. APPLAUSE time confirmed if the difference is
<= -0.25 with the same p. Otherwise inconclusive.
Control: Hamburg archive 101 (APPLAUSE already treats o as sidereal): the difference must be within +-0.05.
