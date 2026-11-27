import sys,warnings
warnings.simplefilter('ignore')
import numpy as np
from astropy.io.votable import parse_single_table
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
import astropy.units as u
t=parse_single_table(sys.argv[1]).to_table()
loc=EarthLocation(lon=12.6505*u.deg,lat=41.7472*u.deg,height=430*u.m)
jd=np.array(t['jd_mid'],float); tm=Time(jd,format='jd',scale='ut1')
def hrs(s):
    p=[float(x) for x in str(s).split(':')]; return p[0]+p[1]/60+(p[2] if len(p)>2 else 0)/3600
o=np.array([hrs(s) for s in t['time_orig_start']])+np.array(t['exptime'],float)/7200
ra=np.array([hrs(s) for s in t['ra_orig']]); dec=np.radians(np.array(t['dec_icrs'],float)); phi=np.radians(41.7472)
wrap=lambda x:(x+12)%24-12
def talt(lsth): 
    H=np.radians((lsth-ra)*15); return np.degrees(np.arcsin(np.sin(phi)*np.sin(dec)+np.cos(phi)*np.cos(dec)*np.cos(H)))
lst=tm.sidereal_time('mean',longitude=loc.lon).hour
print('target alt<20: APP',(talt(lst)<20).mean(),'HB',(talt(o)<20).mean())
rng=np.random.default_rng(2)
pl=[(talt(rng.permutation(o))<20).mean() for i in range(1000)]
print('HB with o permuted: mean',np.mean(pl),'min',np.min(pl))
yr=np.array([str(s)[:4] for s in t['ut_mid']])
for r in t[yr=='2000']: print(r['exposure_id'],r['plate_id'],r['date_orig_start'],r['time_orig_start'],r['ut_mid'],r['object_name'])
print(min(t['ut_mid']),max(t['ut_mid']))
# exposure 1 night->day under HB
