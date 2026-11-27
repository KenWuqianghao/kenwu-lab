"""The fixed plate list (chosen from DASCH coverage before any image was seen).
Selection rule: DASCH DR7 plates taken before the object's first observation in JPL SBDB, with the
object inside the plate (edge distance > offset) and limMag - (V + 0.8) > 0.3, where 0.8 is an assumed B-V."""
SITE = {"b": "800", "a": "800", "i": "802", "ac": "802", "ai": "802", "am": "802", "me": "802"}  # MPC codes: 800 Arequipa, 802 Cambridge
PLATES = [
    # object, horizons id, plate, solnum, DASCH expdate (midpoint), exptime (min), DASCH limMag
    ("Hektor", "624;", "b23074", 0, "1899-06-18T04:24", 10, 15.861),
    ("Hektor", "624;", "b23499", 0, "1899-07-18T02:22", 10, 15.752),
    ("Hektor", "624;", "b28100", 0, "1901-07-28T07:07", 10, 16.077),
    ("Hektor", "624;", "b28276", 0, "1901-08-23T06:06", 60, 15.646),
    ("Hektor", "624;", "b28503", 0, "1901-09-10T05:53", 60, 16.118),
    ("Ganymed", "1036;", "i21050", 0, "1898-08-14T07:12", 14, 13.873),
    ("Ganymed", "1036;", "ac00044", 0, "1898-09-21T05:31", 94, 12.360),
    ("Ganymed", "1036;", "i21576", 0, "1898-11-01T05:01", 12, 13.630),
    ("Ganymed", "1036;", "i21780", 0, "1898-11-26T02:12", 13, 13.410),
    ("Ganymed", "1036;", "ac00115", 0, "1898-12-10T01:45", 63, 13.629),
    ("Ganymed", "1036;", "i22152", 0, "1899-01-20T01:07", 10, 13.625),
]
FIRST_OBS = {"Hektor": "1907-02-11", "Ganymed": "1924-10-23"}

# Round 2 (Hektor confirmation), chosen 2026-11-27 before any of these images was seen: every DASCH plate before
# 1907-02-11 in the coverage list with a limiting magnitude and limMag - (V + 0.8) >= -0.3, not used in round 1.
PLATES2 = [
    ("Hektor", "624;", "b19427", 0, "1897-06-09T00:56", 13, 15.559),
    ("Hektor", "624;", "b23969", 0, "1899-08-25T02:42", 12, 16.199),
    ("Hektor", "624;", "b26258", 0, "1900-09-21T02:26", 60, 15.878),
    ("Hektor", "624;", "b28016", 0, "1901-07-26T05:35", 10, 15.382),
    ("Hektor", "624;", "b28302", 0, "1901-08-24T05:01", 12, 15.363),
    ("Hektor", "624;", "b28586", 0, "1901-09-22T02:51", 10, 15.220),
    ("Hektor", "624;", "a06535", 0, "1903-09-03T07:16", 10, 15.760),
    ("Hektor", "624;", "a07135", 0, "1905-01-13T01:10", 10, 15.360),
]
