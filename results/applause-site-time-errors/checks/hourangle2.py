"""Addendum 3 test: HA_APP = LST(ut_mid) - RA versus HA_HB = o - RA."""
import sys, re, json, math
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from analyze import rows
from hourangle_util import parse_ra, wrap, lst
raw = sys.argv[1]
plates = {r['plate_id']: r for r in rows(raw + '/plate.xml')}
ra = {r['exposure_id']: r for r in rows(raw + '/exposure_ra.xml')}
res = {}
for a in ('501', '101'):
    A = []; B = []
    for e in rows(raw + '/exposure.xml'):
        if e['archive_id'] != a or not e['time_orig_start'] or not e['jd_mid']: continue
        try:
            if not float(e['exptime']) > 0: continue
        except ValueError: continue
        r = ra.get(e['exposure_id']); h = parse_ra(r['ra_orig']) if r else None
        if h is None and r: h = parse_ra(r['ra_icrs'])
        m = re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}))?', e['time_orig_start'])
        if h is None or not m: continue
        o = int(m[1]) + int(m[2]) / 60 + int(m[3] or 0) / 3600 + float(e['exptime']) / 7200
        lon = float(plates[e['plate_id']]['site_longitude'])
        A.append(abs(wrap(lst(float(e['jd_mid']), lon) - h)) < 3); B.append(abs(wrap(o - h)) < 3)
    n = len(A); fa = sum(A) / n; fb = sum(B) / n
    b = sum(1 for x, y in zip(A, B) if y and not x); c = sum(1 for x, y in zip(A, B) if x and not y)
    k = min(b, c); p = min(1.0, 2 * sum(math.comb(b + c, i) for i in range(k + 1)) / 2 ** (b + c)) if b + c else 1.0
    res[a] = dict(n=n, frac_HA_APP_lt3=fa, frac_HA_HB_lt3=fb, diff=fb - fa, b_HBonly=b, c_APPonly=c, p_two_sided=p)
    print(a, res[a])
json.dump(res, open('data/hourangle2.json', 'w'), indent=1)
