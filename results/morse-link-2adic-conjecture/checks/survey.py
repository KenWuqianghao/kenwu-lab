"""Survey: for k=1..K, test Conjecture 4.12 on 2<=n<=N, and the variant that starts at n=4."""
import sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from explore_lib import wcat, v2, s2
from consistency import check
N=int(sys.argv[1]); K=int(sys.argv[2])
C=wcat(lambda h:1,N)
for k in range(1,K+1):
    L=wcat(lambda h,k=k:(2*h+1)**(2*k),N)
    d={n:(None if L[n]==C[n] else v2(L[n]-C[n])-s2(n)) for n in range(2,N+1)}
    r2=[r for r in check(d,2,N) if r[2]]
    r4=[r for r in check(d,4,N) if r[2]]
    bad=[r for r in check(d,2,N) if r[1] is not None and not r[2]]
    print(f"k={k:2d} k%4={k%4} d(3)={d[3]:3d}  n>=2: {'consistent c=%d'%r2[0][1] if r2 else 'FAILS '+str(bad[0][3])}   n>=4: {'consistent c=%d'%r4[0][1] if r4 else 'FAILS'}")
