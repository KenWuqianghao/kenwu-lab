"""Independent verifier parser. Args: raw_dir lahman_dir"""
import sys, zipfile, io, csv, re, json
from collections import defaultdict
from scipy.stats import binomtest, fisher_exact
raw, lah = sys.argv[1], sys.argv[2]
def cls(ev):
    """return None or (ab,hit,bb) using regex on the basic play"""
    basic = ev.split('.')[0]
    head = basic.split('/')[0]
    mods = basic.split('/')[1:]
    first = head.split('+')[0]
    if re.match(r'^(NP|BK|CS|DI|OA|PB|WP|PO|POCS|SB|FLE)', first): return None
    if re.match(r'^(IW|I|W)(?![A-Z])', first): return (0,0,1)
    if first.startswith('HP'): return (0,0,0)
    if re.match(r'^C(/|$)', basic) or first=='C': return (0,0,0)
    if any(m.startswith('SH') or m.startswith('SF') for m in mods): return (0,0,0)
    if re.match(r'^(S\d*$|S\d|S$|D\d|D$|DGR|T\d|T$|HR|H\d|H$)', first) or re.match(r'^[SDT]$',first): return (1,1,0)
    if re.match(r'^(K|\d|E\d|FC)', first): return (1,0,0)
    raise ValueError(ev)
FIX=len(sys.argv)>4; fixes=[]; lastnp=None
def old_ok(lastnp,slot,side,bo,pid): return bo!='0' and lastnp[0]!=pid
pas=defaultdict(list)   # (y,b) -> [(key, seq, team, ab,h,bb, kind)]
names={}
tg=defaultdict(set)
unk=defaultdict(int)
for y in range(2009,2026):
    z=zipfile.ZipFile(f'{raw}/{y}eve.zip')
    for n in sorted(z.namelist()):
        if n.endswith('.ROS'):
            for r in csv.reader(io.TextIOWrapper(z.open(n),encoding='latin-1')):
                names[r[0]]=r[2]+' '+r[1]
        if not n.endswith(('.EVA','.EVN')): continue
        gid=None; seq=0; slot={}; pend=None
        for r in csv.reader(io.TextIOWrapper(z.open(n),encoding='latin-1')):
            seq+=1
            if r[0]=='id': gid=r[1]; slot={}; teams={}
            elif r[0]=='info' and r[1] in('visteam','hometeam'): teams['0' if r[1]=='visteam' else '1']=r[2]
            elif r[0] in('start','sub'):
                pid,side,bo,fp=r[1],r[3],r[4],r[5]
                key=(gid[3:11],gid[11],gid)
                if r[0]=='sub' and fp=='11' and (side,bo) in slot and bo!='0':
                    old=slot[(side,bo)]
                    pas[(y,old)].append((key,seq,teams[side],0,0,0,'SUB'))
                if bo!='0': slot[(side,bo)]=pid
                if r[0]=='sub' and lastnp and lastnp[1]==side and old_ok(lastnp, slot, side, bo, pid): pend=(lastnp[0],pid)
            elif r[0]=='play':
                key=(gid[3:11],gid[11],gid)
                tg[(y,teams[r[2]])].add(key)
                if r[6]=='NP' and len(r[4])==2 and r[4][1]=='2': lastnp=(r[3],r[2],r[1])
                elif r[6]!='NP': lastnp=None
                bat=r[3]
                if FIX and pend and pend[1]==r[3] and r[6]!='NP':
                    if r[6].startswith('K'): bat=pend[0]; fixes.append((gid,pend[0],r[3],r[6]))
                    pend=None
                try: c=cls(r[6])
                except ValueError: unk[r[6].split('/')[0][:3]]+=1; c=(1,0,0)
                if c: pas[(y,bat)].append((key,seq,teams[r[2]])+c+('PA',))
print('unknown event heads',dict(unk)); print('midPA K reassignments',len(fixes),fixes[:6])
for k in pas: pas[k].sort(key=lambda t:(t[0],t[1]))
real={k:[t for t in v if t[6]=='PA'] for k,v in pas.items()}
tot={k:(sum(t[4] for t in v),sum(t[3] for t in v)) for k,v in real.items()}
# Lahman validation
retro={}
for r in csv.DictReader(open(f'{lah}/People.csv',encoding='latin-1')): retro[r['playerID']]=r['retroID']
L=defaultdict(lambda:[0,0])
for r in csv.DictReader(open(f'{lah}/Batting.csv')):
    y=int(r['yearID'])
    if y>=2009:
        k=(y,retro.get(r['playerID'])); L[k][0]+=int(r['H'] or 0); L[k][1]+=int(r['AB'] or 0)
ly=sorted({k[0] for k in L}); print('lahman years',ly[0],ly[-1])
from collections import Counter
mlbdir=sys.argv[3]; mm=0
for y in range(2009,2026):
    best={}
    for sp in json.load(open(f'{mlbdir}/{y}.json'))['stats'][0]['splits']:
        pid=sp['player']['id']; st=(sp['stat']['hits'],sp['stat']['atBats'])
        if pid not in best or st[1]>best[pid][1]: best[pid]=st
    c1=Counter(v for v in best.values() if v[1]>=200); c2=Counter(v for k,v in tot.items() if k[0]==y and v[1]>=200)
    if c1!=c2: mm+=1; print('MLB multiset mismatch',y,'api-only',dict(c1-c2),'retro-only',dict(c2-c1))
    else: print('MLB multiset match',y,sum(c1.values()))

n=bad=0; badl=[]; y_ok=lambda k:True
for k,(h,ab) in L.items():
    if y_ok(k) and (ab>=200 or tot.get(k,(0,0))[1]>=200):
        n+=1
        if tot.get(k)!=(h,ab): bad+=1; badl.append((k,tot.get(k),(h,ab)))
print('lahman check: batter-seasons with AB>=200:',n,'mismatch:',bad,badl[:15])
disp=lambda h,ab:(2000*h+ab)//(2*ab) if ab else None
elig=[k for k,(h,ab) in tot.items() if ab>=200]
print('eligible',len(elig))
fin=defaultdict(int)
for k in elig: fin[disp(*tot[k])]+=1
print('fin 295..305',[(d,fin[d]) for d in range(295,306)])
print('T1 p',binomtest(fin[300],fin[300]+fin[299],0.5,alternative='greater').pvalue, 'CI',binomtest(fin[300],fin[300]+fin[299]).proportion_ci())
ci=binomtest(fin[300],fin[300]+fin[299]).proportion_ci(); print('ratio CI',ci.low/(1-ci.low),ci.high/(1-ci.high))
# paper's .298/.299 vs .300/.301 season-end
a=fin[298]+fin[299]; b=fin[300]+fin[301]; print('end 298/299',a,'300/301',b,'binom p',binomtest(b,a+b,0.5,alternative='greater').pvalue)
# exploratory: all adjacent ratios fin[d]/fin[d-1] for d in 250..340 with fin[d-1]>=10
rat=sorted(((fin[d]/fin[d-1],d,fin[d],fin[d-1]) for d in range(240,341) if fin[d-1]>=15),reverse=True)[:5]; print('top adjacent ratios (den>=15)',rat)
# pairwise binomial p for each d in 250..330
ps=sorted((binomtest(fin[d],fin[d]+fin[d-1],0.5,alternative='greater').pvalue,d,fin[d],fin[d-1]) for d in range(200,351) if fin[d]+fin[d-1]>0)[:5]; print('smallest adjacent-pair p over .200-.350',ps)
# last actual PA (solver def) and last scheduled PA (paper def: incl. pinch-hit substitution)
def groups(seqs, label):
    G=defaultdict(lambda:[0,0,0,0,0]) # n, AB, H, BB, SUB
    who=defaultdict(list)
    for k in elig:
        rows=seqs[k]; last=rows[-1]
        h=sum(t[4] for t in rows[:-1]); ab=sum(t[3] for t in rows[:-1])
        d=disp(h,ab); g=G[d]; g[0]+=1; g[1]+=last[3]; g[2]+=last[4]; g[3]+=last[5]; g[4]+=last[6]=='SUB'
        if d==299: who[(last[5],last[6])].append((k,names.get(k[1]),last[0][2]))
    def agg(ds): return [sum(G[d][i] for d in ds) for i in range(5)]
    print('==',label)
    for nm,ds in [('299',[299]),('300',[300]),('298/299',[298,299]),('300/301',[300,301]),('280-320 excl 299',[d for d in range(280,321) if d!=299]),('280-320 excl 299,300',[d for d in range(280,321) if d not in(299,300)])]:
        g=agg(ds); print(f' {nm}: n={g[0]} AB={g[1]} H={g[2]} BB={g[3]} SUB={g[4]}  hit/n={g[2]/g[0]:.3f} bb/n={g[3]/g[0]:.3f} sub/n={g[4]/g[0]:.3f} H/AB={g[2]/max(g[1],1):.3f}')
    a,b=agg([298,299]),agg([300,301])
    print(' hits 298/299 vs 300/301 per n, fisher greater p=',fisher_exact([[a[2],a[0]-a[2]],[b[2],b[0]-b[2]]],alternative='greater')[1])
    print(' walks 298/299 vs 300/301 per n, fisher less p=',fisher_exact([[a[3],a[0]-a[3]],[b[3],b[0]-b[3]]],alternative='less')[1])
    print(' subs 298/299 vs 300/301, fisher less p=',fisher_exact([[a[4],a[0]-a[4]],[b[4],b[0]-b[4]]],alternative='less')[1])
    a,b=agg([299]),agg([d for d in range(280,321) if d!=299])
    print(' hits 299 vs others per n, fisher greater p=',fisher_exact([[a[2],a[0]-a[2]],[b[2],b[0]-b[2]]],alternative='greater')[1])
    a,b=agg([300]),agg([d for d in range(280,321) if d!=300])
    print(' subs 300 vs others, fisher greater p=',fisher_exact([[a[4],a[0]-a[4]],[b[4],b[0]-b[4]]],alternative='greater')[1], a[4],a[0],b[4],b[0])
    a,b=agg([299]),agg([300]); print(' T3 H/AB 299 vs 300 p=',fisher_exact([[a[2],a[1]-a[2]],[b[2],b[1]-b[2]]],alternative='greater')[1])
    a,b=agg([299]),agg([d for d in range(280,321) if d not in(299,300)]); print(' T2 p=',fisher_exact([[a[3],a[0]-a[3]],[b[3],b[0]-b[3]]],alternative='less')[1])
    print(' 299 walkers:',who[(1,'PA')]); print(' 299 subs:',who[(0,'SUB')])
groups(real,'last actual PA (solver definition)')
groups(pas,'last scheduled PA incl. pinch-hit substitution (paper definition, my reading)')
# T4
last2={k:set(sorted(v)[-2:]) for k,v in tg.items()}
A=[0,0,0,0];B=[0,0,0,0]
for k in elig:
    h=ab=0
    for key,seq,team,iab,ih,ibb,kind in real[k]:
        if key in last2[(k[0],team)] and ab>0:
            d=disp(h,ab); g=None
            if d<300 and disp(h+1,ab+1)>=300: g=B
            elif d>=300 and disp(h,ab+1)<300: g=A
            if g is not None: g[0]+=1;g[1]+=iab;g[2]+=ih;g[3]+=ibb
        h+=ih;ab+=iab
print('T4 B',B,'A',A,fisher_exact([[B[2],B[1]-B[2]],[A[2],A[1]-A[2]]],alternative='greater')[1],fisher_exact([[B[3],B[0]-B[3]],[A[3],A[0]-A[3]]],alternative='less')[1])
