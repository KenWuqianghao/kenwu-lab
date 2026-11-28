"""Main computation: fact (ii) by two independent exact searches, compared with data/.

  python3 -I checks/run_n17.py [--workers W] [--only obb|v2] [--out DIR]

1. Compiles checks/oddsum_bb.c and checks/independent/v2_bb.c with $CC (default: the first of cc, gcc,
   clang, leanc that exists), flag -O2.
2. Runs, W processes at a time (default: number of CPUs):
     oddsum_bb 17 798775 1 <job> 4 2      job = 0..3  (Odd Sum permutations, threshold 798775)
     v2_bb     17 798775 1 <v> <v>        v = 1..9    (the same question, first entry pi_1 = v)
   Both programs list every Odd Sum permutation of [17] with t >= 798775 and pi_1 <= 9.
3. Checks: each program lists exactly the 96 permutations of data/oddsum17_t798775.txt, all with
   t = 798775 (re-evaluated here with the turn identity), so no Odd Sum permutation has t >= 798776;
   the node counts of oddsum_bb equal data/expected.json.
Exits 1 if a check fails."""
import argparse, json, os, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rc_lib import t_turn, odd_sum, read_list, read_obb, read_v2, summary

root = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
ap.add_argument("--only", choices=["obb", "v2"])
ap.add_argument("--out", default=None, help="directory for the raw outputs (default: a temporary one)")
args = ap.parse_args()
out = Path(args.out or tempfile.mkdtemp(prefix="rc17-"))
out.mkdir(parents=True, exist_ok=True)
exp = json.loads((root / "data/expected.json").read_text())["fact_ii"]

cc = os.environ.get("CC") or next((c for c in ("cc", "gcc", "clang", "leanc") if shutil.which(c)), None)
if cc is None:
    sys.exit("no C compiler found; set CC")
bins = {"obb": out / "oddsum_bb", "v2": out / "v2_bb"}
src = {"obb": root / "checks/oddsum_bb.c", "v2": root / "checks/independent/v2_bb.c"}
for k in bins:
    subprocess.run([cc, "-O2", "-o", str(bins[k]), str(src[k])], check=True)

tasks = []
if args.only in (None, "v2"):
    tasks += [("v2", v, [str(bins["v2"]), "17", "798775", "1", str(v), str(v)]) for v in range(9, 0, -1)]
if args.only in (None, "obb"):
    tasks += [("obb", j, [str(bins["obb"]), "17", "798775", "1", str(j), "4", "2"]) for j in range(4)]

def run(task):
    prog, i, cmd = task
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    (out / f"{prog}_{i}.out").write_text(r.stdout)
    print(f"{prog} {i}: exit {r.returncode}, {time.time() - t0:.0f} s", flush=True)
    return prog, i, r.returncode, r.stdout

print(f"compiler {cc}; {len(tasks)} processes, {args.workers} at a time; outputs in {out}", flush=True)
with ThreadPoolExecutor(args.workers) as ex:
    results = list(ex.map(run, tasks))

ref = set(read_list(root / "data/oddsum17_t798775.txt"))
ok = True
def check(cond, msg):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + msg)

for prog in ("obb", "v2"):
    rs = [r for r in results if r[0] == prog]
    if not rs:
        continue
    check(all(r[2] == 0 for r in rs), f"{prog}: all processes exit 0")
    perms, sums = [], []
    for _, i, _, text in rs:
        perms += read_obb(text, 17) if prog == "obb" else read_v2(text)
        sums += [dict(s, idx=i) for s in summary(text) if s["n"] == "17"]
    found = sum(int(s["found"]) for s in sums)
    best = max(int(s["best"]) for s in sums)
    S = {p for _, p in perms}
    check(len(sums) == len(rs), f"{prog}: one SUMMARY line per process")
    check(found == len(perms) == len(S) == 96, f"{prog}: found = {found} permutations with t >= 798775")
    check(best == 798775 and all(t == 798775 for t, _ in perms), f"{prog}: best = {best}")
    check(all(t_turn(p) == t and odd_sum(p) and p[0] <= 9 for t, p in perms), f"{prog}: every listed permutation re-evaluated: Odd Sum, pi_1 <= 9, t as printed")
    check(S == ref, f"{prog}: the list equals data/oddsum17_t798775.txt")
    if prog == "obb":
        nodes = {str(s["idx"]): int(s["nodes"]) for s in sums}
        check(nodes == exp["oddsum_bb_nodes"], f"obb: node counts {nodes} equal data/expected.json")
    else:
        nodes = sum(int(s["nodes"]) for s in sums)
        check(nodes == exp["v2_bb_nodes_total"], f"v2: total node count {nodes} equals data/expected.json")
print("run_n17: ALL PASS" if ok else "run_n17: FAILED")
sys.exit(0 if ok else 1)
