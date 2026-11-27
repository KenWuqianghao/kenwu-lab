import sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from explore_lib import wcat, v2, s2
def check(d, n0, N):
    """d: dict n->int or None. Return list of (parity, c, ok, first_bad) for both alpha parities."""
    out=[]
    for p in (0,1):
        other=[d[n] for n in range(n0,N+1) if n%2!=p]
        if any(x is None for x in other) or len(set(other))!=1:
            out.append((p,None,False,'opposite-parity d not constant')); continue
        c=other[0]
        cons=[]  # (modexp, residue)
        bad=None
        for n in range(n0,N+1):
            if n%2!=p: continue
            if d[n] is None: bad=(n,'zero diff'); break
            e=d[n]-c
            if e<1: bad=(n,'e<1'); break
            cons.append((e+1,(n+2**e)%2**(e+1),n))
            M,r,_=max(cons)
            for (m,rr,nn) in cons:
                if r%2**m!=rr: bad=(n,'conflict with n=%d'%nn); break
            if bad: break
        out.append((p,c,bad is None,bad))
    return out
if __name__=='__main__':
    N=int(sys.argv[1]); K=int(sys.argv[2])
    C=wcat(lambda h:1,N)
    for k in range(1,K+1):
        L=wcat(lambda h,k=k:(2*h+1)**(2*k),N)
        d={n:(None if L[n]==C[n] else v2(L[n]-C[n])-s2(n)) for n in range(2,N+1)}
        res2=check(d,2,N)
        # smallest n0 that makes it consistent
        n0ok=None
        for n0 in range(2,40):
            if any(r[2] for r in check(d,n0,N)): n0ok=n0; break
        print(k,'n0=2:',[r for r in res2],' minimal consistent n0:',n0ok)
