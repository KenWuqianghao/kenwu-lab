# Third-party data

| Source | URL | Use | License / terms | Accessed |
|---|---|---|---|---|
| USGS ComCat (FDSN event service) | `https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&eventtype=earthquake&minmagnitude=7&orderby=time-asc&starttime=1900-01-01T00:00:00&endtime=2026-01-01T00:00:00` | All M≥7 events 1900–2025 (1607 events). Snapshot of id, time, latitude, longitude, depth, mag, magType in `data/comcat_m7_1900_2025.csv` (sha256 e3726621…0a28). | US Government work, public domain (USGS). | 2026-11-25 |
| Paris Observatory EOP C02 (experimental long-term UT1/LOD, C. Bizouard) | `https://hpiers.obspm.fr/eoppc/series/longterm/eopc02.1830-now` (description: `eopc02.txt` in the same folder) | LOD 1830–2026 at 100-day steps; annual means and the deceleration mask. File last modified 2026-11-01; sha256 45a9ffb4…1601. Not stored in git (re-downloaded by `checks/rerun.py`). | No license statement found on the server. Free public download. Source data: Jordi et al. 1994 (GJI 117:811) before 1955, AICAS 1955–1962, IERS C04 after 1962. Cite these. | 2026-11-25 |
| IERS EOP 20 C04 | `https://datacenter.iers.org/data/latestVersion/EOP_20_C04_one_file_1962-now.txt` | Cross-check of C02 annual LOD 1962–2024 only. The downloaded file ends 2025-05-05. | IERS products are free to use with citation of the IERS. No separate license file checked. | 2026-11-25 |
