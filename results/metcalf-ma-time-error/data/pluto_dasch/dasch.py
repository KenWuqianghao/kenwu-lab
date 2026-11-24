"""Polite client for the DASCH DR7 public API. One request at a time, a pause between requests,
and a hard cap on cutouts that persists across runs (data/cutout_log.jsonl)."""
import base64, gzip, hashlib, json, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://api.starglass.cfa.harvard.edu/public"
CUTOUT_CAP = 100
PAUSE_S = 3.0
LOG = ROOT / "cutout_manifest.jsonl"  # tracked in git: URL, payload, SHA-256 per cutout
CUTDIR = ROOT / "data" / "cutouts"
HEADERS = {"User-Agent": "pluto-dasch-pilot", "Accept": "application/json"}
_last = [0.0]


def _post(endpoint, payload, timeout=120):
    for attempt in range(2):
        wait = PAUSE_S - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        r = requests.post(BASE + endpoint, json=payload, headers=HEADERS, timeout=timeout)
        if r.status_code == 429 or r.status_code >= 500:
            if attempt == 0:
                time.sleep(60)
                continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"{endpoint} failed twice: HTTP {r.status_code} {r.text[:200]}")


def queryexps(ra, dec, tmin=None, tmax=None):
    p = {"ra_deg": float(ra) % 360, "dec_deg": float(dec)}
    if tmin: p["midpoint_min"] = tmin
    if tmax: p["midpoint_max"] = tmax
    rows = _post("/dasch/dr7/queryexps", p)
    import csv, io
    rdr = csv.reader(io.StringIO("\n".join(rows)))
    hdr = next(rdr)
    return [dict(zip(hdr, r)) for r in rdr]


def querycat(ra, dec, radius_arcsec, refcat="atlas"):
    p = {"refcat": refcat, "ra_deg": float(ra) % 360, "dec_deg": float(dec), "radius_arcsec": float(radius_arcsec)}
    rows = _post("/dasch/dr7/querycat", p)
    import csv, io
    rdr = csv.reader(io.StringIO("\n".join(rows)))
    hdr = next(rdr)
    return [dict(zip(hdr, r)) for r in rdr]


def _log_entries():
    if not LOG.exists():
        return []
    return [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]


def cutouts_used():
    return len(_log_entries())


def cutout(plate_id, solnum, ra, dec, tag):
    """Fetch one cutout unless already on disk. Each network request counts toward the cap,
    including failed ones."""
    CUTDIR.mkdir(parents=True, exist_ok=True)
    out = CUTDIR / f"{tag}.fits.gz"
    if out.exists():
        return out
    n = cutouts_used()
    if n >= CUTOUT_CAP:
        raise RuntimeError(f"cutout cap reached ({n}/{CUTOUT_CAP}); refusing request")
    payload = {"plate_id": plate_id, "solution_number": int(solnum),
               "center_ra_deg": float(ra) % 360, "center_dec_deg": float(dec)}
    entry = {"n": n + 1, "tag": tag, "url": BASE + "/dasch/dr7/cutout", "payload": payload,
             "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        res = _post("/dasch/dr7/cutout", payload)
        if not isinstance(res, str) or not res:
            raise RuntimeError(f"no image: {str(res)[:200]}")
        raw = base64.b64decode(res)
        gzip.decompress(raw)  # check that it is gzip data
        out.write_bytes(raw)
        entry.update(ok=True, file=str(out.relative_to(ROOT)), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    except Exception as e:
        entry.update(ok=False, error=str(e)[:300])
    with LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    if not entry["ok"]:
        raise RuntimeError(entry["error"])
    return out
