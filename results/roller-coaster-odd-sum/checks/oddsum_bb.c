/* oddsum_bb.c: exact exhaustive search, integer arithmetic only.
   Lists every permutation pi of [n] with t(pi) >= T, optionally only those with the Odd Sum property
   (n odd: pi_j + pi_{n+1-j} odd for 1 <= j <= (n-1)/2).

   Usage: oddsum_bb n T mode [job K split_depth]
     mode 0: all permutations; mode 1: Odd Sum permutations only (n odd).
     job/K/split_depth: run only the subtrees at depth split_depth whose index (in DFS order) is
     congruent to job mod K. The union over job = 0..K-1 is the full search.

   Identity (positions 0-indexed):
     t(pi) = sum_{m=3}^n C(n,m) + sum_{a<b<c} turn(a,b,c) 2^a 2^(n-1-c),
     turn(a,b,c) = 1 iff pi_b > max(pi_a,pi_c) or pi_b < min(pi_a,pi_c).
   loss(pi) = sum_{a<b<c} (1-turn(a,b,c)) 2^a 2^(n-1-c);  t = base + Wtot - loss.
   We need loss <= budget = base + Wtot - T.

   Lower bound on the final loss at a node with positions 0..c placed (sum of four parts over disjoint
   sets of triples; every triple loss is >= 0):
     (1) triples with a,b,c all placed: exact (the running value `loss`);
     (2) triples (a,b,q) with a,b placed, q unplaced, value w at q: loss F(w) 2^(n-1-q), where
         F(w) = sum_b (Alo[b] if pi_b < w else Ahi[b]);
     (4) triples (a,q,r) with a placed, q < r unplaced, value w at q: the loss is 2^a 2^(n-1-r) if pi_a < w < pi_r
         or pi_a > w > pi_r, so the sum over a and r is >= g(w) (2^(n-1-q) - 1), where
         g(w) = min(lo(w), hi(w)), lo(w) = sum_{a placed, pi_a < w} 2^a, hi(w) = sum_{a placed, pi_a > w} 2^a;
       so (2)+(4) >= sum over unplaced q of (F+g)(w_q) 2^(n-1-q) - sum_w g(w), and the minimum over all
       assignments of the unplaced values to the unplaced positions is attained (rearrangement inequality)
       by pairing the smallest F+g with the largest weight. In mode 1, when every unplaced position has a
       forced parity (its mirror is placed, or it is the middle, which must be odd), the assignment must
       respect parity, and the pairing is done in each parity class separately; otherwise parity is ignored
       (a relaxation);
     (3) triples inside the unplaced suffix of length m: >= ML[m] * 2^(n-m), where ML[m] is a lower
         bound on the minimum loss over S_m.
   ML[m] is exact (computed by this program with mode 0) for m <= MLEXACT, and ML[m] = 2 ML[m-1] above,
   which is valid because deleting the last position of a permutation of length m keeps every triple
   among the first m-1 positions, each with weight 2 times its weight in length m-1.

   Symmetry: complement pi -> n+1-pi preserves t and the Odd Sum property, so pi_1 <= (n+1)/2 at the
   top level of the main run (orbits with pi_1 = (n+1)/2 are searched in full). */
int printf(const char*,...); int atoi(const char*); long long atoll(const char*); int fflush(void*);
extern void* stdout;
typedef long long ll;
static ll ML[40];
static int n, mode, sym, job=0, K=1, SD=-1; static ll T, base, Wtot, budget;
static int p[32], used[33]; static ll Alo[32], Ahi[32];
static ll cnt, best, nodes, splitidx;

static void sortll(ll*F,int m){ for(int i=1;i<m;i++){ ll x=F[i]; int j=i-1; while(j>=0&&F[j]>x){F[j+1]=F[j];j--;} F[j+1]=x; } }
static void rec(int c, ll loss){
  nodes++;
  if(c==n){ ll t=base+Wtot-loss; if(t>=T){ printf("t=%lld ",t); for(int i=0;i<n;i++) printf("%d%s",p[i],i<n-1?",":"\n"); cnt++; if(t>best)best=t;} return; }
  if(c==SD){ ll k=splitidx++; if(k%K!=job) return; }
  int vmax = (c==0 && sym) ? (n+1)/2 : n;
  int par = -1; /* required parity of the value at position c, -1 = free */
  if(mode==1){ int mirror=n-1-c; if(mirror<c) par = 1 - (p[mirror]&1); else if(mirror==c) par = 1; }
  for(int v=1;v<=vmax;v++) if(!used[v]){
    if(par>=0 && (v&1)!=par) continue;
    ll s=0; for(int b=1;b<c;b++){ if(p[b]<v) s+=Alo[b]; else s+=Ahi[b]; }
    ll L=loss+s*(1LL<<(n-1-c)); if(L>budget) continue;
    ll lo=0,hi=0; for(int a=0;a<c;a++){ if(p[a]<v) lo+=1LL<<a; else hi+=1LL<<a; }
    Alo[c]=lo; Ahi[c]=hi; p[c]=v; used[v]=1;
    /* per unplaced value w: cost F(w)+g(w) per unit of position weight 2^(n-1-cp), minus g(w);
       parity classes are matched separately when every unplaced position has a forced parity */
    int m=0, mo=0, me=0; ll Fo[32], Fe[32], G=0;
    for(int w=1;w<=n;w++) if(!used[w]){
      ll f=0; for(int b=1;b<=c;b++){ if(p[b]<w) f+=Alo[b]; else f+=Ahi[b]; }
      ll lo=0; for(int a=0;a<=c;a++) if(p[a]<w) lo+=1LL<<a;
      ll hi=((1LL<<(c+1))-1)-lo; ll g=lo<hi?lo:hi;
      G+=g; m++; if(w&1) Fo[mo++]=f+g; else Fe[me++]=f+g; }
    ll lb=-G;
    int forced = (mode==1 && c+1 >= n-1-(c+1)); /* every position cp >= c+1 has its mirror placed or is the middle */
    if(forced){
      int po[32], pe[32], npo=0, npe=0;
      for(int cp=c+1;cp<n;cp++){ int mir=n-1-cp; int want = (mir==cp) ? 1 : 1-(p[mir]&1); if(want) po[npo++]=cp; else pe[npe++]=cp; }
      if(npo!=mo || npe!=me){ used[v]=0; continue; } /* parity counts cannot match: no completion */
      sortll(Fo,mo); sortll(Fe,me);
      for(int i=0;i<mo;i++) lb+=Fo[i]*(1LL<<(n-1-po[i]));   /* po ascending = weights descending */
      for(int i=0;i<me;i++) lb+=Fe[i]*(1LL<<(n-1-pe[i]));
    } else {
      ll F[32]; int k=0; for(int i=0;i<mo;i++) F[k++]=Fo[i]; for(int i=0;i<me;i++) F[k++]=Fe[i];
      sortll(F,m);
      for(int i=0;i<m;i++){ int cp=c+1+i; lb+=F[i]*(1LL<<(n-1-cp)); }
    }
    lb += ML[m]*(1LL<<(n-m));
    if(L+lb<=budget) rec(c+1,L);
    used[v]=0;
  }
}
static void setup(int nn, ll TT){
  n=nn; T=TT; cnt=0; best=-1; nodes=0; splitidx=0;
  base=0; for(int m=3;m<=n;m++){ ll C=1; for(int i=0;i<m;i++) C=C*(n-i)/(i+1); base+=C; }
  Wtot=0; for(int a=0;a<n;a++) for(int c=a+2;c<n;c++) Wtot+=(1LL<<a)*(1LL<<(n-1-c))*(c-a-1);
  budget=base+Wtot-T;
  for(int i=0;i<=n;i++) used[i]=0;
}
/* Lower bounds for tmax(m), m <= MLEXACT: the values of Ahmed-Snevily, Table 1. Each one is only used
   as a search threshold: the search is exhaustive above it, so it returns the exact maximum provided
   that some permutation reaches the threshold (checked: found > 0). */
#define MLEXACT 12
static ll Tlist[]={0,0,0,2,11,37,106,270,653,1523,3480,7768,17123};
int main(int argc,char**argv){
  int N=atoi(argv[1]); ll TT=atoll(argv[2]); int md=atoi(argv[3]);
  if(argc>=7){ job=atoi(argv[4]); K=atoi(argv[5]); SD=atoi(argv[6]); }
  for(int i=0;i<40;i++) ML[i]=0;
  int top = N-1 < MLEXACT ? N-1 : MLEXACT;
  int sj=job,sK=K,sSD=SD; job=0;K=1;SD=-1;
  for(int m=3;m<=top;m++){ setup(m,Tlist[m]); mode=0; sym=1; rec(0,0);
    if(cnt==0){ printf("ERROR: ML threshold not reached at m=%d\n",m); return 1; }
    ML[m]=base+Wtot-best; printf("ML[%d]=%lld (tmax=%lld, exact)\n",m,ML[m],best); }
  for(int m=top+1;m<40;m++) ML[m]=2*ML[m-1];
  job=sj;K=sK;SD=sSD;
  setup(N,TT); mode=md; sym=1;
  if(budget<0){ printf("T above trivial bound\n"); return 1; }
  printf("BEGIN n=%d T=%lld mode=%d job=%d K=%d split_depth=%d budget=%lld\n",n,T,mode,job,K,SD,budget); fflush(stdout);
  rec(0,0);
  printf("SUMMARY n=%d T=%lld mode=%d job=%d K=%d found=%lld best=%lld nodes=%lld splitnodes=%lld\n",n,T,mode,job,K,cnt,best,nodes,splitidx);
  return 0;
}
