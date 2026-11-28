"""Small Horizons API helper: observer ephemeris -> list of dicts (jd, date, ra, dec, V, elong, r, delta)."""
import requests, time, re, json, hashlib, os
from pathlib import Path
CACHE = Path(__file__).resolve().parent.parent / "data" / "hz_cache"
CACHE.mkdir(parents=True, exist_ok=True)
URL = "https://ssd.jpl.nasa.gov/api/horizons.api"

def eph(cmd, start, stop, step, center="500@399", quantities="1,9,19,20,23", extra=None):
    p = {"format": "json", "COMMAND": f"'{cmd}'", "OBJ_DATA": "NO", "MAKE_EPHEM": "YES",
         "EPHEM_TYPE": "OBSERVER", "CENTER": f"'{center}'", "START_TIME": f"'{start}'",
         "STOP_TIME": f"'{stop}'", "STEP_SIZE": f"'{step}'", "QUANTITIES": f"'{quantities}'",
         "CSV_FORMAT": "YES", "ANG_FORMAT": "DEG", "CAL_FORMAT": "BOTH", "EXTRA_PREC": "NO"}
    if extra: p.update(extra)
    key = hashlib.sha1(json.dumps(p, sort_keys=True).encode()).hexdigest()
    f = CACHE / (key + ".txt")
    fz = CACHE / (key + ".txt.gz")
    if fz.exists():
        import gzip; txt = gzip.decompress(fz.read_bytes()).decode()
    elif f.exists():
        txt = f.read_text()
    else:
        for a in range(3):
            try:
                r = requests.get(URL, params=p, timeout=180)
                r.raise_for_status()
                txt = r.json()["result"]; break
            except Exception as e:
                time.sleep(10)
        else:
            raise RuntimeError("horizons failed")
        import gzip; fz.write_bytes(gzip.compress(txt.encode()))
        time.sleep(0.5)
    return parse(txt)

def parse(txt):
    if "$$SOE" not in txt:
        raise RuntimeError(txt[:1500])
    hdr = None
    lines = txt.splitlines()
    for i, l in enumerate(lines):
        if l.strip() == "$$SOE":
            hdr = [h.strip() for h in lines[i-2].split(",")]
            body = lines[i+1:lines.index("$$EOE")]
            break
    out = []
    for l in body:
        v = [x.strip() for x in l.split(",")]
        if len(v) == len(hdr) - 1 and hdr[2] == hdr[3] == "":
            # A rise/transit/set mark ("t ", "tm") fills both flag columns without the comma between them.
            v = v[:2] + ["", v[2]] + v[3:]
        if len(v) != len(hdr):
            raise RuntimeError(f"Horizons row has {len(v)} fields, header has {len(hdr)}: {l}")
        d = dict(zip(hdr, v))
        out.append(d)
    return out

def num(x):
    try: return float(x)
    except: return None
