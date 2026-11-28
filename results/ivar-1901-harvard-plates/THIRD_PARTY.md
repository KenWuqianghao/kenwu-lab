# Third-party material

No image or catalogue file of a third party is stored in this folder. `checks/rerun.py` downloads all images and
catalogue data again from the services below. Only the SHA-256 sums of the cutouts used for the paper are stored
(`data/cutouts.sha256`, `data/controls.sha256`, `data/cutouts/log.jsonl`).

| Source | Used for | Licence or terms | Access date |
|---|---|---|---|
| DASCH DR7 (Digital Access to a Sky Century @ Harvard), Harvard College Observatory, public API `https://api.starglass.cfa.harvard.edu/public` | plate metadata (`queryexps`; stored in derived form in `data/coverage.json` and `data/controls.json`), plate cutouts and WCS (downloaded by the checks; not stored) | Public API. DASCH asks users to acknowledge DASCH and to cite Grindlay et al. (2012), doi:10.1017/S1743921312000166 (https://dasch.cfa.harvard.edu/). Not confirmed: a formal licence text for DASCH DR7 data. | 2026-11-28 |
| ATLAS-REFCAT2 (Tonry et al. 2018, doi:10.3847/1538-4357/aae386), served by the DASCH `querycat` endpoint | reference stars (downloaded by the checks; not stored) | as served by DASCH | 2026-11-28 |
| JPL Horizons API, https://ssd.jpl.nasa.gov/api/horizons.api (NASA/JPL) | predicted positions of (1627) Ivar, orbit solution JPL#1545 (stored: `data/predictions.json`, `data/horizons_check.json`) | NASA/JPL public service | 2026-11-28 |
| JPL Small-Body Database API, https://ssd-api.jpl.nasa.gov/sbdb.api (NASA/JPL) | first observation, discovery, H and diameter of (1627) Ivar (quoted in the paper; not stored) | NASA/JPL public service | 2026-11-28 |
| Minor Planet Center `get-obs` API, https://data.minorplanetcenter.net/api/get-obs | earliest observations of (1627) Ivar (designation 1627, OBS80; 18813 lines, earliest 1929 09 25.96; quoted, not stored) | MPC public service | 2026-11-28 |
| IMCCE SkyBoT cone search, https://ssp.imcce.fr/webservices/skybot/api/conesearch.php | known solar-system objects near each 1901 position (`src/skybot.py`; stored: `data/skybot.json`) | IMCCE public service; no licence text checked | 2026-11-28 |
| Code in `src/measure.py`, `src/dasch.py`, `src/hz.py`, `src/fetch.py`, `src/predict.py` | copied or adapted from the result `ganymed-1898-harvard-plates` of the same repository (same author) | Apache-2.0, as the repository | 2026-11-28 |
