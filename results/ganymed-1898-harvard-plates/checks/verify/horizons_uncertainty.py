import requests,json,sys
sys.path.insert(0,'src')
from plates import PLATES
for obj,hid,plate,sol,mid,expm,lim in PLATES:
    if obj!='Ganymed': continue
    p={"format":"json","COMMAND":"'1036;'","OBJ_DATA":"NO","MAKE_EPHEM":"YES","EPHEM_TYPE":"OBSERVER","CENTER":"'802@399'",
       "TLIST":"'%s'"%mid.replace('T',' '),"QUANTITIES":"'1,9,36,37'","CSV_FORMAT":"YES","ANG_FORMAT":"DEG"}
    t=requests.get("https://ssd.jpl.nasa.gov/api/horizons.api",params=p,timeout=120).json()["result"]
    L=t.splitlines(); i=L.index("$$SOE"); print(plate, L[i-2].strip() if plate=='i21050' else '', '\n  ', L[i+1].strip())
