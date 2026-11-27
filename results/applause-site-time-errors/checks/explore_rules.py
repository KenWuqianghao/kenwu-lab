"""Exploratory (post-hoc, PROTOCOL addendum 1). Two fixed time-misreading rules on flagged blocks.
H_A: logged value is local mean time (from midnight) but was read as local sidereal time.
H_B: logged value is local sidereal time but was read as clock time.
For each exposure: t_C = t_D + Delta, Delta = wrap(orig - X(t_D)) where X = LMT (H_A) or LST (H_B), wrap to (-12,12] h;
for H_B the sidereal difference is scaled by 0.99727 to solar hours."""
import sys, re, collections, math
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from analyze import rows, sun
raw = sys.argv[1]; arch = sys.argv[2].split(',')
plates = {r['plate_id']: r for r in rows(raw + '/plate.xml')}
def wrap(x): return (x + 12) % 24 - 12
def lst(jd, lon):
    return ((280.46061837 + 360.98564736629 * (jd - 2451545.0) + lon) % 360) / 15
def lmt(jd, lon):
    return ((jd + 0.5) % 1 * 24 + lon / 15) % 24
for a in arch:
    n = cnt = 0; d = collections.Counter(); bc = collections.Counter()
    for e in rows(raw + '/exposure.xml'):
        if e['archive_id'] != a or not e['jd_mid'] or not e['time_orig_start']: continue
        try:
            if not float(e['exptime']) > 0: continue
        except ValueError: continue
        m = re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}))?', e['time_orig_start'])
        if not m: continue
        o = int(m[1]) + int(m[2]) / 60 + int(m[3] or 0) / 3600 + float(e['exptime']) / 7200  # midpoint
        p = plates[e['plate_id']]
        if not p['site_longitude']: continue
        lon, lat = float(p['site_longitude']), float(p['site_latitude'])
        jd = float(e['jd_mid']); n += 1
        r0 = sun(jd, lon, lat)[0] > -6
        dA = wrap(o - lmt(jd, lon)); dB = wrap(o - lst(jd, lon)) * 0.99727
        rA = sun(jd + dA / 24, lon, lat)[0] > -6; rB = sun(jd + dB / 24, lon, lat)[0] > -6
        d['raw'] += r0; d['H_A'] += rA; d['H_B'] += rB
        bc['A_b'] += r0 and not rA; bc['A_c'] += rA and not r0; bc['B_b'] += r0 and not rB; bc['B_c'] += rB and not r0
        st = e['time_orig_start'].startswith('ST'); d['ST_prefix'] += st
    pa = sum(math.comb(bc['A_b'] + bc['A_c'], k) for k in range(bc['A_b'], bc['A_b'] + bc['A_c'] + 1)) / 2 ** (bc['A_b'] + bc['A_c'])
    pb = sum(math.comb(bc['B_b'] + bc['B_c'], k) for k in range(bc['B_b'], bc['B_b'] + bc['B_c'] + 1)) / 2 ** (bc['B_b'] + bc['B_c'])
    print(f"archive {a}: n={n} ST-prefixed={d['ST_prefix']} D6 raw={d['raw']/n:.3f} H_A={d['H_A']/n:.3f} H_B={d['H_B']/n:.3f} "
          f"A(b,c)=({bc['A_b']},{bc['A_c']}) pA={pa:.2g} B(b,c)=({bc['B_b']},{bc['B_c']}) pB={pb:.2g}")
