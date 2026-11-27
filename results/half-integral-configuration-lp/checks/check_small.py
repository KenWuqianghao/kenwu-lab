"""Exact check of the second counterexample (5 machines, 14 jobs, found by a random search).
1. The rational x in instance_small.json is a point of CLP(P,T) (exact Fractions).
2. sum p > m (T-1), so LP(P) = T.
3. Exhaustive depth-first search: no half-integral point in CLP(P,T)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json
from check_counterexample import check_point, no_half_integral
d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance_small.json'))); M = [set(q) for q in d['M']]
check_point(d['p'], M, d['m'], d['T'], d['x']); print('1. CLP(P,T) point: verified')
assert sum(d['p']) > d['m'] * (d['T'] - 1); print(f"2. LP(P) = {d['T']}: verified")
assert no_half_integral(d['p'], M, d['m'], d['T']); print('3. no half-integral point (exhaustive search): verified')
