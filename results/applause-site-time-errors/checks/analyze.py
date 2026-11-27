"""APPLAUSE DR4 site-swap test (see PROTOCOL.md). Usage: python3 -I analyze.py RAWDIR OUT.json"""
import sys, re, math, json, random
from collections import defaultdict
from math import sin, cos, radians, degrees, asin, atan2, fmod

def rows(path):
    t = open(path, encoding='utf-8').read()
    names = re.findall(r'<FIELD name="([^"]+)"', t)
    for r in re.findall(r'<TR>(.*?)</TR>', t, re.S):
        v = re.findall(r'<TD>(.*?)</TD>|<TD/>', r, re.S)
        v = [x.strip() for x in re.findall(r'<TD>(.*?)</TD>', r.replace('<TD/>', '<TD></TD>'), re.S)]
        yield dict(zip(names, v))

def sun(jd, lon_e, lat):
    """Altitude (deg) and local apparent solar time (h) of the Sun. Meeus ch. 25 low precision."""
    T = (jd - 2451545.0) / 36525.0
    L0 = fmod(280.46646 + 36000.76983 * T, 360)
    M = radians(357.52911 + 35999.05029 * T)
    C = (1.914602 - 0.004817 * T) * sin(M) + 0.019993 * sin(2 * M) + 0.000289 * sin(3 * M)
    om = radians(125.04 - 1934.136 * T)
    lam = radians(L0 + C - 0.00569 - 0.00478 * sin(om))
    eps = radians(23.439291 - 0.0130042 * T + 0.00256 * cos(om))
    ra = atan2(cos(eps) * sin(lam), cos(lam)); dec = asin(sin(eps) * sin(lam))
    gmst = fmod(280.46061837 + 360.98564736629 * (jd - 2451545.0), 360)
    H = radians(gmst + lon_e) - ra
    phi = radians(lat)
    alt = degrees(asin(sin(phi) * sin(dec) + cos(phi) * cos(dec) * cos(H)))
    last = (degrees(H) / 15.0 + 12.0) % 24.0  # apparent solar time, 0 = midnight
    return alt, last

# Swapped site records (Q1, from geography; see PROTOCOL.md)
SWAPPED = {"Dr. Remeis-Observatory, Bamberg, Germany", "Muottas Muragl, Switzerland",
           "Hotel Schatzalp, Davos, Switzerland", "Observatorio de Fisica Cosmica, San Miguel, Argentina"}

def stats(items, shift_h=0.0):
    n = len(items); d6 = d0 = 0; sx = sy = 0.0; flags = []
    for jd, lon, lat in items:
        a, t = sun(jd + shift_h / 24.0, lon, lat)
        d6 += a > -6; d0 += a > 0; flags.append(a > -6)
        th = t / 24 * 2 * math.pi; sx += cos(th); sy += sin(th)
    m = (math.atan2(sy, sx) / (2 * math.pi) * 24.0)
    m = (m + 12) % 24 - 12
    return dict(n=n, D6=d6 / n, D0=d0 / n, M=m), flags

def binom_tail(b, n):
    return sum(math.comb(n, k) for k in range(b, n + 1)) / 2 ** n

def main(raw, out):
    plates = {r['plate_id']: r for r in rows(raw + '/plate.xml')}
    blocks = defaultdict(list); deltas = {}
    for e in rows(raw + '/exposure.xml'):
        if not e['jd_mid'] or not e['time_orig_start']: continue
        try:
            if not float(e['exptime']) > 0: continue
        except ValueError: continue
        p = plates.get(e['plate_id'])
        if not p or not p['site_longitude'] or not p['site_latitude']: continue
        lon, lat = float(p['site_longitude']), float(p['site_latitude'])
        key = f"{e['archive_id']}|{p['site_name']}"
        if p['site_name'] in SWAPPED:
            deltas[key] = (lon - lat) / 15.0
            lon, lat = lat, lon
        blocks[key].append((float(e['jd_mid']), lon, lat))
    rng = random.Random(20261127); res = {}
    for key, items in sorted(blocks.items()):
        if len(items) < 50: continue
        s, f0 = stats(items)
        plac = []
        for _ in range(200):
            u = [(jd + rng.uniform(-0.5, 0.5), lo, la) for jd, lo, la in items]
            plac.append(stats(u)[0]['D6'])
        s['D6_placebo'] = sum(plac) / len(plac)
        if key in deltas:
            dl = deltas[key]; s['Delta_h'] = dl
            s2, f1 = stats(items, dl)
            b = sum(1 for x, y in zip(f0, f1) if x and not y); c = sum(1 for x, y in zip(f0, f1) if y and not x)
            s.update(D6_shift=s2['D6'], D0_shift=s2['D0'], M_shift=s2['M'], b=b, c=c,
                     p_sign=binom_tail(b, b + c) if b + c else 1.0)
            sup = s['D6'] >= .05 and s2['D6'] <= s['D6'] / 3 and s['p_sign'] < .01 and abs(s['M'] + dl) < 1
            ref = s['D6'] < .03 and abs(s['M']) < 1
            s['verdict'] = 'supported' if sup else 'refuted' if ref else 'inconclusive'
        res[key] = s
    k = [x for x in res if x.startswith('101|')][0]
    inj, _ = stats(blocks[k], 2.5998)
    res['INJECTION_101_plus2.5998h'] = inj
    res['INJECTION_detected'] = inj['D6'] >= .05 and abs(inj['M'] - res[k]['M']) > 1.5
    json.dump(res, open(out, 'w'), indent=1, sort_keys=True)
    for kk, v in res.items(): print(kk, v)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
