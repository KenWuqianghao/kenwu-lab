// Meet-in-the-middle search for ternary Legendre pairs among sequences constant on given orbits.
// Input (stdin): l norb, then norb lines "size j1 j2 ...". Composition fixed to (h-1,h,h), l=3h-1.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#define MAXL 128
int L, H, norb, osz[MAXL], orb[MAXL][MAXL], half;
typedef struct { uint64_t key; uint64_t code; } rec;
rec *R; size_t nR = 0, capR = 0;
int e[MAXL], val[MAXL];
static uint64_t mix(uint64_t x){x^=x>>33;x*=0xff51afd7ed558ccdULL;x^=x>>33;x*=0xc4ceb9fe1a85ec53ULL;x^=x>>33;return x;}
static void paf(const int *s, int *u, int *v){
  for(int t=1;t<=half;t++){int N[3]={0,0,0};for(int j=0;j<L;j++){int d=s[j]-s[(j+t)%L];if(d<0)d+=3;N[d]++;}u[t]=N[0]-N[2];v[t]=N[1]-N[2];}
}
static uint64_t hashv(const int *u,const int *v,int neg){
  uint64_t h=1469598103934665603ULL;
  for(int t=1;t<=half;t++){int a=neg?(-2-u[t]):u[t];int b=neg?(-v[t]):v[t];h=mix(h^(uint64_t)((a+512)*1024+(b+512)));}
  return h;
}
static void decode(uint64_t code,int *s){for(int i=0;i<norb;i++){int x=code%3;code/=3;for(int k=0;k<osz[i];k++)s[orb[i][k]]=x;}}
static void rec_assign(int i,int c0,int c1,int c2,uint64_t code,uint64_t mul){
  if(i==norb){ if(c0==H-1&&c1==H&&c2==H){ int s[MAXL],u[MAXL],v[MAXL];decode(code,s);paf(s,u,v);
      if(nR==capR){capR=capR?capR*2:1<<20;R=realloc(R,capR*sizeof(rec));if(!R){fprintf(stderr,"oom\n");exit(1);}}
      R[nR].key=hashv(u,v,0);R[nR].code=code;nR++;} return; }
  int sz=osz[i];
  if(c0+sz<=H-1) rec_assign(i+1,c0+sz,c1,c2,code,mul*3);
  if(c1+sz<=H) rec_assign(i+1,c0,c1+sz,c2,code+mul,mul*3);
  if(c2+sz<=H) rec_assign(i+1,c0,c1,c2+sz,code+2*mul,mul*3);
}
static int cmp(const void*a,const void*b){uint64_t x=((rec*)a)->key,y=((rec*)b)->key;return x<y?-1:x>y;}
int main(){
  if(scanf("%d %d",&L,&norb)!=2)return 1; H=(L+1)/3; half=L/2;
  for(int i=0;i<norb;i++){scanf("%d",&osz[i]);for(int k=0;k<osz[i];k++)scanf("%d",&orb[i][k]);}
  if(norb>40){fprintf(stderr,"too many orbits\n");return 1;}
  rec_assign(0,0,0,0,0,1);
  fprintf(stderr,"sequences: %zu\n",nR);
  qsort(R,nR,sizeof(rec),cmp);
  long found=0;
  for(size_t i=0;i<nR;i++){int s[MAXL],u[MAXL],v[MAXL];decode(R[i].code,s);paf(s,u,v);uint64_t tk=hashv(u,v,1);
    size_t lo=0,hi=nR;while(lo<hi){size_t m=(lo+hi)/2;if(R[m].key<tk)lo=m+1;else hi=m;}
    for(size_t k=lo;k<nR&&R[k].key==tk;k++){int s2[MAXL],u2[MAXL],v2[MAXL];decode(R[k].code,s2);paf(s2,u2,v2);
      int ok=1;for(int t=1;t<=half;t++)if(u[t]+u2[t]!=-2||v[t]+v2[t]!=0){ok=0;break;}
      if(ok){found++; if(found<=20){printf("A ");for(int j=0;j<L;j++)printf("%d",s[j]);printf(" B ");for(int j=0;j<L;j++)printf("%d",s2[j]);printf("\n");fflush(stdout);}}}
  }
  fprintf(stderr,"pairs found (ordered): %ld\n",found);
  return 0;
}
