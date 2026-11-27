# Reproducing the results

Run all commands from the result folder. `checks/ci.sh` is the full check. It needs Python 3.13, `curl` and network access to `https://www.plate-archive.org`. The analysis uses only the Python standard library.

## Steps of `checks/rerun.py`

1. `fetch.sh`, `fetch_ra.sh` and `fetch_501.sh` download the DR4 metadata through the anonymous TAP service into a new temporary folder (about 90 MB):
   - `plate.xml`: `plate_id, archive_id, site_name, site_longitude, site_latitude` of all plates;
   - `exposure.xml`: `exposure_id, plate_id, archive_id, jd_mid, ut_mid, exptime, time_orig_start, time_orig_end, flag_time` of all exposures;
   - `exposure_ra.xml`: the recorded pointing of archives 101 and 501;
   - `exposure501.xml`: all exposure columns of archive 501.
   The service returns VOTable files, although the query asks for CSV.
2. `analyze.py` runs the pre-registered site-swap test of `PROTOCOL.md`: the Sun altitude at each midpoint for each block, the shifted test for the swapped sites, the random-shift placebo (seed 20261127) and the known-answer injection.
3. `explore_rules.py` applies the two fixed time rules (Addendum 1) to archives 501, 208, 101, 4 and 5.
4. `hourangle2.py` runs the Addendum 3 hour-angle test for archives 501 and 101.
5. `vatican.py` computes the corrected midpoints of archive 501, the scope numbers and the post hoc permutation and target-altitude controls (seed 20261127). It writes the per-exposure table.
6. The script compares 70 values with `data/expected.json` and the new table with `data/vatican_corrected.csv`. It prints `71 of 71 checks match` and `ALL MATCH` when all agree, and exits 1 otherwise.

Options: `--cached` reuses `work/raw/` (no download); `--write` rewrites `data/expected.json` and `data/vatican_corrected.csv` (for the authors only).

## Files

| File | Content |
|---|---|
| `analyze.py` | VOTable reader, Sun altitude (low-precision Meeus formulae), site-swap test |
| `explore_rules.py` | rules H_A (local mean time read as sidereal time) and H_B (sidereal time read as clock time) |
| `hourangle_util.py`, `hourangle2.py` | hour angle of the plate centre, Addendum 3 test |
| `vatican.py` | corrected midpoints and post hoc controls for archive 501 |
| `plot.py` | `data/fig_vatican.png` and `paper/fig_vatican.pdf` (needs matplotlib; not run by CI) |
| `independent/` | independent code of the verification stage (astropy, numpy, scipy; not run by CI) |

The independent scripts read the downloaded files:

```sh
python3 -I checks/independent/swap.py work/raw
python3 -I checks/independent/vat.py work/raw/exposure501.xml
python3 -I checks/independent/vat2.py work/raw/exposure501.xml
```

## Known sensitivities

- DR4 is a fixed release, but the TAP service serves the live tables. If APPLAUSE corrects the metadata, the counts change and the check fails. The tables used for the paper were downloaded on 2026-11-27.
- The permutation controls use Python's `random` module with a fixed seed. Their values are exact on one Python version; Python keeps the `random.shuffle` sequence stable between versions, but this was checked only on Python 3.13 and 3.14.
- `vatican.py` dates the second rule (`ut_mid_sidereal_same_ut_date`) from `date_orig_start`. The verification stage used the UT date of `jd_mid` and got 225 day differences in place of 222.
