"""Vatican archive 501: per-exposure corrected midpoints and the post hoc controls.
Usage: python3 -I vatican.py RAWDIR OUT.json OUT.csv
Reads RAWDIR/exposure501.xml (fetch_501.sh) and RAWDIR/plate.xml (fetch.sh). Standard library only.
Rule H_B: the logged time o (time_orig_start + exptime/2) is local sidereal time (LST).
DR4 copied o into ut_mid as UT. The corrected midpoint is an instant where LST = o."""
import sys, os, re, json, csv, math, random, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import rows, sun
from hourangle_util import parse_ra, wrap, lst

SOLAR_PER_SIDEREAL = 0.99727
raw, out_json, out_csv = sys.argv[1:4]
site = {p['plate_id']: p for p in rows(raw + '/plate.xml') if p['archive_id'] == '501'}
lons = {(p['site_longitude'], p['site_latitude']) for p in site.values()}
assert len(lons) == 1, lons
lon, lat = map(float, lons.pop())

def hms(s):
    m = re.search(r'(\d{1,2}):(\d{2})(?::(\d{2}(?:\.\d+)?))?', s)
    return int(m[1]) + int(m[2]) / 60 + float(m[3] or 0) / 3600

def jd_of_date(d):  # JD at 0h UT of a Gregorian date 'YYYY-MM-DD'
    y, mo, da = map(int, d[:10].split('-'))
    a = (14 - mo) // 12; y2 = y + 4800 - a; m2 = mo + 12 * a - 3
    return da + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045 - 0.5

def ut_str(jd):
    z = jd + 0.5; f = z % 1; j = int(z)
    a = j + 32044; b = (4 * a + 3) // 146097; c = a - 146097 * b // 4
    d = (4 * c + 3) // 1461; e = c - 1461 * d // 4; m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1; mon = m + 3 - 12 * (m // 10); yr = 100 * b + d - 4800 + m // 10
    s = round(f * 86400); hh, rem = divmod(s, 3600); mm, ss = divmod(rem, 60)
    if hh == 24: return ut_str(jd + 1e-6)
    return f'{yr:04d}-{mon:02d}-{day:02d} {hh:02d}:{mm:02d}:{ss:02d}'

def target_alt(lst_h, ra_h, dec_deg):
    H = math.radians((lst_h - ra_h) * 15); p = math.radians(lat); d = math.radians(dec_deg)
    return math.degrees(math.asin(math.sin(p) * math.sin(d) + math.cos(p) * math.cos(d) * math.cos(H)))

E = []
for e in rows(raw + '/exposure501.xml'):
    if not e['jd_mid'] or not e['time_orig_start']: continue
    if not float(e['exptime'] or 0) > 0: continue
    o = hms(e['time_orig_start']) + float(e['exptime']) / 7200
    jd = float(e['jd_mid'])
    ra = parse_ra(e['ra_orig']) or parse_ra(e['ra_icrs'])
    jd_near = jd + wrap(o - lst(jd, lon)) * SOLAR_PER_SIDEREAL / 24       # nearest instant to the DR4 midpoint
    jd0 = jd_of_date(e['date_orig_start'])
    jd_same = jd0 + ((o - lst(jd0, lon)) % 24) * SOLAR_PER_SIDEREAL / 24   # UT date = logged date
    E.append(dict(e=e, o=o, jd=jd, ra=ra, dec=float(e['dec_icrs']), jd_near=jd_near, jd_same=jd_same))

placeholder = [x for x in E if x['e']['date_orig_start'].startswith('1999')]
dated = [x for x in E if x not in placeholder]
years = sorted(x['e']['date_orig_start'][:10] for x in dated)
day = lambda j: sun(j, lon, lat)[0] > -6
r = dict(n_timed=len(E), n_dated=len(dated), first_date=years[0], last_date=years[-1],
         placeholder=[dict(exposure_id=x['e']['exposure_id'], plate_id=x['e']['plate_id'],
                           date_orig_start=x['e']['date_orig_start'], ut_mid=x['e']['ut_mid']) for x in placeholder])
r['D6_dr4'] = sum(day(x['jd']) for x in E) / len(E)
r['n_day_dr4'] = sum(day(x['jd']) for x in E)
r['D6_near'] = sum(day(x['jd_near']) for x in E) / len(E)
r['D6_same'] = sum(day(x['jd_same']) for x in E) / len(E)
r['n_near_vs_same_differ_by_a_day'] = sum(abs(x['jd_near'] - x['jd_same']) > 0.5 for x in E)
corr = [abs(x['jd_near'] - x['jd']) * 24 for x in dated]
r['median_abs_correction_h'] = statistics.median(corr)
r['max_abs_correction_h'] = max(corr)
r['frac_dated_correction_gt_10min'] = sum(c > 1 / 6 for c in corr) / len(corr)
night = [x for x in E if not day(x['jd'])]
r['n_night_dr4'] = len(night)
r['night_median_abs_correction_h'] = statistics.median(abs(x['jd_near'] - x['jd']) * 24 for x in night)
r['night_frac_correction_lt_1h'] = sum(abs(x['jd_near'] - x['jd']) * 24 < 1 for x in night) / len(night)
alt_app = [target_alt(lst(x['jd'], lon), x['ra'], x['dec']) for x in E]
alt_hb = [target_alt(x['o'], x['ra'], x['dec']) for x in E]
r['target_below_0_dr4'] = sum(a < 0 for a in alt_app) / len(E)
r['target_below_0_HB'] = sum(a < 0 for a in alt_hb) / len(E)
r['target_below_20_dr4'] = sum(a < 20 for a in alt_app) / len(E)
r['target_below_20_HB'] = sum(a < 20 for a in alt_hb) / len(E)
ni = [i for i, x in enumerate(E) if not day(x['jd'])]
r['night_target_below_0_dr4'] = sum(alt_app[i] < 0 for i in ni) / len(ni)
r['night_target_below_0_HB'] = sum(alt_hb[i] < 0 for i in ni) / len(ni)
# Permutation placebos: give each exposure the logged time of another exposure (seed fixed).
rng = random.Random(20261127); os_ = [x['o'] for x in E]
def perm(): p = os_[:]; rng.shuffle(p); return p
d6p = []
for _ in range(50):
    p = perm()
    d6p.append(sum(day(x['jd'] + wrap(q - lst(x['jd'], lon)) * SOLAR_PER_SIDEREAL / 24) for x, q in zip(E, p)) / len(E))
r['perm_D6_mean'] = statistics.mean(d6p); r['perm_D6_min'] = min(d6p)
a20 = []
for _ in range(1000):
    p = perm(); a20.append(sum(target_alt(q, x['ra'], x['dec']) < 20 for x, q in zip(E, p)) / len(E))
r['perm_target_below_20_mean'] = statistics.mean(a20); r['perm_target_below_20_min'] = min(a20)
ha = []
for _ in range(200):
    p = perm(); ha.append(sum(abs(wrap(q - x['ra'])) < 3 for x, q in zip(E, p)) / len(E))
r['perm_HA_lt3_mean'] = statistics.mean(ha); r['perm_HA_lt3_max'] = max(ha)
r['HA_lt3_HB'] = sum(abs(wrap(x['o'] - x['ra'])) < 3 for x in E) / len(E)
json.dump(r, open(out_json, 'w'), indent=1)
with open(out_csv, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['exposure_id', 'plate_id', 'object_name', 'date_orig_start', 'time_orig_start', 'exptime_s',
                'ut_mid_dr4', 'ut_mid_sidereal_nearest', 'ut_mid_sidereal_same_ut_date', 'correction_h_nearest',
                'sun_alt_dr4_deg', 'sun_alt_nearest_deg', 'note'])
    for x in sorted(E, key=lambda x: int(x['e']['exposure_id'])):
        e = x['e']
        w.writerow([e['exposure_id'], e['plate_id'], e['object_name'], e['date_orig_start'], e['time_orig_start'],
                    e['exptime'], e['ut_mid'][:19], ut_str(x['jd_near']), ut_str(x['jd_same']),
                    f"{(x['jd_near'] - x['jd']) * 24:+.3f}", f"{sun(x['jd'], lon, lat)[0]:.1f}",
                    f"{sun(x['jd_near'], lon, lat)[0]:.1f}", 'placeholder date; correction not valid' if x in placeholder else ''])
print(json.dumps(r, indent=1))
