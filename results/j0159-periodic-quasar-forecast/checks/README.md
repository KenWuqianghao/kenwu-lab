# Reproducing the forward test

Run all commands from the result folder. `checks/ci.sh` is the full check. It installs the pinned packages of `checks/requirements.txt` into the active Python 3.13, runs `checks/rerun.py`, and redraws the figure.

## Steps of `checks/rerun.py`

1. Download the ZTF light curve of the quasar from IRSA (`nph_light_curves`, 2.2-arcsec circle around RA 29.791908, Dec +1.087369, all filters). The file goes to `work/ztf_raw.csv`. Keep the zg and zr points with `catflags` = 0.
2. Run the pre-registered test of `PROTOCOL.md`: the statistic T, 5000 null and 5000 signal mocks for tau = 210 d and 500 d, the phase scan, the free-phase fit at 741 d, the per-band T, and the period scan from 300 to 1500 d. Then the post hoc free-phase null test of the sprint stage.
3. Download the arXiv source of Zheng et al. 2016 (`https://arxiv.org/src/1512.08730`, to `work/src/src.tgz`). Read the 252 CRTS points and the green fit curve of Fig. 1a from `lc.eps`.
4. Run Addendum 1 of `PROTOCOL.md`: the CRTS control (A1), the refit forward test in 8 worlds plus a null world (A2), the period scan with a CRTS refit (A3), the power at the CRTS amplitude (A4), and the free-phase amplitude against random-phase signals (A5). Store the SHA-256 of both downloads (A6).
5. Compare every value with `data/expected.json` (relative tolerance 1e-6). Print `OK` and exit 0 if all agree. Print `MISMATCH <key>` and `FAIL` and exit 1 if not. If the SHA-256 of the IRSA file differs from the stored value, print a `NOTE` line first: the ZTF release changed.

`python3 -I checks/rerun.py --write` writes `data/expected.json` instead of comparing. `--cache` reuses the files in `work/`.

The analysis uses the epochs up to MJD 60970 (`MJD_END` in `rerun.py`). The last ZTF epoch in the data that we used is MJD 60969.34 (2025-10-21). So new epochs in a later ZTF release do not change the result; the checksum `NOTE` then appears, but the comparison passes. A reprocessing of old ZTF photometry by IRSA would change the input data and make the comparison fail. The write stage added `MJD_END`; it removes no point from the data of 2026-11-28. The data were downloaded on 2026-11-28.

The mocks use fixed seeds (numpy `default_rng`, seeds 20261128 to 20261130). The values were produced on Linux x86_64 with numpy 2.5.5.

## Files

| File | Content |
|---|---|
| `rerun.py` | downloads, pre-registered test, Addendum 1, comparison with `data/expected.json` |
| `plot.py` | `data/fig_forecast.png` (CRTS points with both curves; ZTF 30-day medians with both curves continued). Descriptive; no number comes from it. |
| `ci.sh`, `requirements.txt` | CI entry point and pinned packages |

## Independent checks

The verification stage of the pipeline wrote its own code for the CRTS extraction, the registered statistic and the refit worlds. Its results are quoted in the paper (Sections 4, 5.2 and 6): CRTS points equal to ours to 0.0005 d and 0.00005 mag; Gaussian p_sig = 2.2e-7; refit-world fractions 0.0153, 0.0077, 0.080 and 0.057 for the 0.1 mag worlds (seed 4242, 3000 mocks). That code is not part of this folder.
