# Checks

Run `bash checks/ci.sh` from the result folder. It installs the pinned packages, downloads the raw data into a temporary folder, runs `checks/rerun.py`, and compares 647 numbers with `data/expected.json`. The temporary folder is deleted at the end.

To keep the downloads:

```sh
python3 -m pip install -r checks/requirements.txt
python3 -I checks/rerun.py --work /path/to/workdir            # download and compare
python3 -I checks/rerun.py --work /path/to/workdir --offline  # ComCat from data/, LOD files from the work folder
```

The work folder receives the downloads and `results.json` (all computed values).

## What `rerun.py` computes

| Part | Content |
|---|---|
| P1 | Baseline 1900–2017, NB fit, the 2018–2022 count, both p-values, the verdict, the 95% interval of the rate ratio. |
| P1 secondary | Poisson, M≥7.1, declustered (Gardner–Knopoff windows), baseline 1973–2017, window 2017–2021, level 17 per year, sliding 5-year sums, 2013–2017 against 2018–2022. |
| P1 controls | The rule on 114 historical windows; 10 000 simulated windows at 1.00, 1.25 and 1.30 times the baseline. |
| P2 | Held-out lag test 2018–2025: lag 5, lag 6, declustered, M≥7.1; exact permutation test. |
| P3 | In-sample lag curve 1900–2017 for lags 0–9, circular-shift and random-catalog nulls, max over lags, synthetic lag-5 catalog. |
| `write_additions` | Added at the write stage: P2 power and false-positive rate with the pre-registered 10 000 simulations, the P1 thresholds in N, p_refute for other forecast levels, the 1900–1972 rate, C02 annual LOD 2010–2025, and the P2 test with a mask from C04. These use their own random generator, so the other values equal the solve-stage run. |

The solve-stage code used 2000 simulations for the P2 power. Those values (0.172 and 0.028) are still computed and compared (`P2_power_x1.25`, `P2_false_positive_x1.00`). The paper reports the 10 000-simulation values. See Addendum 1 of `PROTOCOL.md`.

## Raw data

| File | Source |
|---|---|
| ComCat M≥7 1900–2025 | https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&eventtype=earthquake&minmagnitude=7&orderby=time-asc&starttime=1900-01-01T00:00:00&endtime=2026-01-01T00:00:00 |
| EOP C02 | https://hpiers.obspm.fr/eoppc/series/longterm/eopc02.1830-now |
| EOP 20 C04 | https://datacenter.iers.org/data/latestVersion/EOP_20_C04_one_file_1962-now.txt |

`data/comcat_m7_1900_2025.csv` is the snapshot of 2026-11-25 (id, time, latitude, longitude, depth, mag, magType; 1607 events). A new download that differs from it gives a `NOTE` line.

The figure is made by `python3 paper/figures/make_figure.py WORKDIR/results.json` (needs matplotlib 3.11.2).

Random seeds are fixed (20171022 for the solve-stage computations, 20261125 for the additions).
