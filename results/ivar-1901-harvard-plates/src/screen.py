import json, sys, urllib.request, urllib.parse
objs = {"1627":"1929-09-20","4954":"1975-06-01","2212":"1978-09-20","3122":"1979-03-01","3200":"1983-10-20","3552":"1983-09-01","1866":"1955-01-20"}
out={}
for o,end in objs.items():
    p = dict(format="json", COMMAND=f"'{o};'", EPHEM_TYPE="OBSERVER", CENTER="'500@399'",
             START_TIME="'1885-01-01'", STOP_TIME=f"'{end}'", STEP_SIZE="'4 d'", QUANTITIES="'1,3,9,23'", CSV_FORMAT="YES")
    url = "https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(p)
    r = json.load(urllib.request.urlopen(url, timeout=300))["result"]
    lines = r.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
    rows=[]
    for L in lines:
        c=[x.strip() for x in L.split(",")]
        try:
            rows.append((c[0], float(c[3]), float(c[4]), float(c[7]), float(c[9])))
        except Exception: pass
    # cols: date, , , RA, DEC, dRA, dDEC, APmag, Sbrt, S-O-T
    good=[]
    for L in lines:
        c=[x.strip() for x in L.split(",")]
        try:
            V=float(c[7]); elong=float(c[9]); good.append((V,c[0],elong,c[3],c[4],c[5],c[6]))
        except: pass
    good.sort()
    out[o]=good[:8]
    print(o, len(lines), [ (g[0],g[1][:12],g[2]) for g in good[:8]], flush=True)
    print("   n(V<12.5):", sum(1 for g in good if g[0]<12.5), " n(V<13):", sum(1 for g in good if g[0]<13))
json.dump(out, open("work/screen.json","w"), indent=1)
