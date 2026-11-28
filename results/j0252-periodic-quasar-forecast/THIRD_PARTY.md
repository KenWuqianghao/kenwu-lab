# Third-party data

All sources are public and need no account. Access date: 2026-11-28.

| Source | What we use | Access | Licence or terms |
|---|---|---|---|
| Zwicky Transient Facility (ZTF) public light curves, NASA/IPAC Infrared Science Archive (IRSA) | zr and zg points of the quasar (2.2-arcsec circle) and a 0.08-degree zr cone around it, epochs to MJD 60968.34. Downloaded by `checks/rerun.py`; not redistributed here. | `https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves` | ZTF public data. Users must acknowledge ZTF and IRSA and cite Bellm et al. 2019 (PASP 131, 018002) and Masci et al. 2019 (PASP 131, 018003). |
| arXiv source of Liao et al. 2021 (MNRAS 500, 4025), arXiv:2008.12317v3: files `burst_fit_J0252_rednoise_new-eps-converted-to.pdf` (Fig. 1) and `chain_4band.pdf` (DRW-parameter figure) | `data/model_r_digitized.json` (digitized r-band model curve) and `data/drw_posterior_r.json` (digitized r-band DRW contours). These are measurements from the figures; the figures are not redistributed. | `https://arxiv.org/e-print/2008.12317v3` | arXiv non-exclusive distribution licence. We use measured values and short quotes, with citation. |
| OpenAlex API | citation lists for the prior-art search | `https://api.openalex.org` | CC0 |
| Crossref API | bibliographic data of the references | `https://api.crossref.org` | Metadata openly available |

Software (pinned in `checks/requirements.txt`): numpy 2.5.5, matplotlib 3.11.2. Optional for the digitizations: Pillow 13.0.0, PyMuPDF 2.2, Poppler `pdfimages`. `checks/verify/` holds code written by the verification stage of the same pipeline.
