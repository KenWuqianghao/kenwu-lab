# Third-party data

All sources are public and need no account. Access dates: 2026-11-24 and 2026-11-25.

| Source | What we use | Access | Licence or terms |
|---|---|---|---|
| Zwicky Transient Facility (ZTF) public light curves, NASA/IPAC Infrared Science Archive (IRSA) | r-band epochs of 86 candidates and 344 placebo quasars, epochs to MJD 60969.55. Downloaded by `checks/fetch_data.py`; not redistributed here. | `https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves` | ZTF public data. Users must acknowledge ZTF and cite Bellm et al. 2019 (PASP 131, 018002) and Masci et al. 2019 (PASP 131, 018003). |
| ZTF DR11 release notes (IRSA, 2022-05-09) | DR11 epoch limits | `https://irsa.ipac.caltech.edu/data/ZTF/docs/releases/dr11/ztf_release_notes_dr11.pdf` | Public documentation. |
| SDSS DR14 quasar catalogue (DR14Q; Pâris et al. 2018, A&A 613, A51) | positions, redshifts and PSF r magnitudes in `data/candidates.csv` and `data/placebo.csv` | `https://data.sdss.org/sas/dr14/eboss/qso/DR14Q/DR14Q_v4_4.fits` | SDSS data are public. Cite SDSS and the catalogue paper. |
| 2dF QSO Redshift Survey catalogue (Croom et al. 2004, MNRAS 349, 1397) | position, redshift and r magnitude of 2QZ J131914.8+002709 | `http://www.2dfquasar.org/Spec_Cat/cat/2QZ_6QZ_pubcat.txt` | Public catalogue. Cite Croom et al. 2004. |
| Chen et al. 2024 (MNRAS 527, 12154), arXiv:2206.11497v2 source | the 86 candidate names in `data/candidate_names.txt` (labels of the Appendix C figures), the method, 5 published periods | `https://arxiv.org/e-print/2206.11497v2` | arXiv non-exclusive distribution licence. We use names and facts only. |

Software (pinned in `checks/requirements.txt`): numpy, scipy, astropy, pandas, matplotlib, requests, certifi. `checks/independent/` holds code written by the verification stage of the same pipeline.
