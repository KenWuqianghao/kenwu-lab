// Backtracking search: DFAO over msd Pell digits {0,1,2} (Pell numbers 1,2,5,12,...),
// output alphabet {0..K-1}, delta(q0,0)=q0, output prefix of length N with no square.
// Usage: java -Xss512m Sqf N S K   (S = maximum number of states). The paper uses N=3000, S=4, K=4.
public class Sqf {
  static int N,S,K,best=0; static int[][] rep; static int[][] delta=new int[64][3]; static int[] out=new int[64]; static int ns; static int[] x;
  static boolean okAt(int n){
    for(int p=1;p<=n;p++){ int L=2*p; if(L>n+1) break; boolean g=true;
      for(int j=n-L+1+p;j<=n;j++) if(x[j]!=x[j-p]){g=false;break;} if(g) return false; }
    return true; }
  static void report(int n){ System.out.println("REACHED "+n+" states="+ns);
    for(int q=0;q<ns;q++) System.out.println("q"+q+" out="+out[q]+" : "+delta[q][0]+" "+delta[q][1]+" "+delta[q][2]); System.out.flush(); }
  static boolean walk(int n,int k,int q){
    if(k==rep[n].length){ x[n]=out[q]; if(!okAt(n)) return false;
      if(n+1>best){best=n+1; if(best%100==0) {System.err.println("best "+best); report(best);} if(best==N) {report(N); return true;}}
      return walk(n+1,0,0); }
    int d=rep[n][k];
    if(delta[q][d]>=0) return walk(n,k+1,delta[q][d]);
    for(int t=0;t<ns;t++){ delta[q][d]=t; if(walk(n,k+1,t)) return true; }
    if(ns<S){ int t=ns++; delta[t][0]=delta[t][1]=delta[t][2]=-1; delta[q][d]=t;
      for(int o=0;o<K;o++){ out[t]=o; if(walk(n,k+1,t)) return true; } ns--; }
    delta[q][d]=-1; return false; }
  public static void main(String[] a){
    N=Integer.parseInt(a[0]); S=Integer.parseInt(a[1]); K=Integer.parseInt(a[2]); x=new int[N]; rep=new int[N][];
    long[] P=new long[60]; P[0]=1;P[1]=2; for(int i=2;i<60;i++)P[i]=2*P[i-1]+P[i-2];
    for(int n=0;n<N;n++){ if(n==0){rep[0]=new int[0];continue;} int i=0; while(P[i+1]<=n) i++;
      int[] dg=new int[i+1]; long m=n; for(int j=i;j>=0;j--){ dg[i-j]=(int)(m/P[j]); m-=dg[i-j]*P[j]; } rep[n]=dg; }
    for(int[] r:delta) java.util.Arrays.fill(r,-1); ns=1; delta[0][0]=0;
    for(int o=0;o<K;o++){ out[0]=o; if(walk(0,0,0)){System.out.println("FOUND");return;} }
    System.out.println("NONE best="+best); } }
