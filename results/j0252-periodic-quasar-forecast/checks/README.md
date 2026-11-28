# Reproducing the forward test

Run all commands from the result folder. `checks/ci.sh` is the full check. It installs the pinned packages of `checks/requirements.txt` into the active Python 3.13, runs `checks/rerun.py`, and redraws both figures.

## Steps of `checks/rerun.py`

1. Download the ZTF light curve of the quasar from IRSA (`nph_light_curves`, 2.2-arcsec circle around RA 43.061125, Dec -0.470472, all filters). The file goes to `work/ztf_raw.csv`.
2. Run the pre-registered test of `PROTOCOL.md` on zr and zg: the statistic T, 5000 null and 5000 signal mocks, the phase scan.
3. Run the post hoc robustness checks of the sprint stage: the positive control on pre-cutoff ZTF data, other periods, the last-cycle template, other DRW time scales, a period scan from 1400 to 1700 d.
4. Download a 0.08-degree zr cone around the quasar (about 10 MB, `work/placebo/cone.csv`) and run Addendum 1 (`checks/censored.py`): the exposure list, the censored forward model, the DRW grid and the published-posterior scan, the placebo calibration, the depth checks and the other periods.
5. Compare every value with `data/expected.json` (relative tolerance 1e-6). Print `OK` and exit 0 if all agree. Print `MISMATCH <key>` and exit 1 if not.

`python3 -I checks/rerun.py --write` writes `data/expected.json` instead of comparing.

The analysis window is MJD 58927 < t <= 60970. The last ZTF epoch in the data that we used is MJD 60968.34 (2025-10-20). So a later ZTF release does not change the result. A reprocessing of old ZTF photometry by IRSA would change the input data. The data were downloaded on 2026-11-28.

The mocks use fixed seeds (numpy `default_rng`, seed 20261128 and offsets). On one platform every number is exact. The values were produced on Linux x86_64 with numpy 2.5.5.

## Files

| File | Content |
|---|---|
| `rerun.py` | download, pre-registered test, robustness checks, comparison with `data/expected.json` |
| `censored.py` | Addendum 1: censored forward model, DRW scan, placebo calibration, depth checks, other periods |
| `fig_addendum.py` | `data/fig_addendum.png` (p_sig across the published DRW posterior) |
| `plot_forecast.py` | `data/fig_forecast.png` (model, continuation and binned ZTF data); descriptive, no number comes from it |
| `digitize_model.py` | digitization of the r-band model curve of Liao et al. Fig. 1 into `data/model_r_digitized.json` |
| `digitize_drw.py` | digitization of the r-band DRW posterior contours into `data/drw_posterior_r.json` |
| `verify/v4_censored_independent.py` | independent censored model, written by the verification stage from the text of Addendum 1 |
| `ci.sh`, `requirements.txt` | CI entry point and pinned packages |

## Independent implementation

`verify/v4_censored_independent.py` does not import the other scripts. It reads the cone file of step 4:

```sh
python3 -I checks/verify/v4_censored_independent.py work/placebo/cone.csv data/model_r_digitized.json
```

It runs in about 25 s. Its output in the write stage (2026-11-28), with the original verification seeds:

```
exposures 345 by group [312  33] listed 97 k 1.416 T_obs -0.6636
deep exposures (limitmag > 21.6): 23 listed 15
paper best fit  m0(a=1) 21.096 | median T 0.612 sd 0.366 | p_sig 0.0005 | p_null 0.962 | power 0.345 | p_sig x1.67 0.0175 | x2.07 0.0428
placebo objects 51 z median -0.036 sd 2.083 robust sd 1.748
white-only T sd 0.173, DRW part 0.322, placebo-based total sd 0.553, z -2.31, Gaussian p_sig 0.0105
```

The paper's calibration range of p_sig (0.0105 to 0.043) uses these lines. The write stage added only the upper end of the analysis window (`END`) to this script.

## Redo the digitizations (optional)

Both inputs come from the arXiv source of arXiv:2008.12317v3 (`https://arxiv.org/e-print/2008.12317v3`, a tar file). They need Pillow and PyMuPDF (`pip install pillow==13.0.0 pymupdf==2.2`) and Poppler's `pdfimages`.

```sh
mkdir -p work/src && curl -L -o work/src.tar https://arxiv.org/e-print/2008.12317v3 && tar -xf work/src.tar -C work/src
pdfimages -png work/src/burst_fit_J0252_rednoise_new-eps-converted-to.pdf work/fig
python3 -I checks/digitize_model.py work/fig-000.png work/model_r_digitized.json
python3 -I checks/digitize_drw.py work/src/chain_4band.pdf work/drw_posterior_r.json
cmp work/drw_posterior_r.json data/drw_posterior_r.json
```

The verification stage got identical output for both files from a new download of the source. The pixel coordinates of the axis ticks are fixed in the scripts.
