// DFS for projections pi: Sigma_9 -> Sigma_5 of class P_ret with marker '0':
// pi(i) = '0' x_i, x_i a 0-free palindrome, image pi(u_9) rich and with no
// repetition of exponent >= THR (THR slightly above E*(u_9)).
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;
typedef long long ll;
const int D=9;
vector<int> U; int NU;
string img; // image so far
// eertree with undo
struct Node{int len,link; int nxt[5];};
vector<Node> T; int last_;
struct Undo{int last; int created; int parent; int ch;};
vector<Undo> ust;
bool addRich(char cc){ // returns false if not rich (no new palindrome)
  int c=cc-'0'; int i=img.size()-1; // char already pushed to img
  int cur=last_;
  while(true){int L=T[cur].len; if(i-1-L>=0 && img[i-1-L]==cc) break; cur=T[cur].link;}
  if(T[cur].nxt[c]!=-1){ return false; }
  Node nd; nd.len=T[cur].len+2; for(int k=0;k<5;k++)nd.nxt[k]=-1;
  if(nd.len==1) nd.link=1; else {int q=T[cur].link; while(true){int L=T[q].len; if(i-1-L>=0&&img[i-1-L]==cc)break; q=T[q].link;} nd.link=T[q].nxt[c];}
  T.push_back(nd); T[cur].nxt[c]=T.size()-1; ust.push_back({last_,1,cur,c}); last_=T.size()-1; return true;
}
void undoRich(){Undo u=ust.back(); ust.pop_back(); T[u.parent].nxt[u.ch]=-1; T.pop_back(); last_=u.last;}
ll NUM=2059285449LL, DEN=1000000000LL; // threshold; forbid len/p >= NUM/DEN
bool suffixRep(){ int n=img.size();
  for(int p=1; (ll)n*DEN>= (ll)p*NUM; p++){ int i=0; while(img[n-1-i]==img[n-1-i-p]){ if((ll)(i+1+p)*DEN>=(ll)p*NUM) return true; i++; if(i+p>=n)break;} }
  return false;}
bool push(char c){ img.push_back(c); if(!addRich(c)){img.pop_back(); return false;} if(suffixRep()){undoRich(); img.pop_back(); return false;} return true;}
void pop(){undoRich(); img.pop_back();}
string blk[D]; bool known[D]; int maxLetter=0; int MAXB=60; long long sols=0, nodes=0, NODECAP=20000000; int target;
int hcheck(int k){ // check length relation once block k known
  auto h=[&](int i){return (int)blk[i].size();};
  if(k==5) return h(5)==h(0)+h(4);
  if(k==6) return h(6)==h(1)-h(4)+2*h(5);
  if(k==7) return h(7)==h(2)-h(4)+2*h(6);
  if(k==8) return h(8)==h(3)-h(4)+2*h(7);
  return 1;}
int H0[5]; bool fixH=false;
int needLen(int k){ auto h=[&](int i){return (int)blk[i].size();}; if(fixH && k<5) return H0[k];
  if(k==5) return h(0)+h(4); if(k==6) return h(1)-h(4)+2*h(5); if(k==7) return h(2)-h(4)+2*h(6); if(k==8) return h(3)-h(4)+2*h(7); return -1;}
bool useH=true;
void dfs(int pos);
bool ispal(const string&x){int L=x.size();for(int i=0;i<L/2;i++)if(x[i]!=x[L-1-i])return false;return true;}
void genBlock(int letter,int pos,string&cur,int ml){
  nodes++; if(nodes>NODECAP){fprintf(stderr,"CAP\n"); exit(3);}
  int L=cur.size(); int need = useH? needLen(letter): -1;
  if(need>=0 && L>need) return;
  // try closing
  if(L>=1 && (need<0||L==need) && ispal(cur.substr(1))){ bool dup=false; for(int j=0;j<D;j++) if(known[j]&&blk[j]==cur) dup=true;
    if(!dup){ blk[letter]=cur; known[letter]=true; int sv=maxLetter; maxLetter=ml; dfs(pos+1); maxLetter=sv; known[letter]=false; blk[letter]=""; } }
  if(L>=MAXB) return;
  // extend
  int x=L-1; // index in x of next char
  // palindrome forcing only known when final length known
  for(int c=1;c<=min(4,ml+1);c++){
    if(need>=0){ int xl=need-1; int j=x; if(j>=xl/2+ (xl%2) ){ /* mirrored */ int mj=xl-1-j; if(cur[1+mj]-'0'!=c) continue; } }
    if(!push('0'+c)) continue; cur.push_back('0'+c);
    genBlock(letter,pos,cur,max(ml,c)); cur.pop_back(); pop(); }
}
void dfs(int pos){
  if(pos==target){ sols++; printf("SOL"); for(int i=0;i<D;i++)printf(" %s",blk[i].c_str()); printf("\n"); fflush(stdout); return; }
  int a=U[pos];
  if(known[a]){ int k=0; bool ok=true; for(char c:blk[a]){ if(!push(c)){ok=false;break;} k++; } if(ok) dfs(pos+1); for(int j=0;j<k;j++)pop(); return; }
  string cur="0"; if(!push('0')) return; genBlock(a,pos,cur,maxLetter); pop();
}
int main(int argc,char**argv){ target=atoi(argv[1]); MAXB=atoi(argv[2]); if(argc>3) useH=atoi(argv[3]); if(argc>8){fixH=true; for(int i=0;i<5;i++)H0[i]=atoi(argv[4+i]);}
  vector<int> w={0}; while((int)w.size()<target+10){ vector<int> nw; for(int c:w){ if(c<D-1){nw.push_back(0);nw.push_back(c+1);} else {nw.push_back(0);nw.push_back(D-1);nw.push_back(D-1);} } w=nw; }
  U=w; T.clear(); Node r0; r0.len=-1; r0.link=0; Node r1; r1.len=0; r1.link=0; for(int k=0;k<5;k++){r0.nxt[k]=r1.nxt[k]=-1;} T.push_back(r0); T.push_back(r1); last_=1;
  dfs(0); fprintf(stderr,"sols=%lld nodes=%lld\n",sols,nodes); }
