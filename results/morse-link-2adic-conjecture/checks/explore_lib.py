import sys
def wcat(b, N):
    # C_n^b via Dyck path DP: f[h] = weighted count of prefixes ending at height h
    res=[1]
    f={0:1}
    # step through 2N steps
    rows=[ [0]*(N+2) for _ in range(1)]
    cur=[0]*(N+2); cur[0]=1
    out=[1]
    for step in range(1,2*N+1):
        nxt=[0]*(N+2)
        for h in range(N+1):
            v=cur[h]
            if v==0: continue
            if h+1<=N: nxt[h+1]+=v*b(h)   # up step at height h
            if h>0: nxt[h-1]+=v
        cur=nxt
        if step%2==0: out.append(cur[0])
    return out
def v2(x):
    if x==0: return None
    c=0
    while x%2==0: x//=2; c+=1
    return c
def s2(n): return bin(n).count('1')
