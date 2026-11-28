"""Independent verifier recomputation. Written from PROTOCOL.md, not from analysis.py.
Stars: linear space motion of unit vector + erfa long-term precession (Vondrak 2011) ecliptic matrix.
Uranus: Horizons geocentric ICRF vectors (light-time corrected), rotated with the same matrix; elongation from Sun vectors.
Usage: python -I indep.py RAWDIR VECDIR"""
import sys, csv, math, json
import numpy as np, erfa
raw, vec = sys.argv[1], sys.argv[2]
def tsv(p):
    L=[l.rstrip('\n') for l in open(p) if l.strip() and not l.startswith('#')]
    h=L[0].split('\t'); return [dict(zip(h,[x.strip() for x in l.split('\t')])) for l in L[3:]]
def sx(s):
    sg=-1 if s.strip().startswith('-') else 1; d,m=s.strip().lstrip('+-').split(':')[:2]; return sg*(int(d)+float(m)/60)
def epj(jd): return 2000+(jd-2451545.0)/365.25
def M(jd): return erfa.ltecm(epj(jd))   # ICRS -> mean ecliptic & equinox of date
def lonlat(v):
    v=np.atleast_2d(v); return np.degrees(np.arctan2(v[:,1],v[:,0]))%360, np.degrees(np.arcsin(v[:,2]/np.linalg.norm(v,axis=1)))
def sep(l1,b1,l2,b2):
    l1,b1,l2,b2=[np.radians(np.asarray(x,float)) for x in (l1,b1,l2,b2)]
    a=np.sin((b2-b1)/2)**2+np.cos(b1)*np.cos(b2)*np.sin((l2-l1)/2)**2
    return np.degrees(2*np.arcsin(np.sqrt(a)))
H=[h for h in tsv(raw+'/hip_v65.tsv') if h['RAICRS'] and h['Vmag']]
ra=np.radians([float(h['RAICRS']) for h in H]); de=np.radians([float(h['DEICRS']) for h in H])
pra=np.array([float(h['pmRA'] or 0) for h in H]); pde=np.array([float(h['pmDE'] or 0) for h in H])
V=np.array([float(h['Vmag']) for h in H]); hip=[int(h['HIP']) for h in H]; ix={h:i for i,h in enumerate(hip)}
r=np.c_[np.cos(de)*np.cos(ra),np.cos(de)*np.sin(ra),np.sin(de)]
ea=np.c_[-np.sin(ra),np.cos(ra),0*ra]; ed=np.c_[-np.sin(de)*np.cos(ra),-np.sin(de)*np.sin(ra),np.cos(de)]
mas=math.radians(1/3.6e6)
def stars(jd):
    dt=(jd-2448349.0625)/365.25
    p=r+dt*mas*(pra[:,None]*ea+pde[:,None]*ed)
    return lonlat(p@M(jd).T)
def vecs(p):
    t=open(p).read().split('$$SOE')[1].split('$$EOE')[0].strip().splitlines()
    a=np.array([[float(x.split(',')[i]) for i in (0,2,3,4)] for x in t]); return a[:,0],a[:,1:]
P=tsv(raw+'/ptolemy.tsv')
for e in P:
    e['lam']=sx(e['Elon']); e['bet']=sx(e['Elat'])
def run(jd0, uf, sf, lo=120):
    sl,sb=stars(jd0)
    C=[e for e in P if e['I']=='1' and e['HIP'] and int(e['HIP']) in ix and abs(e['bet'])<=10 and e['P']!='513']
    i=np.array([ix[int(e['HIP'])] for e in C]); lam=np.array([e['lam'] for e in C]); bet=np.array([e['bet'] for e in C])
    dL=np.median((lam-sl[i]+180)%360-180); dB=np.median(bet-sb[i])
    res=sep(lam-dL,bet-dB,sl[i],sb[i])*60
    vp=np.array([int(e['VP']) if e['VP'].isdigit() else -1 for e in C]); faint=vp>=5
    R=res[faint]
    out=dict(nC=len(C),dL=dL,dB=dB,nR=len(R),VPcounts={int(k):int((vp[faint]==k).sum()) for k in set(vp[faint])},
             Rmed=np.median(R),Rp95=np.percentile(R,95))
    tj,uv=vecs(uf); tj2,sv=vecs(sf); assert np.allclose(tj,tj2)
    elong=np.degrees(np.arccos(np.sum(uv*sv,1)/np.linalg.norm(uv,axis=1)/np.linalg.norm(sv,axis=1)))
    ul,ub=np.zeros(len(tj)),np.zeros(len(tj))
    # ecliptic of date for each day (matrix changes slowly; compute per 30 d)
    for k in range(0,len(tj),30):
        s=slice(k,k+30); ul[s],ub[s]=lonlat(uv[s]@M(tj[k]).T)
    g=elong>=lo
    x,y=177.25-dL,1/6-dB
    ds=sep(x,y,sl,sb)*60
    cand=np.argsort(ds)[:6]
    out['near_stars']=[(hip[c],float(V[c]),round(float(ds[c]),1)) for c in cand]
    b=V<=6.0; j=np.where(b,ds,1e9).argmin(); rs=ds[j]
    du=sep(x,y,ul[g],ub[g])*60; k=du.argmin()
    pct=lambda v: 100*np.mean(R<=v)
    out.update(e513=(x,y),r_star=rs,r_hip=hip[j],d_U=du[k],d_U_jd=tj[g][k],d_U_el=elong[g][k],U_at=(ul[g][k],ub[g][k]),Q_S=pct(rs),Q_U=pct(du[k]),nU=int(g.sum()),
               U_lon_range=(ul[g].min(),ul[g].max()))
    band=np.abs(bet)<=3
    dub=np.array([ (sep(l-dL,bb-dB,ul[g],ub[g])*60).min() for l,bb in zip(lam[band],bet[band])])
    out.update(n_band=int(band.sum()),n_match=int((dub<=du[k]).sum()),F=float((dub<=du[k]).mean()))
    # extra: band entries whose longitude lies inside the track range; faint-only band
    inr=((lam[band]-dL)>=ul[g].min()-1)&((lam[band]-dL)<=ul[g].max()+1)
    out['band_in_track_lon']=int(inr.sum()); out['match_in_track']=int((dub[inr]<=du[k]).sum())
    fb=faint[band]; out['band_faint']=int(fb.sum()); out['band_faint_match']=int((dub[fb]<=du[k]).sum())
    out['matches']=[(C[q]['P'],C[q]['cst'],C[q]['N'],C[q]['VP'],round(float(d),1)) for q,d in zip(np.where(band)[0],dub) if d<=du[k]]
    # sensitivity: all window days (no elongation cut), elong>=90
    for lo2 in (0,90,150):
        g2=elong>=lo2; out[f'd_U_el{lo2}']=float((sep(x,y,ul[g2],ub[g2])*60).min())
    # R restricted to VP 5,6 only; to VP==6; latitude-only comparison
    for nm,m in (('VP56',(vp==5)|(vp==6)),('VP6',vp==6),('all',vp>0)):
        RR=res[m]; out['Q_'+nm]=(int(m.sum()),100*np.mean(RR<=rs),100*np.mean(RR<=du[k]))
    # date on Mar 25 -127 (JD of -127-03-25 0h TT)
    return out,(tj,ul,ub,elong)
o,(tj,ul,ub,el)=run(1674487.5,vec+'/ura_vec.txt',vec+'/sun_vec.txt')
print(json.dumps(o,indent=1,default=float))
# Julian calendar date -127 Mar 25: JD
def jul2jd(y,m,d):
    a=(14-m)//12; yy=y+4800-a; mm=m+12*a-3
    return d+(153*mm+2)//5+365*yy+yy//4-32083-0.5
j=jul2jd(-127,3,25); k=np.argmin(abs(tj-j)); print('Julian -127 Mar 25 JD',j,'Uranus',ul[k],ub[k],'elong',el[k])
print('epoch JD 1674487.5 is', 1674487.5-jul2jd(-128,1,1),'days after Julian -128 Jan 1 (astronomical year -128 = 129 BC)')
print('best night days after Julian -127 Jan 1:', o['d_U_jd']-jul2jd(-127,1,1))
