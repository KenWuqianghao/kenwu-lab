import json,sys,glob,math
from collections import Counter
from scipy.stats import binomtest, fisher_exact
root=sys.argv[1]
e=json.load(open(root+'/data/expected.json'))
print(json.dumps(e['paper_comparisons'],indent=0)[-900:])
# own T1 from MLB API totals, using the API's own 'avg' string too
c=Counter(); cs=Counter(); n=0; multi=0
for y in range(2009,2026):
    js=json.load(open(f'{root}/work/val/mlb{y}.json'))
    sp=js['stats'][0]['splits']; ids=Counter(s['player']['id'] for s in sp)
    multi+=sum(1 for v in ids.values() if v>1)
    for s in sp:
        h,ab=s['stat']['hits'],s['stat']['atBats']
        if ab>=200:
            n+=1; c[math.floor(1000*h/ab+0.5)]+=1; cs[s['stat']['avg']]+=1
print('mlb elig',n,'dup ids',multi,'300/299',c[300],c[299],'avg-string',cs['.300'],cs['.299'],'330/329',c[330],c[329],'298-301',c[298],c[299],c[300],c[301])
print('binom',binomtest(47,67,.5,alternative='greater').pvalue)
ci=binomtest(47,67).proportion_ci(method='exact'); print('ci',ci.low/(1-ci.low),ci.high/(1-ci.high))
print('T2',fisher_exact([[3,20],[89,1003]],alternative='less')[1])
print('T3',fisher_exact([[8,11],[4,16]],alternative='greater')[1])
print('T4',fisher_exact([[62,155],[14,53]],alternative='greater')[1])
print('C2',fisher_exact([[0,61],[3,20]])[1])
ps={'P2':fisher_exact([[16,42],[8,47]],alternative='greater')[1],'P3':fisher_exact([[8,15],[229,883]],alternative='greater')[1],
'P4':fisher_exact([[3,55],[2,53]],alternative='less')[1],'P5':fisher_exact([[1,57],[11,44]],alternative='less')[1],'P6':fisher_exact([[9,21],[63,1042]],alternative='greater')[1]}
o=sorted(ps,key=ps.get); run=0
for r,k in enumerate(o):
    run=max(run,min(1,(5-r)*ps[k])); print(k,ps[k],'holm',run)
