# Reproducing the results

Run all commands from the result folder. `bash checks/ci.sh` is the full check. It needs Python 3.13, `curl`, and network access to `vizier.cfa.harvard.edu` and `ssd.jpl.nasa.gov`. It installs `checks/requirements.txt` (numpy, scipy, astropy and its dependencies; pinned versions).

## Steps of `checks/rerun.py`

1. `checks/fetch.sh DIR` downloads the raw data into a new temporary directory:
   - `ptolemy.tsv`: VizieR J/A+A/544/A31/ptolema (1028 entries; Toomer values, Hipparcos identifications and flags of Verbunt and van Gent 2012).
   - `hip_v65.tsv`: VizieR I/239/hip_main, all stars with V < 6.6.
   - `uranus_hipparchus.txt`, `uranus_ptolemy.txt`: JPL Horizons, target 7 (Uranus barycentre), geocentric, daily at 0 h TT, quantities 9, 23 and 31 (magnitude, Sun-observer-target elongation, ecliptic longitude and latitude of date). Windows JD 1667365.5-1675400.5 (149 BC Dec 31 to 127 BC Dec 31) and JD 1764887.5-1774384.5 (AD 120 Jan 1 to AD 146 Jan 1).
2. `checks/analysis.py DIR OUT`: the registered test of `PROTOCOL.md` for the Hipparchus window and, as a secondary result, for the Ptolemy window. Key `analysis` of `data/expected.json`.
3. `checks/exploratory.py DIR OUT`: exploratory numbers named in the protocol addendum (density ratio, latitude variant "south 0;10", Uranus latitude near the entry, count of larger reference errors). Key `exploratory`.
4. `checks/posthoc.py DIR OUT`: post hoc limits added at the write stage in reply to the verification round: the placebo inside the longitude range of the Uranus track, the magnitude codes of the reference set, the longitude variant 177;00, a bootstrap of the percentiles, other elongation cuts, and the calendar dates of the key Julian dates. Key `posthoc`.
5. The script compares every value of `data/expected.json` with the new value (relative tolerance 1e-6; strings and integers exactly), prints `N/N values match`, and exits 1 on any difference.

The registered numbers (key `analysis`) and the exploratory numbers are the 63 values that the solve stage registered and reproduced. The post hoc numbers are not part of the decision.

## Other files

| File | Content |
|---|---|
| `checks/figure.py` | Figure 1 of the paper (needs matplotlib; not run by `ci.sh`): `python -I checks/figure.py DIR paper/fig_virgo17.png`, with `DIR` from `checks/fetch.sh DIR` |
| `checks/verify/indep.py` | independent recomputation of the verification stage: other precession model (ERFA `ltecm`), Horizons vectors (not run by `ci.sh`) |
| `checks/verify/fetch_vectors.sh` | downloads the Horizons geocentric ICRF vectors of Uranus and the Sun for `indep.py` |
| `checks/verify/sens.py` | sensitivity checks of the verification stage in its own frame (not run by `ci.sh`) |
| `PROTOCOL.md` | the pre-registered protocol with its dated addendum |
| `data/GIT_LOG.txt` | commit list of the working repository with times (registration evidence) |

To run the independent check: `bash checks/verify/fetch_vectors.sh VEC`, `bash checks/fetch.sh RAW`, then `python -I checks/verify/indep.py RAW VEC` (needs numpy and pyerfa).

## Known sensitivities

- VizieR and JPL Horizons can change their data. Horizons serves DE441 for Uranus; a new planetary ephemeris would change the Uranus positions by a negligible amount, but enough to fail the 1e-6 tolerance.
- The bootstrap uses `numpy.random.default_rng(1)` and the injection uses `default_rng(20261128)`. The values were checked with the pinned numpy version.
