# Checks

Run `bash checks/ci.sh` from the result folder. It installs the pinned packages, downloads the raw data into a temporary folder, runs the scripts below, and compares 252 numbers with `data/expected.json`. The temporary folder is deleted at the end.

To keep the downloads, run the comparison directly:

```sh
python3 -m pip install -r checks/requirements.txt
python3 -I checks/rerun.py /path/to/workdir
```

A second run with the same work folder uses the downloaded files and the cached arrays.

## Scripts

| Script | What it does | Output |
|---|---|---|
| `lunar.py` | Archive parser, lunar elongation from DE440s through Skyfield, the harmonic statistic, the station tests, the year-wise random rotation (YRR) null, and the injection of a known signal. | (library) |
| `run_all.py` | Pre-registered analyses: periods A (1895–2008) and B (2009–2026), YRR null, decision H1 and H2, placebo periods, the period scan, injections. | `results.json` |
| `exploratory.py` | Protocol addenda 1 and 2: the two `t` station tests, the binomial p-value, the pooled period 1895–2026. | `exploratory.json` |
| `timing.py` | Protocol addendum 3: the lunar phase at five times of day for each date, adjusted p-values. | `timing.json` |
| `rerun.py` | Downloads the raw data, prints SHA-256 values and the GHCN version, runs the three scripts, compares with `data/expected.json`. | exit 0 if all match |

The stored outputs of the original run are in `data/results.json`, `data/exploratory.json` and `data/timing.json`. `data/expected.json` holds the 252 compared values and the tolerance for each kind of value.

## Raw data

| File | Source |
|---|---|
| `ghcnd_hcn.tar.gz` | https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd_hcn.tar.gz |
| `ghcnd-stations.txt`, `ghcnd-version.txt` | https://www.ncei.noaa.gov/pub/data/ghcn/daily/ |
| `de440s.bsp` | https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp |

The numbers in the paper come from GHCN-Daily version 3.35-upd-2026111517 (`ghcnd_hcn.tar.gz` SHA-256 `b327e62d507b717198fd1735f6378dca6993a86e77d7a1bda3768589836a2151`). `de440s.bsp` has SHA-256 `c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2`. NCEI does not keep old versions at this URL. Version 3.35-upd-2026112318 (SHA-256 `2f94aed85c4fc0b9967c95cab87490c09d0e6fd00baa24147b70fd6640a81148`) changes 46 values, all inside the tolerances.

## Random seeds

YRR null and injections: seed 20261124. Exploratory station tests: 20261126. Pooled period: 20261127. Timing table: 20261125. Each null has 2000 replicates. Each injection level has 200 draws.

## Figure

`paper/figures/make_figure.py` draws Figure 1 from `data/results.json`. It needs matplotlib, which CI does not install.
