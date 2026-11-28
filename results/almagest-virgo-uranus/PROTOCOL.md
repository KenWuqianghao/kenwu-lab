# PROTOCOL: is Almagest Virgo 17 (Baily 513) Uranus seen by Hipparchus?

Committed 2026-11-28, before any distance, percentile or match was computed.

## Claim under test
K. P. Hertzog, "Ancient Uranus?", QJRAS 29 (1988) 277-279, proposes that the 17th star
of Virgo in Ptolemy's catalogue (Baily/Peters-Knobel no. 513; Toomer: longitude Virgo 27 1/4,
latitude +0 1/6, magnitude 6) is Uranus, observed by Hipparchus near 25 March -127.
N. M. Swerdlow, "A curiosity: Did Ptolemy see Uranus?" (2020, doi:10.5281/zenodo.3975731),
p. 144 n. 4, says the question is not decided: "any decision rests upon first determining
whether the coordinates of this star were adapted from Hipparchus. I do not know how to do this."

This test does not decide the Hipparchan origin. It tests the identification by position:
does Uranus fit the entry better than any real naked-eye star, when both are judged against
the error distribution of the catalogue itself?

## What I saw before this commit
- Swerdlow's numbers: Uranus at -127 Mar 25 at 175;12, +0;45; entry 177;15, +0;10;
  76 Vir at 179;21, -0;18.
- The Verbunt & van Gent table rows for Virgo, including their identification of entry 513
  with HIP 66098 (76 Vir, V = 5.2) at their distance 71.2 arcmin.
- The first two rows of the Horizons file (dates -148), no positions near the entry.

## Data (accessed 2026-11-28)
1. Ptolemy catalogue with identifications: Verbunt & van Gent 2012, A&A 544, A31, VizieR
   table J/A+A/544/A31/ptolema (1028 entries, Toomer values).
2. Hipparcos main catalogue, VizieR I/239/hip_main, all stars with Vmag < 6.6.
3. Uranus: JPL Horizons API, target 7 (Uranus barycenter, DE441), geocentric, daily at
   0h TT, quantities 23 (S-O-T elongation) and 31 (ecliptic of date, IAU76/80).
   Hipparchus window file: JD 1667365.5 to 1675400.5.

## Method
- Epoch t0 = Hipparchus catalogue epoch, JD 1674487.5 (approx. -127 Jan 1 TT).
- Star positions: propagate each Hipparcos star from J1991.25 with its proper motion
  (astropy `apply_space_motion`; parallax <= 0 replaced by 0.1 mas) to t0, then transform to
  `GeocentricMeanEcliptic(equinox=t0)`.
- Calibration set C: entries with I = 1, a HIP number, |beta_P| <= 10 deg, entry 513 excluded.
- Frame offset: dL = median(lambda_P - lambda_star), dB = median(beta_P - beta_star) over C.
  Hipparchus-frame position of an entry: (lambda_P - dL, beta_P - dB).
- Reference residual distribution R: angular distance between the Hipparchus-frame entry and
  its identified star, for entries in C with Ptolemy magnitude VP >= 5.
- For entry 513:
  - r_star = distance to the nearest Hipparcos star with V <= 6.0 (any star, not only 76 Vir).
  - d_U = minimum distance to Uranus over the window days with S-O-T >= 120 deg.
  - Q_S, Q_U = percentiles (fraction of R that is <= the value, times 100).

## Decision rule (fixed now)
- SUPPORT for Hertzog: Q_S > 95 and Q_U <= 50.
- REFUTE (Uranus not favoured): Q_S <= Q_U (a real V <= 6.0 star fits as well as or better
  than Uranus), or Q_U > 95.
- Otherwise INCONCLUSIVE.

## Controls
- Placebo (specificity of a Uranus match): compute d_U for every entry of C with
  |beta_P| <= 3 deg. F = fraction with d_U <= d_U(513). If F > 0.2, the Uranus match alone is
  weak evidence, and the report must say so.
- Known-answer check: 200 fake entries built from the Uranus position on random window days
  with S-O-T >= 120, plus (dL, dB). The pipeline must give d_U < 1 arcmin for all.
- Consistency check: my residuals for C must correlate with the Verbunt & van Gent `dist`
  column (Spearman rho > 0.8), else the frame transform is wrong and I must stop.
- Secondary, descriptive only: the same d_U for a Ptolemy window AD 120-145 (equinox AD 137).

## Addendum, 2026-11-28 (after the pre-registered run)
- Seen before this addendum: the full pre-registered output (`data/expected.json`, key
  `analysis`), verdict INCONCLUSIVE.
- Deviation in a comment only: JD 1674487.5 is -128 Jul 1 (Julian), not "approx. -127 Jan 1".
  The code used JD 1674487.5 as written. The frame offset is fitted at the same epoch, so a
  shift of a few months moves no star by more than about 0.3 arcmin relative to the fit.
- New, exploratory, not part of the decision: `checks/exploratory.py` computes a density
  ratio for the two distances, the result for the textual variant "south 0;10" that Swerdlow
  names, and the Uranus latitude range near the entry. No pre-registered rule was changed.
