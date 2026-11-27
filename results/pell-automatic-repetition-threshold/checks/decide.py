"""Independent decision procedure (no Walnut code or data) for:
   'the Pell-automatic word X has a factor of length n+m(n) with period n', n>=1,
   where mode 'square' means the factor X[i..i+2n-1] (matches for u in [i,i+n)),
   and mode 'short' means matches for u in [i,i+n-1) (length 2n-1; control).
Automata read msd-first greedy Pell representations, padded with leading zeros."""
import sys, itertools
from collections import deque
D3=(0,1,2)
def load(path):
    d=[];out=[]
    for l in open(path):
        t=l.split()
        if not t or t[0].startswith('msd'): continue
        if '->' in t: d[-1][int(t[0])]=int(t[2])
        else: assert int(t[0])==len(d); d.append([None]*3); out.append(int(t[1]))
    assert d[0][0]==0
    return d,out
# --- adder x+y=z: state (c1,c2) means pending value c1*alpha+c2 in Z[alpha], alpha^2=2alpha+1
def add_step(st,a,b,c,B1,B2):
    c1,c2=st; n=(2*c1+c2, c1+a+b-c)
    return n if abs(n[0])<=B1 and abs(n[1])<=B2 else None
def add_acc(st): return 2*st[0]+st[1]==0
def adder(B1,B2,target=0):
    # reachable + co-accessible states
    seen={(0,0)};dq=deque(seen);edges={}
    while dq:
        s=dq.popleft()
        for a,b,c in itertools.product(D3,repeat=3):
            n=add_step(s,a,b,c,B1,B2)
            if n is None: continue
            edges.setdefault(n,set()).add(s)
            if n not in seen: seen.add(n);dq.append(n)
    live={s for s in seen if 2*s[0]+s[1]==target};dq=deque(live)
    while dq:
        s=dq.popleft()
        for p in edges.get(s,()):
            if p not in live: live.add(p);dq.append(p)
    return live
LIVE=adder(10,45); assert LIVE==adder(20,90), "pruning bound active"
def ADD(st,a,b,c):
    c1,c2=st; n=(2*c1+c2, c1+a+b-c)
    return n if n in LIVE else None
def VAL(v,a):  # 0 ok, 1 = just read 2
    if v==1: return 0 if a==0 else None
    return 1 if a==2 else 0
def CMP(c,a,b):  # 0 equal so far, 1 less, 2 greater
    return c if c else (1 if a<b else 2 if a>b else 0)
def rep(n,L):
    P=[1,2]
    while len(P)<L: P.append(2*P[-1]+P[-2])
    r=[]
    for w in reversed(P[:L]): c=n//w; n-=c*w; r.append(c)
    assert n==0; return r
def selftest_adder():
    L=8
    for x in range(0,400,3):
        for y in range(0,400,7):
            for z in (x+y,x+y+1,max(0,x+y-1),x+y+5):
                st=(0,0)
                for a,b,c in zip(rep(x,L),rep(y,L),rep(z,L)):
                    st=ADD(st,a,b,c)
                    if st is None: break
                assert (st is not None and add_acc(st))==(z==x+y),(x,y,z)
class NFA:
    """Explicit NFA over kept letters, built from step(); hidden tracks are projected away.
    States not co-accessible are removed. Subsets are int bitsets."""
    def __init__(self, init, step, kept_letters, hidden_letters, acc):
        ids={init:0};sts=[init];succ=[];i=0
        while i<len(sts):
            s=sts[i];row=[]
            for k in kept_letters:
                m=0
                for h in hidden_letters:
                    n=step(s,k,h)
                    if n is None: continue
                    j=ids.get(n)
                    if j is None: j=ids[n]=len(sts);sts.append(n)
                    m|=1<<j
                row.append(m)
            succ.append(row);i+=1
        N=len(sts);pred=[[] for _ in range(N)]
        for i,row in enumerate(succ):
            m=0
            for x in row: m|=x
            while m:
                low=m&-m;pred[low.bit_length()-1].append(i);m^=low
        live=[acc(s) for s in sts];dq=deque(i for i in range(N) if live[i])
        self.accmask=sum(1<<i for i in range(N) if live[i])
        while dq:
            j=dq.popleft()
            for p in pred[j]:
                if not live[p]: live[p]=True;dq.append(p)
        lm=sum(1<<i for i in range(N) if live[i])
        self.succ=[[x&lm for x in row] for row in succ];self.K=kept_letters
        print("  nfa states",N,"co-accessible",bin(lm).count("1"),flush=True)
        zi=kept_letters.index(tuple(0 for _ in kept_letters[0]))
        self.cache={}
        S=1&lm
        while True:
            T=S|self.move(S,zi)
            if T==S: break
            S=T
        self.init=S
    def move(self,S,ki):
        key=(S,ki);T=self.cache.get(key)
        if T is not None: return T
        T=0;x=S;succ=self.succ
        while x:
            low=x&-x;T|=succ[low.bit_length()-1][ki];x^=low
        self.cache[key]=T;return T
    def accepts(self,S): return bool(S&self.accmask)
    def determinize(self):
        idx={self.init:0};states=[self.init];trans=[];dq=deque([self.init])
        while dq:
            S=dq.popleft();row=[]
            for ki in range(len(self.K)):
                T=self.move(S,ki)
                if T not in idx: idx[T]=len(states);states.append(T);dq.append(T)
                row.append(idx[T])
            trans.append(row)
        return states,trans,[self.accepts(S) for S in states]
def main(path,mode):
    d,out=load(path); selftest_adder()
    K2=list(itertools.product(D3,repeat=2))
    # M(u,n) = exists b: u+n=b, valid(b), X[u]!=X[b].  NFA state (add,qu,qb,vb)
    def stepM(s,k,h):
        ad,qu,qb,vb=s;u,n=k;b=h[0]
        ad=ADD(ad,u,n,b)
        if ad is None: return None
        vb=VAL(vb,b)
        if vb is None: return None
        return (ad,d[qu][u],d[qb][b],vb)
    accM=lambda s: add_acc(s[0]) and s[3]==0 and out[s[1]]!=out[s[2]]
    Ms,Mt,Ma=NFA(((0,0),0,0,0),stepM,K2,[(b,) for b in D3],accM).determinize()
    print("D_M states:",len(Ms),flush=True)
    kidx={k:i for i,k in enumerate(K2)}
    # bad(i,n) = exists u,s: i+n=s, valid(u), valid(s), i<=u, u<s (or u+1<s), M(u,n)
    # mode short: u < s-1, i.e. exists s1: handled by requiring u<s and (u+1)<s -> use e=s-1: i+n=e+1.
    # Implemented as: add(i,n,s) with z digit; for 'short' we use relation i+n = s+1 by starting the adder at pending -1.
    def stepB(s,k,h):
        ad,vu,vs,c1,c2,m=s;i,n=k;u,sd=h
        ad=ADD(ad,i,n,sd)
        if ad is None: return None
        vu=VAL(vu,u); vs=VAL(vs,sd)
        if vu is None or vs is None: return None
        c1=CMP(c1,i,u)
        if c1==2: return None
        c2=CMP(c2,u,sd)
        if c2==2: return None
        return (ad,vu,vs,c1,c2,Mt[m][kidx[(u,n)]])
    if mode=='square': fin=lambda ad: add_acc(ad)
    else: fin=lambda ad: 2*ad[0]+ad[1]==1   # i+n-s = 1, i.e. s = i+n-1
    accB=lambda s: fin(s[0]) and s[1]==0 and s[2]==0 and s[4]==1 and Ma[s[5]]
    global LIVE
    if mode!='square':
        # co-accessibility must be recomputed for the new acceptance: use the untrimmed bounded adder
        LIVE=adder(10,45,1); assert LIVE==adder(20,90,1)
    NB=NFA(((0,0),0,0,0,0,0),stepB,K2,list(itertools.product(D3,repeat=2)),accB)
    # lazy search over valid (i,n), n>=1, for a subset with bad false
    start=(NB.init,0,0,False); seen={start:None}; dq=deque([start]); wit=None
    while dq and wit is None:
        s=dq.popleft(); S,vi,vn,nz=s
        for ki,(i,n) in enumerate(K2):
            a=VAL(vi,i); c=VAL(vn,n)
            if a is None or c is None: continue
            t=(NB.move(S,ki),a,c,nz or n>0)
            if t not in seen:
                seen[t]=(s,(i,n)); dq.append(t)
                if len(seen)%20000==0: print("  ...top states",len(seen),file=sys.stderr,flush=True)
                if a==0 and c==0 and t[3] and not NB.accepts(t[0]): wit=t; break
    if wit is None: print("RESULT",mode,": no (i,n) with n>=1 and all matches. reachable top states:",len(seen))
    else:
        w=[];t=wit
        while seen[t] is not None: t,k=seen[t]; w.append(k)
        w.reverse(); P=[1,2]
        while len(P)<len(w): P.append(2*P[-1]+P[-2])
        iv=sum(k[0]*P[len(w)-1-j] for j,k in enumerate(w)); nv=sum(k[1]*P[len(w)-1-j] for j,k in enumerate(w))
        print("RESULT",mode,": FOUND i=%d n=%d"%(iv,nv))
main(sys.argv[1],sys.argv[2])
