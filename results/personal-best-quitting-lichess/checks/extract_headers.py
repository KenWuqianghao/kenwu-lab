"""Read Lichess PGN header lines on stdin; write one TSV row per game on stdout.
Columns: site, event, white, black, result, utcdate, utctime, welo, belo, wdiff, bdiff, timecontrol, termination.
Missing values are empty strings."""
import sys
KEYS = ["Site", "White", "Black", "Result", "UTCDate", "UTCTime", "WhiteElo", "BlackElo",
        "WhiteRatingDiff", "BlackRatingDiff", "TimeControl", "Termination"]
IDX = {k: i + 1 for i, k in enumerate(KEYS)}
out = sys.stdout.write
row = None
for line in sys.stdin:
    if not line.startswith("["):
        continue
    sp = line.find(" ")
    key = line[1:sp]
    val = line[sp + 2:line.rfind('"')]
    if key == "Event":
        if row is not None:
            out("\t".join(row) + "\n")
        row = [val] + [""] * len(KEYS)
    elif row is not None:
        i = IDX.get(key)
        if i is not None:
            row[i] = val.replace("\t", " ")
if row is not None:
    out("\t".join(row) + "\n")
