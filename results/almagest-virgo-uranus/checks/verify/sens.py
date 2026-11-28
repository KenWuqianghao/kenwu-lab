"""Verifier sensitivity checks (variant longitude 177;00, bootstrap of the percentiles). Usage: python -I sens.py RAWDIR VECDIR"""
import sys, runpy, numpy as np
sys.argv=['x',sys.argv[1],sys.argv[2]]
import io, contextlib
import os
with contextlib.redirect_stdout(io.StringIO()): g=runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)),'indep.py'))
sep=g['sep']; P=g['P']; ix=g['ix']; sl,sb=g['stars'](1674487.5); o=g['o']; tj,ul,ub,el=g['tj'],g['ul'],g['ub'],g['el']
C=[e for e in P if e['I']=='1' and e['HIP'] and int(e['HIP']) in ix and abs(e['bet'])<=10 and e['P']!='513']
i=np.array([ix[int(e['HIP'])] for e in C]); lam=np.array([e['lam'] for e in C]); bet=np.array([e['bet'] for e in C])
vp=np.array([int(e['VP']) if e['VP'].isdigit() else -1 for e in C])
res=sep(lam-o['dL'],bet-o['dB'],sl[i],sb[i])*60; R=res[vp>=5]; g_=el>=120
for name,L,B in (('Toomer 177;15 +0;10',177.25,1/6),('Hertzog/Peters-Knobel 177;00 +0;10',177.0,1/6),('177;00 -0;10',177.0,-1/6)):
    x,y=L-o['dL'],B-o['dB']; rs=sep(x,y,sl[ix[66098]],sb[ix[66098]])*60; du=(sep(x,y,ul[g_],ub[g_])*60).min()
    print(name,'76Vir %.1f Q=%.1f | Uranus %.1f Q=%.1f'%(rs,100*np.mean(R<=rs),du,100*np.mean(R<=du)))
# bootstrap of percentiles (sampling uncertainty of R)
rng=np.random.default_rng(1); qs=[];qu=[]
for _ in range(5000):
    r=rng.choice(R,len(R)); qs.append(100*np.mean(r<=o['r_star'])); qu.append(100*np.mean(r<=o['d_U']))
print('bootstrap Q_S 2.5/97.5',np.percentile(qs,[2.5,97.5]),'Q_U',np.percentile(qu,[2.5,97.5]),'P(Q_S>95)',np.mean(np.array(qs)>95),'P(Q_U<=50)',np.mean(np.array(qu)<=50))
