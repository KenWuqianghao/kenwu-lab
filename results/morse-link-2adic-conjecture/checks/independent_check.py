# independent checker: weighted Catalan via continued-fraction / height DP
from fractions import Fraction
from math import comb
def wc(n,b):
    # dp over heights
    dp={0:1}
    for step in range(2*n):
        nd={}
        rem=2*n-step-1
        for h,v in dp.items():
            if h+1<=rem: nd[h+1]=nd.get(h+1,0)+v*b(h)
            if h>0: nd[h-1]=nd.get(h-1,0)+v
        dp=nd
    return dp.get(0,0)
def v2(x):
    assert x!=0
    c=0
    while x%2==0: x//=2;c+=1
    return c
s2=lambda n: bin(n).count('1')
for k in (1,2):
    b=lambda h:(2*h+1)**(2*k)
    d={}
    for n in range(2,41):
        C=wc(n,lambda h:1); assert C==comb(2*n,n)//(n+1)
        L=wc(n,b); d[n]=v2(L-C)-s2(n)
    print(k,[ (n,d[n]) for n in (2,3,4,19)], [d[n] for n in range(2,41)])
    # exhaustive: alpha mod 2^M, M large; xi(n-alpha)=m iff alpha ≡ n+2^m mod 2^{m+1}
    for N0 in (2,4):
        ok=[]
        for c in range(0,min(d.values())+1 if True else 0):
            # constraints alpha ≡ n+2^m (mod 2^{m+1}), m=d[n]-c >=0
            cons=[]; good=True
            for n in range(N0,41):
                m=d[n]-c
                if m<0: good=False;break
                cons.append(((n+(1<<m))%(1<<(m+1)),m+1))
            if not good: continue
            # compatibility: pairwise agree modulo min modulus
            for i in range(len(cons)):
                for j in range(i):
                    e=min(cons[i][1],cons[j][1])
                    if (cons[i][0]-cons[j][0])%(1<<e): good=False
            if good: ok.append(c)
        print(' k',k,'range n>=',N0,'to 40: feasible c:',ok)
# direct k=2 on n in {2,3,4,19}
