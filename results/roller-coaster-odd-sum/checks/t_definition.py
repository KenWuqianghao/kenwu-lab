"""Evaluate t(pi) directly from the Ahmed-Snevily definition: sum over all subsequences tau
with |tau| >= 3 of id(tau) = number of maximal increasing runs + maximal decreasing runs
(runs of at least two contiguous entries). Also checks the Odd Sum condition."""
import sys
from itertools import combinations
def idv(t):
    runs=0; prev=None
    for i in range(1,len(t)):
        d = t[i]>t[i-1]
        if d!=prev: runs+=1; prev=d
    return runs
def t_def(p):
    n=len(p); s=0
    for mask in range(1<<n):
        if bin(mask).count('1')>=3:
            s+=idv([p[i] for i in range(n) if mask>>i&1])
    return s
if __name__ == "__main__":
    assert t_def([2,1,4,3])==11 and t_def([1,2,3,4])==5   # examples in the source
    p=[8,14,3,15,6,10,2,17,7,12,1,16,5,11,4,13,9]          # Botler-Netto Table 1, N=17
    assert sorted(p)==list(range(1,18))
    print('t =',t_def(p))
    n=len(p); print('pair sums', [(j+1,p[j]+p[n-1-j]) for j in range(n//2)])
