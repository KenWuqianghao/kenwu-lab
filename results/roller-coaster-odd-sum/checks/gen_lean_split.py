"""Usage: python3 -I checks/gen_lean_split.py [--check]
Generate the split Lean proof of tval witness = 798783 (block between the markers in lean/Solution.lean).
The witness is head (first K entries) ++ suf. For every sublist S of head, one lemma states
subSum S suf = v_S, proved by the kernel; the values v_S are computed here from the definition."""
from itertools import combinations
W=[8,14,3,15,6,10,2,17,7,12,1,16,5,11,4,13,9]; K=5
head, suf = W[:K], W[K:]
def idv(t):
    runs=0; prev=None
    for i in range(1,len(t)):
        d=t[i]>t[i-1]
        if d!=prev: runs+=1; prev=d
    return runs
def g(t): return idv(t) if len(t)>=3 else 0
def subsum(pre,l):
    if not l: return g(pre)
    return subsum(pre,l[1:])+subsum(pre+[l[0]],l[1:])
out=[]
out.append("/-- The last %d entries of the witness. -/\ndef witnessSuf : List ℕ := %s\n" % (len(suf), suf))
out.append("theorem witness_split : witness = %s :: witnessSuf := rfl\n" % " :: ".join(map(str,head)))
tot=0; names=[]
for mask in range(1<<K):
    S=[head[i] for i in range(K) if mask>>i&1]
    v=subsum(S,suf); tot+=v
    nm="subSum_part_%d" % mask; names.append(nm)
    out.append("set_option maxRecDepth 100000 in\ntheorem %s : subSum %s witnessSuf = %d := by decide +kernel\n" % (nm, S, v))
assert tot==798783, tot
import sys
from pathlib import Path
if "--check" in sys.argv:
    lean = (Path(__file__).resolve().parent.parent / "lean/Solution.lean").read_text()
    missing = [blk for blk in out if blk.strip() not in lean]
    print(f"{len(out) - len(missing)} of {len(out)} generated blocks found in lean/Solution.lean; parts add up to {tot}")
    sys.exit(1 if missing else 0)
print("\n".join(out))
print("NAMES", " ".join(names))
