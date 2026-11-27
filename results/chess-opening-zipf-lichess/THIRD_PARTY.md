# Third-party material

| Source | What | License | Access date |
|---|---|---|---|
| Lichess open database, https://database.lichess.org/standard/ | Standard rated games, monthly files 2013-01 to 2015-12 (`lichess_db_standard_rated_YYYY-MM.pgn.zst`), `counts.txt`, `sha256sums.txt`. Not included here: `checks/download.sh` downloads them. | CC0 1.0 (stated on database.lichess.org) | 2026-11-25 |
| B. Blasius, R. Tönjes, arXiv:0704.2711v2 (PRL 103, 218701, 2009) | Read for the claims and the definitions. Short quotes only. | arXiv non-exclusive license | 2026-11-25 |
| numpy, scipy, powerlaw, matplotlib (PyPI) | Analysis and figure. Installed by `checks/ci.sh` from `checks/requirements.txt`; not included. | BSD-3, BSD-3, MIT, matplotlib license (PSF-based) | 2026-11-25 |

`data/sha256sums_2013_2015.txt` and `data/counts_2013_2015.txt` are copies of the matching lines of the Lichess `sha256sums.txt` and `counts.txt`.
