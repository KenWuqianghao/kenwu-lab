"""Build the player-game table from the header TSVs (PROTOCOL.md sections 3-4).

Usage: python build.py HDR_DIR[:HDR_DIR2...] OUT_PARQUET
Env: NFILES (expected number of monthly files, default 36), END (last start time kept,
default '2015-12-30 23:59:59'), DUCK_TMP (spill folder), NBUCKETS (player buckets, default 8).

Writes one row per player-game for speeds Bullet, Blitz, Classical that passes sample rules
2, 3, 5, 6, 7 of the protocol. Self-play games (White = Black) are excluded (addendum B). The PB filter (rule 4) is a column (pb_prev20), so the
round-number control can use the same file. Players are processed in buckets (pid mod NBUCKETS)
to limit memory and disk spill; all window functions are per player, so buckets do not change
the result.
"""
import sys, os, glob, time, shutil
import duckdb

hdr, out = sys.argv[1], sys.argv[2]
t0 = time.time()
tmp = os.environ.get("DUCK_TMP", os.path.join(os.path.dirname(os.path.abspath(out)), "duck_tmp"))
END = os.environ.get("END", "2015-12-30 23:59:59")
NB = int(os.environ.get("NBUCKETS", 8))
stage = out + ".stage"
shutil.rmtree(stage, ignore_errors=True)
os.makedirs(stage)
con = duckdb.connect()
con.execute(f"SET memory_limit='3GB'; SET threads={os.environ.get('HEAVY_THREADS', '2')}; "
            f"SET temp_directory='{tmp}'; SET preserve_insertion_order=false")
files = sorted(f for d in hdr.split(":") for f in glob.glob(os.path.join(d, "20*.tsv.zst")))
assert len(files) == int(os.environ.get("NFILES", 36)), len(files)
cols = ("{'event':'VARCHAR','site':'VARCHAR','white':'VARCHAR','black':'VARCHAR','result':'VARCHAR',"
        "'d':'VARCHAR','t':'VARCHAR','welo':'VARCHAR','belo':'VARCHAR','wdiff':'VARCHAR','bdiff':'VARCHAR',"
        "'tc':'VARCHAR','term':'VARCHAR'}")
csv = f"read_csv({files}, delim='\t', header=false, quote='', escape='', columns={cols})"
con.execute(f"""CREATE TABLE pl AS SELECT player, row_number() OVER (ORDER BY player) pid FROM
  (SELECT white player FROM {csv} UNION SELECT black FROM {csv})""")
print("players", con.execute("SELECT count(*) FROM pl").fetchone()[0], f"{time.time()-t0:.0f}s", flush=True)
# Player-games, written once to parquet, partitioned by player bucket.
# Self-play games (White = Black, a 2013 Lichess artifact) are excluded.
con.execute(f"""COPY (
WITH g AS (SELECT split_part(event,' ',2) speed, contains(event,'tournament') tourn,
       substr(site, 21) gid, white, black, result,
       strptime(d||' '||t,'%Y.%m.%d %H:%M:%S') ts,
       try_cast(welo AS INT) welo, try_cast(belo AS INT) belo,
       try_cast(wdiff AS INT) wdiff, try_cast(bdiff AS INT) bdiff,
       CASE WHEN tc LIKE '%+%' THEN 2*(try_cast(split_part(tc,'+',1) AS INT) + 40*try_cast(split_part(tc,'+',2) AS INT)) END dsec
     FROM {csv} WHERE white <> black)
SELECT p.pid % {NB} b, p.pid, g.speed, g.tourn, g.gid, g.ts, g.dsec, g.welo pre, g.wdiff diff, g.belo opp,
       (g.result = '1-0')::INT win
FROM g JOIN pl p ON p.player = g.white
UNION ALL
SELECT p.pid % {NB} b, p.pid, g.speed, g.tourn, g.gid, g.ts, g.dsec, g.belo, g.bdiff, g.welo, (g.result = '0-1')::INT
FROM g JOIN pl p ON p.player = g.black
) TO '{stage}/pg' (FORMAT parquet, PARTITION_BY (b))""")
con.execute("DROP TABLE pl")
print("player-games written", f"{time.time()-t0:.0f}s", flush=True)

n_rows = n_dup = 0
for b in range(NB):
    src = f"read_parquet('{stage}/pg/b={b}/*.parquet', hive_partitioning=false)"
    # A game can appear twice at a month edge; keep one row per (player, game).
    con.execute(f"""CREATE TABLE pg AS SELECT * FROM {src}
      QUALIFY row_number() OVER (PARTITION BY pid, gid ORDER BY ts, speed, pre, opp) = 1""")
    n = con.execute(f"SELECT count(*) FROM {src}").fetchone()[0]
    m = con.execute("SELECT count(*) FROM pg").fetchone()[0]
    n_rows += m
    n_dup += n - m
    # Next game of any speed (quit outcome).
    con.execute("CREATE TABLE pg2 AS SELECT *, lead(ts) OVER (PARTITION BY pid ORDER BY ts, gid) next_ts FROM pg")
    con.execute("DROP TABLE pg")
    # Per speed: post rating, game index, first rating, previous game time.
    con.execute("""CREATE TABLE s1 AS SELECT *,
      coalesce(pre + diff, lead(pre) OVER w) r,
      row_number() OVER w idx,
      first_value(pre) OVER w first_pre,
      lag(ts) OVER w prev_ts
    FROM pg2 WHERE speed IN ('Bullet','Blitz','Classical')
    WINDOW w AS (PARTITION BY pid, speed ORDER BY ts, gid)""")
    con.execute("DROP TABLE pg2")
    con.execute("""CREATE TABLE s2 AS SELECT *,
      max(r) OVER (PARTITION BY pid, speed ORDER BY ts, gid ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) pb
    FROM s1""")
    con.execute("DROP TABLE s1")
    con.execute("""CREATE TABLE s3 AS SELECT *,
      coalesce(sum(CASE WHEN r > pb THEN 1 ELSE 0 END) OVER (PARTITION BY pid, speed ORDER BY ts, gid
        ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING), 0) pb_prev20
    FROM s2""")
    con.execute("DROP TABLE s2")
    con.execute(f"""COPY (
    SELECT pid, speed, tourn, ts, dsec, pre, r, pb, opp, idx, pb_prev20,
      r - pb x,
      epoch(ts - prev_ts) / 60.0 prev_gap_min,
      CASE WHEN next_ts IS NULL THEN NULL ELSE epoch(next_ts - ts) / 60.0 END next_gap_min
    FROM s3
    WHERE win = 1 AND first_pre = 1500 AND idx >= 200 AND r IS NOT NULL AND pb IS NOT NULL
      AND epoch(ts - prev_ts) <= 30*86400 AND ts <= TIMESTAMP '{END}'
    ) TO '{stage}/part{b}.parquet' (FORMAT parquet)""")
    con.execute("DROP TABLE s3")
    print(f"bucket {b} done", f"{time.time()-t0:.0f}s", flush=True)
print(f"player-games {n_rows}, duplicates dropped {n_dup}", flush=True)
con.execute(f"COPY (SELECT * FROM '{stage}/part*.parquet' ORDER BY pid, speed, idx) TO '{out}' (FORMAT parquet)")
shutil.rmtree(stage)
print("rows out", con.execute(f"SELECT count(*), count(*) FILTER (WHERE speed='Blitz') FROM '{out}'").fetchone(),
      f"total {time.time()-t0:.0f}s", flush=True)
