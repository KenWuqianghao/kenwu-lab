# Third-party data
- Retrosheet event files 2009–2025, https://www.retrosheet.org/events/YYYYeve.zip, accessed 2026-11-28.
  License notice required by Retrosheet: "The information used here was obtained free of charge from
  and is copyrighted by Retrosheet. Interested parties may contact Retrosheet at www.retrosheet.org."
  SHA-256 of each file: `data/expected.json`, key `retrosheet_sha256`.
- MLB Stats API, season hitting totals 2009–2025,
  `https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&season=YYYY&sportId=1&gameType=R&limit=3000&playerPool=ALL`,
  accessed 2026-11-28. Notice in each response: "Copyright 2026 MLB Advanced Media, L.P. Use of any
  content on this page acknowledges agreement to the terms posted here
  http://gdx.mlb.com/components/copyright.txt". Used only for validation; not redistributed.
- Chadwick Bureau register, https://github.com/chadwickbureau/register (commit
  ba48ce101349a2156c7a5420f54d13e8ef3a4256), `data/people-*.csv`, accessed 2026-11-28. License: Open
  Data Commons Attribution License 1.0. Used for the ID map from MLBAM to Retrosheet.
- Lahman database (Chadwick Baseball Databank format), `core/Batting.csv` and `core/People.csv` from
  the mirror https://github.com/cbwinslow/baseballdatabank (commit
  8a908d51833ee99b56fce165c93dc99ee8886d6f), accessed 2026-11-28. License (from its README): Creative
  Commons Attribution-ShareAlike 3.0, Chadwick Baseball Bureau. Seasons to 2021. The equality of this
  mirror with an official release is not confirmed.
- Source paper full text (read only, not committed): web.archive.org copy of the Wharton in-press PDF
  (URL in `PRIOR_ART.md`).
