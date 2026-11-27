"""Check by brute force: nu2(N) == -sigma1(N)/2 (mod 4) for N = 8n+6, where nu2(N)
counts partitions of N with exactly two distinct part sizes (counted directly)."""
import sys
L=int(sys.argv[1]) if len(sys.argv)>1 else 3000
s1=[0]*(L+1)
for i in range(1,L+1):
    for j in range(i,L+1,i): s1[j]+=i
def nu2(N):  # #{(x>y>=1, i,j>=1): i*x + j*y = N}
    c=0
    for x in range(2,N):
        for i in range(1,(N-1)//x+1):
            r=N-i*x  # r = j*y with 1<=y<x
            c+=sum(1 for y in range(1,min(x,r+1)) if r%y==0)
    return c
bad=0
for N in range(6,L+1,8):
    if (nu2(N)+s1[N]//2)%4: bad+=1; print("FAIL",N)
print("checked N=8n+6 <=",L,"failures:",bad)
