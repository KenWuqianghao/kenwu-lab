# Third-party material

| Source | Use | License | Accessed |
|---|---|---|---|
| Lichess open database, standard rated games, monthly files 2013-01 to 2016-12, `https://database.lichess.org/standard/` | All game data. Only 13 PGN header tags are read. The files are not redistributed; `checks/rerun.py` downloads them. Checksums: `https://database.lichess.org/standard/sha256sums.txt`. | CC0 1.0 (stated on database.lichess.org) | 2026-11-25 |
| lichess-org/lila on GitHub, commits `5e9fde4a` (2015-12-26), `4dacb459` (2016-01-10), `b928a2c8` (2015-12-24) | Date of the "Highest rating" display (addendum A). Commit metadata and diff text were read through the GitHub API. No code is copied. | AGPL-3.0 | 2026-11-25 |
| A. Anderson, E. A. Green, "Personal bests as reference points", PNAS 115(8):1772-1776 (2018), full text from Europe PMC (PMC5828569) | Claim under test and its definitions. Short quotes only. | Article text (copyright of the authors/PNAS); quoted under fair use | 2026-11-25 |
| Python packages: duckdb 2.0.1, numpy 2.5.5, pandas 3.1.1, pyarrow 26.0.1, matplotlib 3.11.2 (and statsmodels 0.15.0 for `checks/independent/`) | Analysis. Installed by `checks/ci.sh`; not redistributed. | MIT / BSD / Apache-2.0 | 2026-11-25 |
