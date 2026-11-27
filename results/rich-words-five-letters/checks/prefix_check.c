/* Definitions-only test on a prefix of z = pi(u_9): richness (eertree) and the largest
   exponent of any repetition with exponent >= 2 inside the prefix (all periods). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const char *PHI[9]={"01","02","03","04","05","06","07","08","088"};
int main(int argc,char**argv){
  const char *PI[9]; for(int i=0;i<9;i++) PI[i]=argv[1+i];
  long NU=atol(argv[10]);
  char *u=malloc(NU+8), *v=malloc(NU+8); long n=1; u[0]=0;
  while(n<NU){ long m=0; for(long i=0;i<n&&m<NU;i++){ for(const char*p=PHI[(int)u[i]];*p&&m<NU;p++) v[m++]=*p-'0'; } char*t=u;u=v;v=t; if(m==n)break; n=m; }
  long N=0; for(long i=0;i<n;i++) N+=strlen(PI[(int)u[i]]);
  char *z=malloc(N+1); long k=0; for(long i=0;i<n;i++) for(const char*p=PI[(int)u[i]];*p;p++) z[k++]=*p-'0';
  printf("u prefix %ld letters, z prefix %ld letters\n",n,N);
  /* eertree */
  int (*to)[5]=calloc(N+3,sizeof(int[5])); int *len=malloc((N+3)*sizeof(int)), *link=malloc((N+3)*sizeof(int));
  len[0]=-1; link[0]=0; len[1]=0; link[1]=0; int cnt=2,last=1; long fail=-1;
  for(long i=0;i<N;i++){ int c=z[i]; int cur=last;
    while(!(i-len[cur]-1>=0 && z[i-len[cur]-1]==c)) cur=link[cur];
    if(to[cur][c]){ last=to[cur][c]; if(fail<0) fail=i; continue; }
    int nw=cnt++; len[nw]=len[cur]+2;
    if(len[nw]==1) link[nw]=1; else { int x=link[cur]; while(!(i-len[x]-1>=0 && z[i-len[x]-1]==c)) x=link[x]; link[nw]=to[x][c]; }
    to[cur][c]=nw; last=nw; }
  printf("distinct nonempty palindromes %d, length %ld, rich prefix: %s (first failure index %ld)\n",cnt-2,N,(cnt-2==N)?"YES":"NO",fail);
  /* repetitions: for each period p and checkpoint i=kp, extend the match z[j]==z[j+p] */
  long bestL=0,bestp=1; long cntabove=0;
  /* per dyadic band of p keep the best */
  long bL[64],bp[64]; for(int b=0;b<64;b++){bL[b]=0;bp[b]=1;}
  for(long p=1;2*p<=N;p++){ int band=0; while((1L<<(band+1))<=p) band++;
    for(long i=0;i+p<N;i+=p){ if(z[i]!=z[i+p]) continue;
      long f=i; while(f+p<N && z[f]==z[f+p]) f++;      /* matches on [b0,f) */
      long b0=i; while(b0>0 && z[b0-1]==z[b0-1+p]) b0--;
      long L=f-b0+p;                                   /* repetition z[b0, f+p) with period p */
      if(L>=2*p){ if(f+p>=N) continue;                 /* cut by the end of the prefix: skip */
        if((__int128)L*bestp>(__int128)bestL*p){bestL=L;bestp=p;}
        if((__int128)L*bp[band]>(__int128)bL[band]*p){bL[band]=L;bp[band]=p;} }
      long nx=((f)/p)*p; if(nx>i) i=nx-p+p>i? nx : i; } }
  printf("largest exponent in prefix: %ld/%ld = %.10f\n",bestL,bestp,(double)bestL/bestp);
  for(int b=0;b<64;b++) if(bL[b]) printf("band p in [2^%d,2^%d): best %ld/%ld = %.10f\n",b,b+1,bL[b],bp[b],(double)bL[b]/bp[b]);
  return 0; }
