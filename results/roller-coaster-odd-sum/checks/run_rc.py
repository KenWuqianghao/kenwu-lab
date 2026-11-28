"""Exact RC(n) by both search programs, and a test of Conjecture 2.4 on it.

  python3 -I checks/run_rc.py N T [--workers W] [--only obb|v2] [--out DIR] [--write]

Runs, W processes at a time (default: number of CPUs):
  oddsum_bb N T 0 <job> 4 2          job = 0..3
  v2_bb     N T 0 <v> <v>            v = 1..ceil(N/2)
Each program lists every permutation of [N] with t >= T and pi_1 <= ceil(N/2). If some permutation
reaches T, the largest listed value is tmax(N). The complements of the listed permutations give the
rest of RC(N) (the complement keeps t). The script checks that the two programs give the same list,
re-evaluates every listed permutation, and compares RC(N) with data/rc<N>.txt (--write creates it).
Exits 1 if a check fails."""
import argparse, os, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rc_lib import t_turn, odd_sum, complement, read_list, read_obb, read_v2, summary

root = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("n", type=int); ap.add_argument("T", type=int)
ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
ap.add_argument("--only", choices=["obb", "v2"])
ap.add_argument("--out", default=None)
ap.add_argument("--write", action="store_true")
args = ap.parse_args()
n, T, h = args.n, args.T, (args.n + 1) // 2
out = Path(args.out or tempfile.mkdtemp(prefix=f"rc{n}-"))
out.mkdir(parents=True, exist_ok=True)
cc = os.environ.get("CC") or next((c for c in ("cc", "gcc", "clang", "leanc") if shutil.which(c)), None)
if cc is None:
    sys.exit("no C compiler found; set CC")
bins = {"obb": out / "oddsum_bb", "v2": out / "v2_bb"}
src = {"obb": root / "checks/oddsum_bb.c", "v2": root / "checks/independent/v2_bb.c"}
for k in bins:
    subprocess.run([cc, "-O2", "-o", str(bins[k]), str(src[k])], check=True)
tasks = []
if args.only in (None, "v2"):
    tasks += [("v2", v, [str(bins["v2"]), str(n), str(T), "0", str(v), str(v)]) for v in range(h, 0, -1)]
if args.only in (None, "obb"):
    tasks += [("obb", j, [str(bins["obb"]), str(n), str(T), "0", str(j), "4", "2"]) for j in range(4)]

def run(task):
    prog, i, cmd = task
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    (out / f"{prog}_{i}.out").write_text(r.stdout)
    print(f"{prog} {i}: exit {r.returncode}, {time.time() - t0:.0f} s", flush=True)
    return prog, i, r.returncode, r.stdout

print(f"n={n} T={T}; compiler {cc}; {len(tasks)} processes, {args.workers} at a time; outputs in {out}", flush=True)
with ThreadPoolExecutor(args.workers) as ex:
    results = list(ex.map(run, tasks))

ok = True
def check(cond, msg):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + msg)

lists = {}
for prog in ("obb", "v2"):
    rs = [r for r in results if r[0] == prog]
    if not rs:
        continue
    perms, sums = [], []
    for _, i, code, text in rs:
        perms += read_obb(text, n) if prog == "obb" else read_v2(text)
        sums += [s for s in summary(text) if s["n"] == str(n)]
    S = {p for _, p in perms}
    check(all(r[2] == 0 for r in rs) and len(sums) == len(rs), f"{prog}: all processes exit 0 and print SUMMARY")
    check(len(S) == len(perms) > 0, f"{prog}: {len(S)} distinct permutations with t >= {T}")
    check(all(sorted(p) == list(range(1, n + 1)) and p[0] <= h and t_turn(p) == t for t, p in perms), f"{prog}: every listed permutation re-evaluated")
    tmax = max(t for t, _ in perms)
    lists[prog] = {p for t, p in perms if t == tmax}
    print(f"{prog}: tmax({n}) = {tmax}; {len(lists[prog])} maximisers with pi_1 <= {h}")
if len(lists) == 2:
    check(lists["obb"] == lists["v2"], "the two programs give the same maximisers")
M = next(iter(lists.values()))
rc = sorted(M | {complement(p) for p in M})
tm = t_turn(rc[0])
nodd = sum(odd_sum(p) for p in rc)
print(f"RESULT n={n} tmax={tm} |RC(n)|={len(rc)} odd_sum_members={nodd} closed_under_reversal={all(p[::-1] in set(rc) for p in rc)}")
path = root / f"data/rc{n}.txt"
if args.write:
    path.write_text(f"# RC({n}): the {len(rc)} permutations of [{n}] with t = tmax({n}) = {tm}.\n"
                    f"# Output of checks/run_rc.py {n} {T} (both programs), with complements.\n"
                    + "".join(" ".join(map(str, p)) + "\n" for p in rc))
    print("wrote", path.relative_to(root))
else:
    check(path.is_file() and sorted(read_list(path)) == rc, f"RC({n}) equals data/rc{n}.txt")
print("run_rc: ALL PASS" if ok else "run_rc: FAILED")
sys.exit(0 if ok else 1)
