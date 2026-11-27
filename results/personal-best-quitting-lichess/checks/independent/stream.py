"""Verifier's independent build: stream all games in time order, keep per-player state.
Usage: python stream.py OUT_NPZ END_EPOCH_STR HDRDIR [HDRDIR2]"""
import sys, os, glob, time, calendar
from array import array
import duckdb, numpy as np
out, END_S = sys.argv[1], sys.argv[2]
files = sorted((f for d in sys.argv[3:] for f in glob.glob(os.path.join(d, "20*.tsv.zst"))), key=os.path.basename)
print(len(files), "files", flush=True)
NARROW = os.environ.get('NARROW') == '1'
END = calendar.timegm(time.strptime(END_S, "%Y-%m-%d %H:%M:%S"))
con = duckdb.connect()
con.execute(f"SET memory_limit='2500MB'; SET threads=2; SET temp_directory='{out}.ducktmp'")
cols = "{'event':'VARCHAR','site':'VARCHAR','white':'VARCHAR','black':'VARCHAR','result':'VARCHAR','d':'VARCHAR','t':'VARCHAR','welo':'VARCHAR','belo':'VARCHAR','wdiff':'VARCHAR','bdiff':'VARCHAR','tc':'VARCHAR','term':'VARCHAR'}"
def allrows():
    last = -1
    for f in files:
        cur = con.execute(f"""SELECT epoch(strptime(d||' '||t,'%Y.%m.%d %H:%M:%S'))::BIGINT ts, site, white, black, event, result, welo, belo, wdiff, bdiff, tc
          FROM read_csv('{f}', delim='\t', header=false, quote='', escape='', columns={cols}) ORDER BY ts, site""")
        first = True
        while True:
            rows = cur.fetchmany(200000)
            if not rows:
                break
            if first:
                assert rows[0][0] > last, (f, rows[0][0], last)
                first = False
            last = rows[-1][0]
            yield rows
GEN = allrows()

def toint(s):
    try:
        return int(s)
    except (TypeError, ValueError):
        return None

pid_of = {}
P = []   # per player: [last_rec_index, last_speed, last_pre, last_diff, blitz_state]
# blitz_state: [n, first_pre, pb, last_ts, mask, pend_idx, last_idx, last_pre, last_diff]
A = {k: array('q') for k in ("pid", "ts", "dsec", "pre", "r", "pb", "mask0", "tourn", "opp", "idx", "gapok", "next", "rnext", "elig", "pb2", "mask20")}
NONE = -10**9
chain = {}      # (year, kind, delta_class) -> count ; kind: 'same' blitz consecutive, 'cross' speed change, 'anysame'
cnt = {"games": 0, "selfplay": 0, "nodiff_pg": 0, "pg": 0, "dupsite": 0}
t0 = time.time(); lastsite = None
def tally(year, kind, delta):
    c = 0 if delta == 0 else (1 if abs(delta) == 1 else (2 if abs(delta) <= 5 else 3))
    k = (year, kind, c); chain[k] = chain.get(k, 0) + 1

while True:
    rows = next(GEN, None)
    if not rows:
        break
    for ts, site, white, black, event, result, welo, belo, wdiff, bdiff, tc in rows:
        cnt["games"] += 1
        if site == lastsite:
            cnt["dupsite"] += 1
        lastsite = site
        if white == black:
            cnt["selfplay"] += 1
            continue
        ev = event.split(" ")
        speed = ev[1] if len(ev) > 1 else ""
        tourn = 1 if "tournament" in event else 0
        dsec = NONE
        if tc and "+" in tc:
            a, b = tc.split("+", 1)
            a, b = toint(a), toint(b)
            if a is not None and b is not None:
                dsec = 2 * (a + 40 * b)
        year = time.gmtime(ts).tm_year if cnt["games"] % 50 == 0 else None  # sampled tallies
        for name, pre_s, diff_s, opp_s, winres in ((white, welo, wdiff, belo, "1-0"), (black, belo, bdiff, welo, "0-1")):
            pid = pid_of.get(name)
            if pid is None:
                pid = len(P); pid_of[name] = pid; P.append([-1, None, None, None, None])
            pl = P[pid]
            pre = toint(pre_s); diff = toint(diff_s); opp = toint(opp_s)
            cnt["pg"] += 1
            if diff is None:
                cnt["nodiff_pg"] += 1
            if pl[0] >= 0:
                A["next"][pl[0]] = ts
            pl[0] = -1
            if year is not None and pl[1] is not None and pl[2] is not None and pl[3] is not None and pre is not None:
                tally(year, "anysame" if pl[1] == speed else "cross", pre - (pl[2] + pl[3]))
            pl[1] = speed; pl[2] = pre; pl[3] = diff
            if speed != "Blitz":
                continue
            st = pl[4]
            if st is None:
                st = pl[4] = [0, pre, None, None, 0, -1, -1, None, None, None, 0]
            if year is not None and st[0] > 0 and st[7] is not None and st[8] is not None and pre is not None:
                tally(year, "blitz", pre - (st[7] + st[8]))
            # resolve a pending previous game (no RatingDiff): its post rating is this pre
            if st[5] >= 0:
                j = st[5]; st[5] = -1
                flag = 0
                if pre is not None:
                    A["r"][j] = pre
                    pbj = A["pb"][j]
                    if pbj != NONE and pre > pbj:
                        flag = 1
                    if st[2] is None or pre > st[2]:
                        st[2] = pre
                st[4] = ((st[4] << 1) | flag) & 0xFFFFF
                flag2 = 0
                if pre is not None:
                    pb2j = A["pb2"][j]
                    if pb2j != NONE and pre > pb2j:
                        flag2 = 1
                st[10] = ((st[10] << 1) | flag2) & 0xFFFFF
            if st[6] >= 0 and pre is not None:
                A["rnext"][st[6]] = pre
            idx = st[0] + 1
            if pre is not None and (st[9] is None or pre > st[9]):
                st[9] = pre
            pb2 = st[9]; mask2 = st[10]
            pb = st[2]; mask = st[4]
            gapok = 1 if (st[3] is not None and ts - st[3] <= 30 * 86400) else 0
            r = pre + diff if (pre is not None and diff is not None) else None
            elig = 1 if (result == winres and st[1] == 1500 and idx >= 200 and gapok and ts <= END) else 0
            keep = False
            if r is None:
                keep = True
            elif elig and pb is not None:
                keep = (not NARROW) or (mask == 0 and -70 <= r - pb <= 30) or abs(((r + 50) % 100) - 50 + 0.5) < 15
            if keep:
                i = len(A["pid"])
                A["pid"].append(pid); A["ts"].append(ts); A["dsec"].append(dsec); A["pre"].append(NONE if pre is None else pre)
                A["r"].append(NONE if r is None else r); A["pb"].append(NONE if pb is None else pb)
                A["mask0"].append(1 if mask == 0 else 0); A["tourn"].append(tourn); A["opp"].append(NONE if opp is None else opp)
                A["idx"].append(idx); A["gapok"].append(gapok); A["next"].append(NONE); A["rnext"].append(NONE); A["elig"].append(elig)
                A["pb2"].append(NONE if pb2 is None else pb2); A["mask20"].append(1 if mask2 == 0 else 0)
                pl[0] = i; st[6] = i
            else:
                st[6] = -1
            if r is None:
                st[5] = i
            else:
                flag = 1 if (pb is not None and r > pb) else 0
                if pb is None or r > pb:
                    st[2] = r
                st[4] = ((mask << 1) | flag) & 0xFFFFF
                flag2 = 1 if (pb2 is not None and r > pb2) else 0
                if pb2 is None or r > pb2:
                    st[9] = r
                st[10] = ((mask2 << 1) | flag2) & 0xFFFFF
            st[0] = idx; st[3] = ts; st[7] = pre; st[8] = diff
    print(cnt["games"], len(A["pid"]), f"{time.time()-t0:.0f}s", flush=True) if cnt["games"] % 5000000 < 200000 else None
print(cnt, "players", len(P), f"{time.time()-t0:.0f}s", flush=True)
for k in sorted(chain):
    print("chain", k, chain[k])
np.savez(out, **{k: np.frombuffer(v, dtype=np.int64) for k, v in A.items()})
