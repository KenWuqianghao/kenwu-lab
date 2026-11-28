/* Exhaustive branch and bound, version 2: lists all permutations pi of [n] with t(pi) >= T.
   t(pi) = sum_{m=3}^n C(n,m) + sum_{a<b<c} turn(a,b,c) * 2^a * 2^(n-1-c)   (positions 0-indexed)
   Pruning: loss so far + a lower bound on the loss of triples (a,b,c') with a,b placed and c' unplaced.
   For such a triple the loss is 2^a 2^(n-1-c') [v > pi_b] if pi_a < pi_b, and [v < pi_b] if pi_a > pi_b,
   where v = pi_c'. The bound assigns the remaining values to the remaining positions optimally,
   with each future position treated independently of the others (rearrangement inequality). */
int printf(const char*,...); int atoi(const char*); long long atoll(const char*);
typedef long long ll;
int N; ll ML[40]; /* ML[m] = exact minimum loss for length m, computed in order */
int n; ll T, base, Wtot, budget; int p[32]; int used[33]; ll Alo[32], Ahi[32];
ll cnt=0, best=-1, nodes=0;
static void rec(int c, ll loss){
  nodes++;
  if(c==n){ ll t=base+Wtot-loss; if(t>=T){ printf("t=%lld ",t); for(int i=0;i<n;i++) printf("%d%s",p[i],i<n-1?",":"\n"); cnt++; if(t>best)best=t;} return; }
  int vmax = (c==0 && n==N) ? (n+1)/2 : n; /* complement symmetry: pi_1 <= (n+1)/2 at the top level */
  for(int v=1;v<=vmax;v++) if(!used[v]){
    /* exact loss of triples (a,b,c) ending at the new position c */
    ll s=0; for(int b=1;b<c;b++){ if(p[b]<v) s+=Alo[b]; else s+=Ahi[b]; }  /* pi_b<v: turn fails iff pi_a<pi_b ; pi_b>v: fails iff pi_a>pi_b */
    ll L=loss+s*(1LL<<(n-1-c)); if(L>budget) continue;
    ll lo=0,hi=0; for(int a=0;a<c;a++){ if(p[a]<v) lo+=1LL<<a; else hi+=1LL<<a; }
    Alo[c]=lo; Ahi[c]=hi; p[c]=v; used[v]=1;
    /* lower bound for future positions c+1..n-1 */
    int m=0; ll F[32];
    for(int w=1;w<=n;w++) if(!used[w]){ ll f=0; for(int b=1;b<=c;b++){ if(p[b]<w) f+=Alo[b]; else f+=Ahi[b]; } F[m++]=f; }
    /* sort F ascending */
    for(int i=1;i<m;i++){ ll x=F[i]; int j=i-1; while(j>=0&&F[j]>x){F[j+1]=F[j];j--;} F[j+1]=x; }
    ll lb=0; for(int i=0;i<m;i++){ int cp=c+1+i; lb+=F[i]*(1LL<<(n-1-cp)); }
    lb += ML[m]*(1LL<<(n-m)); /* triples inside the unplaced suffix of length m */ /* largest coefficient (cp=c+1) gets smallest F */
    if(L+lb<=budget) rec(c+1,L);
    used[v]=0;
  }
}
static ll Tlist[]={0,0,0,2,11,37,106,270,653,1523,3480,7768,17123,37405,81350,174954,374409,798471,1700036,3596124,7588303,15970785,33596706,70310126,146867861};
int main(int argc,char**argv){ N=atoi(argv[1]);
  for(int i=0;i<40;i++) ML[i]=0;
  for(n=3;n<=N;n++){ T=Tlist[n]; cnt=0; best=-1; nodes=0;
  base=0; for(int m=3;m<=n;m++){ ll C=1; for(int i=0;i<m;i++) C=C*(n-i)/(i+1); base+=C; }
  Wtot=0; for(int a=0;a<n;a++) for(int c=a+2;c<n;c++) Wtot+=(1LL<<a)*(1LL<<(n-1-c))*(c-a-1);
  budget=base+Wtot-T; if(budget<0){printf("T above trivial bound\n");return 1;}
  printf("BEGIN n=%d\n",n);
  rec(0,0);
  printf("SUMMARY n=%d T=%lld found=%lld best=%lld nodes=%lld\n",n,T,cnt,best,nodes);
  if(cnt==0){printf("ERROR: threshold not reached\n");return 1;}
  ML[n]=base+Wtot-best; }
  return 0; }
