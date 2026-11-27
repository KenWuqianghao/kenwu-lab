"""Download the raw APPLAUSE DR4 metadata and reproduce every number in the paper.
Usage: python3 -I checks/rerun.py [--cached] [--write]
  --cached  reuse work/raw (no download)
  --write   write data/expected.json (do not use to check)
Compares with data/expected.json and data/vatican_corrected.csv. Exits 1 on any mismatch."""
import sys, os, json, subprocess, re, collections, tempfile
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
sys.path.insert(0, here)
from analyze import rows
raw = os.path.join(root, 'work', 'raw')
if '--cached' not in sys.argv:
    raw = tempfile.mkdtemp(prefix='applause_', dir=os.environ.get('TMPDIR'))
    subprocess.run(['bash', os.path.join(here, 'fetch.sh'), raw], check=True)
    subprocess.run(['bash', os.path.join(here, 'fetch_ra.sh'), raw], check=True)
    subprocess.run(['bash', os.path.join(here, 'fetch_501.sh'), raw], check=True)
py = [sys.executable, '-I']
tmp = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
subprocess.run(py + [os.path.join(here, 'analyze.py'), raw, os.path.join(tmp, 'r.json')], check=True, capture_output=True)
r = json.load(open(os.path.join(tmp, 'r.json')))
cwd = os.getcwd(); os.chdir(tmp); os.makedirs('data', exist_ok=True)
subprocess.run(py + [os.path.join(here, 'hourangle2.py'), raw], check=True, capture_output=True)
h = json.load(open('data/hourangle2.json')); os.chdir(cwd)
csv_new = os.path.join(tmp, 'vatican_corrected.csv')
subprocess.run(py + [os.path.join(here, 'vatican.py'), raw, os.path.join(tmp, 'v.json'), csv_new], check=True, capture_output=True)
v = json.load(open(os.path.join(tmp, 'v.json')))
ex = subprocess.run(py + [os.path.join(here, 'explore_rules.py'), raw, '501,208,101,4,5'], check=True, capture_output=True, text=True).stdout
m501 = re.search(r'archive 501: n=(\d+).*D6 raw=([\d.]+) .*H_B=([\d.]+) .*B\(b,c\)=\((\d+),(\d+)\)', ex)
m208 = re.search(r'archive 208: n=(\d+).*D6 raw=([\d.]+)', ex)
mA = {a: re.search(r'archive ' + a + r': n=(\d+).*D6 raw=([\d.]+) H_A=([\d.]+) H_B=([\d.]+)', ex) for a in ('501', '4', '5')}
m101 = re.search(r'archive 101: n=(\d+).*D6 raw=([\d.]+) .*H_B=([\d.]+) .*B\(b,c\)=\((\d+),(\d+)\)', ex)
sites = collections.Counter((p['site_name'], p['site_longitude'], p['site_latitude']) for p in rows(os.path.join(raw, 'plate.xml')))
B = '208|Dr. Remeis-Observatory, Bamberg, Germany'; S = '205|Observatorio de Fisica Cosmica, San Miguel, Argentina'
got = {
 'n_plates_bamberg_swapped': sites[('Dr. Remeis-Observatory, Bamberg, Germany', '49.8845', '10.8881')],
 'n_plates_sanmiguel_swapped': sites[('Observatorio de Fisica Cosmica, San Miguel, Argentina', '-34.5567', '-58.7317')],
 'n_plates_muottas_swapped': sites[('Muottas Muragl, Switzerland', '46.5217', '9.9025')],
 'n_plates_schatzalp_swapped': sites[('Hotel Schatzalp, Davos, Switzerland', '46.8014', '9.8147')],
 'bamberg_n': r[B]['n'], 'bamberg_D6_true_site': round(r[B]['D6'], 4), 'bamberg_D6_shifted': round(r[B]['D6_shift'], 4),
 'bamberg_b': r[B]['b'], 'bamberg_c': r[B]['c'], 'bamberg_M': round(r[B]['M'], 2), 'bamberg_verdict': r[B]['verdict'],
 'bamberg_D6_recorded_site': float(m208[2]),
 'sanmiguel_n': r[S]['n'], 'sanmiguel_D6_true_site': round(r[S]['D6'], 4), 'sanmiguel_D6_shifted': round(r[S]['D6_shift'], 4),
 'sanmiguel_verdict': r[S]['verdict'],
 'injection_detected': r['INJECTION_detected'], 'injection_D6': round(r['INJECTION_101_plus2.5998h']['D6'], 4),
 'vatican_n': r['501|Castel Gandolfo, Italy']['n'], 'vatican_D6': round(r['501|Castel Gandolfo, Italy']['D6'], 4),
 'vatican_D0': round(r['501|Castel Gandolfo, Italy']['D0'], 4),
 'vatican_D6_HB': float(m501[3]), 'vatican_HB_b': int(m501[4]), 'vatican_HB_c': int(m501[5]),
 'vatican_frac_HA_APP_lt3': round(h['501']['frac_HA_APP_lt3'], 4), 'vatican_frac_HA_HB_lt3': round(h['501']['frac_HA_HB_lt3'], 4),
 'vatican_ha_b': h['501']['b_HBonly'], 'vatican_ha_c': h['501']['c_APPonly'], 'vatican_ha_p_lt_1e-50': h['501']['p_two_sided'] < 1e-50,
 'vatican_D6_HA': float(mA['501'][3]),
 'potsdam4_explore': [float(x) for x in mA['4'].groups()[1:]], 'potsdam5_explore': [float(x) for x in mA['5'].groups()[1:]],
 'control101_HB_b': int(m101[4]), 'control101_HB_c': int(m101[5]), 'control101_D6_HB': float(m101[3]),
 'control101_ha_diff': round(h['101']['diff'], 4),
 'control101_ha_b': h['101']['b_HBonly'], 'control101_ha_c': h['101']['c_APPonly'],
 'control101_ha_p_lt_1e-16': h['101']['p_two_sided'] < 1e-16,

 'potsdam4_D6': round(r['4|Potsdam-Telegrafenberg']['D6'], 4), 'potsdam5_D6': round(r['5|Potsdam-Telegrafenberg']['D6'], 4),
}
for k in ('n_timed', 'n_dated', 'first_date', 'last_date', 'n_day_dr4', 'n_near_vs_same_differ_by_a_day', 'n_night_dr4'):
    got['vatican_' + k] = v[k]
got['vatican_placeholder_exposure_id'] = v['placeholder'][0]['exposure_id'] if len(v['placeholder']) == 1 else None
for k in ('D6_near', 'D6_same', 'median_abs_correction_h', 'max_abs_correction_h', 'frac_dated_correction_gt_10min',
          'night_median_abs_correction_h', 'night_frac_correction_lt_1h', 'target_below_0_dr4', 'target_below_0_HB',
          'target_below_20_dr4', 'target_below_20_HB', 'night_target_below_0_dr4', 'night_target_below_0_HB',
          'perm_D6_mean', 'perm_D6_min', 'perm_target_below_20_mean', 'perm_target_below_20_min',
          'perm_HA_lt3_mean', 'perm_HA_lt3_max'):
    got['vatican_' + k] = round(v[k], 4)
got['blocks'] = {k: [v['n'], round(v['D6'], 4), round(v['D0'], 4), round(v['M'], 2), round(v['D6_placebo'], 3), v.get('verdict', '')]
                 for k, v in sorted(r.items()) if isinstance(v, dict) and not k.startswith('INJECTION')}
got['injection_M'] = round(r['INJECTION_101_plus2.5998h']['M'], 2)
csv_old = os.path.join(root, 'data', 'vatican_corrected.csv')
exp_path = os.path.join(root, 'data', 'expected.json')
if '--write' in sys.argv:
    json.dump(got, open(exp_path, 'w'), indent=1); print('wrote', exp_path)
    open(csv_old, 'w').write(open(csv_new).read()); print('wrote', csv_old); sys.exit(0)
exp = json.load(open(exp_path)); bad = 0
for k, v in exp.items():
    ok = got.get(k) == v; bad += not ok
    print(('OK  ' if ok else 'DIFF'), k, v, '' if ok else f'got {got.get(k)}')
same = open(csv_old).read() == open(csv_new).read(); bad += not same
print(('OK  ' if same else 'DIFF'), 'data/vatican_corrected.csv (544 rows) identical')
print(f'{len(exp) + 1 - bad} of {len(exp) + 1} checks match')
print('ALL MATCH' if not bad else f'{bad} MISMATCHES'); sys.exit(1 if bad else 0)
