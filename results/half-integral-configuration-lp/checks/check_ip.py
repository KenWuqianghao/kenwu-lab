"""Integer optimum of the main instance (context only; not part of the disproof).

Usage: python3 -I checks/check_ip.py checks/instance.json
1. An explicit assignment of every job to an allowed machine has makespan 4.
   Machines (0,t) and (1,t) take one filler of their pair and the point P(c,t+1 mod 4);
   machine (2,t) takes the point P(2,t+1 mod 4).
2. CLP(P,3) has no integral point (an integral point is half-integral, and the main
   theorem excludes those), so IP(P) = 4 and the gap of this instance is 4/3.
"""
import json, sys
from fractions import Fraction

d = json.load(open(sys.argv[1]))
p, M, m = d["p"], [set(q) for q in d["M"]], d["m"]
names = d["names"]
job = {nm: j for j, nm in enumerate(names)}
assign = {}
for c in range(3):
    for t in range(4):
        i = 4 * c + t
        assign[job[f"P{c}{(t + 1) % 4}"]] = i
        if c < 2:
            assign[job[f"F{2 * t + c}"]] = i
assert sorted(assign) == list(range(len(p))), "every job is assigned once"
assert all(i in M[j] for j, i in assign.items()), "every job is on an allowed machine"
loads = [sum(p[j] for j, i in assign.items() if i == k) for k in range(m)]
print("1. loads of the integral assignment:", loads, "makespan", max(loads))
assert max(loads) == 4
print("2. IP(P) = 4, LP(P) = 3, gap of this instance:", Fraction(4, 3))
