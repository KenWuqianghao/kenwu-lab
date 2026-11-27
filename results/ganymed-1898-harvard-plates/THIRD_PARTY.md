# Third-party material

No third-party file is stored in this folder except the tables listed here. `checks/rerun.py` downloads all images and
catalogue data again from the services below.

| Source | Used for | Licence or terms | Access date |
|---|---|---|---|
| DASCH DR7 (Digital Access to a Sky Century @ Harvard), public API `https://api.starglass.cfa.harvard.edu/public` | plate metadata, plate cutouts and WCS (downloaded by the checks; only their SHA-256 sums are stored, in `data/cutouts.sha256` and `data/cutouts/log.jsonl`) | No licence text found on https://dasch.cfa.harvard.edu/dr7/, /citing/ and /data-access/ (checked 2026-11-27). The site footer links the Harvard terms of use (https://hwp.harvard.edu/terms-use). DASCH asks users to acknowledge DASCH and to cite Grindlay et al. (2012), doi:10.1017/S1743921312000166. Not confirmed: whether DASCH DR7 data have a formal licence. | 2026-11-27 |
| ATLAS-REFCAT2 (Tonry et al. 2018, doi:10.3847/1538-4357/aae386), served by the DASCH `querycat` endpoint | reference stars (downloaded by the checks; not stored) | as served by DASCH | 2026-11-27 |
| HDAP (Heidelberg Digitized Astronomical Plates), GAVO Data Center: TAP `https://dc.g-vo.org/tap` (table `lsw.plates`) and SODA cutouts | plate table (stored: `data/hdap/plates_1895_1907.csv`, `data/hdap/hektor_cover.csv` derived from it) and cutouts (downloaded by the checks) | CC0 1.0 (resource page https://dc.g-vo.org/browse/lswscans/res/positions, checked 2026-11-27). Requested acknowledgement: "This work made use of the HDAP which was produced at Landessternwarte Heidelberg-Königstuhl under grant No. 00.071.2005 of the Klaus-Tschira-Foundation." | 2026-11-27 |
| JPL Horizons and JPL Small-Body Database APIs (NASA/JPL) | ephemerides (stored in `data/prereg/predictions*.json`); first-observation dates | NASA/JPL public services | 2026-11-27 |
| Minor Planet Center `get-obs` API | earliest observations of (1036), (624), (12126) (verification stage; not stored) | MPC public service | 2026-11-27 |
