import sys,warnings,csv,re
warnings.simplefilter('ignore')
import numpy as np
from astropy.io.votable import parse_single_table
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, get_sun
import astropy.units as u
raw=sys.argv[1]
p=parse_single_table(raw+'/plate.xml').to_table()
e=parse_single_table(raw+'/exposure.xml').to_table()
site={int(r['plate_id']):(str(r['site_name']),r['site_longitude'],r['site_latitude']) for r in p}
def run(arch,name,swap,shift=0.0):
    m=(np.array(e['archive_id'])==arch)
    jd=[];
    for r in e[m]:
        s=site[int(r['plate_id'])]
        if s[0]!=name: continue
        if np.ma.is_masked(r['jd_mid']) or not str(r['time_orig_start']).strip(): continue
        if np.ma.is_masked(r['exptime']) or not float(r['exptime'])>0: continue
        jd.append(float(r['jd_mid'])); lon,lat=float(s[1]),float(s[2])
    if swap: lon,lat=lat,lon
    jd=np.array(jd)+shift/24
    tm=Time(jd,format='jd',scale='ut1'); loc=EarthLocation(lon=lon*u.deg,lat=lat*u.deg)
    alt=get_sun(tm).transform_to(AltAz(obstime=tm,location=loc)).alt.deg
    print(arch,name[:25],'swap' if swap else 'recorded','shift',round(shift,3),'n',len(jd),'D6',round((alt>-6).mean(),4),'D0',round((alt>0).mean(),4))
    return alt>-6
B='Dr. Remeis-Observatory, Bamberg, Germany';S='Observatorio de Fisica Cosmica, San Miguel, Argentina'
a=run(208,B,True); b=run(208,B,True,(49.8845-10.8881)/15); print('discordant',(a&~b).sum(),(b&~a).sum())
run(208,B,False)
run(205,S,True); run(205,S,True,(-34.5567+58.7317)/15); run(205,S,False)
run(208,'Muottas Muragl, Switzerland',True); run(208,'Hotel Schatzalp, Davos, Switzerland',True)
h=run(101,'Hamburg-Bergedorf, Germany',False); run(101,'Hamburg-Bergedorf, Germany',False,2.5998)
