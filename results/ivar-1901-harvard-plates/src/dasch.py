"""Polite DASCH DR7 client (one request at a time, 3 s apart). Cutouts are capped at CAP for this project,
and each request is logged in data/cutouts/log.jsonl with its payload and SHA-256."""
import base64, csv, gzip, hashlib, io, json, os, time
from pathlib import Path
import requests
BASE = "https://api.starglass.cfa.harvard.edu/public"
HEADERS = {"User-Agent": "precovery-records (research script)", "Accept": "application/json"}
CAP = 32
CUT = (Path(os.environ["PRECOVERY_DATA"]) if os.environ.get("PRECOVERY_DATA") else Path(__file__).resolve().parent.parent / "data") / "cutouts"
_last = [0.0]

def _post(endpoint, payload, timeout=180):
    for attempt in range(2):
        wait = 3.0 - (time.time() - _last[0])
        if wait > 0: time.sleep(wait)
        _last[0] = time.time()
        r = requests.post(BASE + endpoint, json=payload, headers=HEADERS, timeout=timeout)
        if (r.status_code == 429 or r.status_code >= 500) and attempt == 0:
            time.sleep(60); continue
        r.raise_for_status(); return r.json()

def _csv(rows):
    rdr = csv.reader(io.StringIO("\n".join(rows))); hdr = next(rdr)
    return [dict(zip(hdr, r)) for r in rdr]

def querycat(ra, dec, radius_arcsec, refcat="atlas"):
    return _csv(_post("/dasch/dr7/querycat", {"refcat": refcat, "ra_deg": float(ra) % 360, "dec_deg": float(dec),
                                              "radius_arcsec": float(radius_arcsec)}))

def cutout(plate_id, solnum, ra, dec):
    CUT.mkdir(parents=True, exist_ok=True)
    out = CUT / f"{plate_id}_s{solnum}.fits.gz"
    if out.exists(): return out
    log = CUT / "log.jsonl"
    n = sum(1 for _ in open(log)) if log.exists() else 0
    if n >= CAP: raise RuntimeError(f"cutout cap {CAP} reached")
    payload = {"plate_id": plate_id, "solution_number": int(solnum), "center_ra_deg": float(ra) % 360, "center_dec_deg": float(dec)}
    e = {"n": n + 1, "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "payload": payload}
    try:
        raw = base64.b64decode(_post("/dasch/dr7/cutout", payload)); gzip.decompress(raw)
        out.write_bytes(raw); e.update(ok=True, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    except Exception as ex:
        e.update(ok=False, err=str(ex)[:300])
    with open(log, "a") as f: f.write(json.dumps(e) + "\n")
    if not e["ok"]: raise RuntimeError(e["err"])
    return out
