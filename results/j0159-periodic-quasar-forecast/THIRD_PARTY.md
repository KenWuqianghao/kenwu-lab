# Third-party data

All sources are public and need no account. Access date: 2026-11-28.

| Source | What we use | Access | Licence or terms |
|---|---|---|---|
| Zwicky Transient Facility (ZTF) public light curves, NASA/IPAC Infrared Science Archive (IRSA) | zg and zr points of the quasar in a 2.2-arcsec circle, MJD 58298.5 to 60969.3. Downloaded by `checks/rerun.py`; not redistributed here. The service output does not name the data release. The IRSA ZTF page listed Data Release 24 as the newest on the access date; that the service used it is not confirmed. SHA-256 of the file: `data/expected.json` key `ztf_csv_sha256`. | `https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves` | ZTF public data. Users must acknowledge ZTF and IRSA and cite Bellm et al. 2019 (PASP 131, 018002) and Masci et al. 2019 (PASP 131, 018003). |
| arXiv source of Zheng et al. 2016 (ApJ 827, 56), arXiv:1512.08730: file `lc.eps` (Fig. 1) and `ms.tex` | the quoted formula (`ms.tex` line 303); the 252 CRTS V points and the fit curve of Fig. 1a, read from the PostScript commands by `checks/rerun.py`. The figure and the points are not redistributed here. SHA-256 of `lc.eps`: key `addendum1.lc_eps_sha256`. | `https://arxiv.org/src/1512.08730` | arXiv non-exclusive distribution licence. We use measured values and short quotes, with citation. |
| Charisi et al. 2018 (arXiv:1801.06189); D'Orazio and Charisi 2023 (arXiv:2310.16896) | short quotes about the candidate | `https://arxiv.org` | arXiv licence; quoted with citation |
| Semantic Scholar Graph API | citation list for the prior-art search | `https://api.semanticscholar.org` | Semantic Scholar API terms |
| Crossref API, arXiv API | bibliographic data of the references | `https://api.crossref.org`, `https://export.arxiv.org/api` | metadata openly available |

Software (pinned in `checks/requirements.txt`): numpy 2.5.5, matplotlib 3.11.2. The paper was built with Tectonic 0.15.0.
