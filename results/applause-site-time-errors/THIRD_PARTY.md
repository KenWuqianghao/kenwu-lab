# Third-party material

| Source | What we use | Licence / terms | Access date |
|---|---|---|---|
| APPLAUSE Data Release 4, Leibniz Institute for Astrophysics Potsdam (AIP), https://www.plate-archive.org, [doi:10.17876/plate/dr.4](https://doi.org/10.17876/plate/dr.4) | Columns of `applause_dr4.plate` and `applause_dr4.exposure`, read through the anonymous TAP service `https://www.plate-archive.org/tap/sync`. Derived values in `data/` (counts, fractions, and the per-exposure table `data/vatican_corrected.csv`, which repeats DR4 identifiers, object names, logged dates and times, and `ut_mid`). | CC0 1.0 Universal, as stated on the DR4 landing page (https://www.plate-archive.org/metadata/applause_dr4/). The page asks for an acknowledgement; the paper and README give it. | 2026-11-27 |

The raw downloads are not in this folder. `checks/fetch.sh`, `checks/fetch_ra.sh` and `checks/fetch_501.sh` download them again.

Acknowledgement requested by APPLAUSE: "Funding for APPLAUSE has been provided by DFG (German Research Foundation, Grant), Leibniz Institute for Astrophysics Potsdam (AIP), Dr. Remeis Sternwarte Bamberg (University Nuernberg/Erlangen), the Hamburger Sternwarte (University of Hamburg) and Tartu Observatory. Plate material also has been made available from Thüringer Landessternwarte Tautenburg, and from the archives of the Vatican Observatory."
