import json, sys, urllib.request, urllib.parse, math
o,start,stop,vmax=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4])
p = dict(format="json", COMMAND=f"'{o};'", EPHEM_TYPE="OBSERVER", CENTER="'500@399'",
         START_TIME=f"'{start}'", STOP_TIME=f"'{stop}'", STEP_SIZE="'2 d'", QUANTITIES="'1,3,9,20,23'", CSV_FORMAT="YES", ANG_FORMAT="DEG")
r = json.load(urllib.request.urlopen("https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(p), timeout=300))["result"]
for L in r.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines():
    c=[x.strip() for x in L.split(",")]
    try: V=float(c[7])
    except: continue
    rate=math.hypot(float(c[5]),float(c[6]))
    if V<vmax and float(c[11])>60: print(c[0][:11], f"RA {float(c[3]):7.2f} Dec {float(c[4]):6.2f} V {V:5.2f} rate {rate:6.0f}\"/h elong {float(c[11]):5.1f} delta {float(c[9]):.3f}")
