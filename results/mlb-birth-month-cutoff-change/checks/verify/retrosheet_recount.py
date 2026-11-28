import csv, sys
from datetime import date
from scipy.stats import fisher_exact
rows=[]; mx="0"
for r in csv.DictReader(open(sys.argv[1], encoding="latin-1")):
    b, d, c = r["birthdate"], r["debut_p"], r["birthcountry"]
    if len(b)!=8 or len(d)!=8 or b[4:6]=="00" or b[6:]=="00": continue
    mx=max(mx,d)
    try: rows.append((c, date(int(b[:4]),int(b[4:6]),int(b[6:])), date(int(d[:4]),int(d[4:6]),int(d[6:]))))
    except ValueError: pass
print("players with dates", len(rows), "max debut", mx)
def addy(b,n):
    try: return b.replace(year=b.year+n)
    except ValueError: return date(b.year+n,3,1)
def sel(lo,hi,us=True): return [b for c,b,d in rows if (c=="USA")==us and lo<=b<=hi and d<addy(b,25)]
def ab(bs,A=(5,6,7),B=(8,9,10)): return sum(b.month in A for b in bs), sum(b.month in B for b in bs)
C=sel(date(1976,8,1),date(1992,7,31)); T=sel(date(1996,5,1),date(2001,4,30))
print("n_C",len(C),"n_T",len(T))
print("months C",[sum(b.month==m for b in C) for m in range(1,13)])
print("months T",[sum(b.month==m for b in T) for m in range(1,13)])
(ta,tb),(ca,cb)=ab(T),ab(C)
print("primary",ta,tb,ca,cb,fisher_exact([[ta,tb],[ca,cb]],alternative="greater"))
G=sel(date(1992,8,1),date(1995,7,31)); print("gap 1992-08..1995-07",ab(G))
# long history of ratio, all US-born debut<25, 8-year bins
for y in range(1900,1993,8):
    a,b=ab(sel(date(y,8,1),date(y+8,7,31))); print(f"born {y}-08..{y+8}-07 MJJ={a} ASO={b} ratio={b/a:.2f}")
