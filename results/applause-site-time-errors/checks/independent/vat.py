import sys,warnings,collections
warnings.simplefilter('ignore')
import numpy as np
from astropy.io.votable import parse_single_table
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, get_sun, SkyCoord
import astropy.units as u
from scipy.stats import binomtest
t=parse_single_table(sys.argv[1]).to_table()
loc=EarthLocation(lon=12.6505*u.deg,lat=41.7472*u.deg,height=430*u.m)
jd=np.array(t['jd_mid'],float)
tm=Time(jd,format='jd',scale='ut1')
def sunalt(tt): return get_sun(tt).transform_to(AltAz(obstime=tt,location=loc)).alt.deg
alt=sunalt(tm)
def hrs(s):
    p=[float(x) for x in str(s).split(':')]; return p[0]+p[1]/60+(p[2] if len(p)>2 else 0)/3600
o=np.array([hrs(s) for s in t['time_orig_start']])+np.array(t['exptime'],float)/7200
ra=np.array([hrs(s) for s in t['ra_orig']])
dec=np.array(t['dec_icrs'],float)
wrap=lambda x:(x+12)%24-12
lst=tm.sidereal_time('mean',longitude=loc.lon).hour
# check ut_mid == o verbatim
utc=(jd+0.5)%1*24
print('n',len(t),'max |ut_mid clock - o| h:',np.abs(wrap(utc-o)).max())
print('missing ra',sum(1 for s in t['ra_orig'] if not str(s).strip()))
day=alt>-6
print('D6',day.mean(),'D0',(alt>0).mean(),'n day',day.sum())
yr=np.array([int(str(s)[:4]) for s in t['ut_mid']])
dB=wrap(o-lst)*0.99727
tB=Time(jd+dB/24,format='jd',scale='ut1'); altB=sunalt(tB)
print('H_B (nearest) D6',(altB>-6).mean(), 'b',(day&~(altB>-6)).sum(),'c',(~day&(altB>-6)).sum())
# same-date rule: UT on logged date (0..24h UT of date_orig) where LST=o
jd0=np.floor(jd+0.5)-0.5
lst0=Time(jd0,format='jd',scale='ut1').sidereal_time('mean',longitude=loc.lon).hour
dsame=((o-lst0)%24)*0.99727
altS=sunalt(Time(jd0+dsame/24,format='jd',scale='ut1'))
print('H_B same-UT-date D6',(altS>-6).mean(),' differs from nearest by a day for',(np.abs((jd0+dsame/24)-(jd+dB/24))>0.5).sum())
# local-evening rule: local civil date = date_orig, time in [12h local on date, 12h next day)
haA=np.abs(wrap(lst-ra)); haB=np.abs(wrap(o-ra))
A=haA<3;B=haB<3
print('HA all: APP',A.mean(),'HB',B.mean(),'b',(B&~A).sum(),'c',(A&~B).sum(),binomtest(int((B&~A).sum()),int((B^A).sum())).pvalue,'median HB',np.median(haB),'median APP',np.median(haA))
for name,m in [('daylight',day),('night',~day)]:
    print(name,'n',m.sum(),'APP<3',A[m].mean(),'HB<3',B[m].mean(),'b',(B&~A&m).sum(),'c',(A&~B&m).sum(),'median|Delta|',np.median(np.abs(dB[m])),'frac |Delta|<1h',(np.abs(dB[m])<1).mean())
# target altitude at midpoint under each reading
sc=SkyCoord(ra*15*u.deg,dec*u.deg)
altA=sc.transform_to(AltAz(obstime=tm,location=loc)).alt.deg
altHB=sc.transform_to(AltAz(obstime=tB,location=loc)).alt.deg
print('target below horizon: APP',(altA<0).mean(),'HB',(altHB<0).mean(),' target alt<20: APP',(altA<20).mean(),'HB',(altHB<20).mean())
for name,m in [('daylight',day),('night',~day)]:
    print(' ',name,'target<0 APP',(altA[m]<0).mean(),'HB',(altHB[m]<0).mean(),'<20 APP',(altA[m]<20).mean(),'HB',(altHB[m]<20).mean())
print('by 5-yr: yr n nday HB<3 APP<3 tgt<20APP tgt<20HB')
for y0 in range(1950,2000,5):
    m=(yr>=y0)&(yr<y0+5)
    if m.sum(): print(y0,m.sum(),day[m].sum(),round(B[m].mean(),2),round(A[m].mean(),2),round((altA[m]<20).mean(),2),round((altHB[m]<20).mean(),2))
# alternative: constant clock offsets
for sh in (-2,-1,1,2):
    print('shift',sh,'D6',(sunalt(Time(jd+sh/24,format='jd',scale='ut1'))>-6).mean())
# placebo for H_B: permute o among exposures (break link between o and date), recompute H_B D6 -> always night? 
rng=np.random.default_rng(1)
pl=[]
for i in range(50):
    op=rng.permutation(o); d=wrap(op-lst)*0.99727
    pl.append((sunalt(Time(jd+d/24,format='jd',scale='ut1'))>-6).mean())
print('H_B D6 with o permuted: mean',np.mean(pl),'min',np.min(pl))
plh=[(np.abs(wrap(rng.permutation(o)-ra))<3).mean() for i in range(200)]
print('HB<3 with o permuted: mean',np.mean(plh),'max',np.max(plh))
import collections
print(collections.Counter(yr.tolist()))
