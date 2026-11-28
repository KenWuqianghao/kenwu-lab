"""Download the raw data, recompute every number, compare with data/expected.json.
Usage: python -I checks/rerun.py   (needs the packages of checks/requirements.txt, curl and network access)"""
import json, os, subprocess, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
tmp = tempfile.mkdtemp(prefix='rerun_', dir=os.environ.get('TMPDIR'))
raw = os.path.join(tmp, 'raw')
subprocess.run(['bash', os.path.join(here, 'fetch.sh'), raw], check=True)
for s in ('analysis', 'exploratory', 'posthoc'):
    subprocess.run([sys.executable, '-I', os.path.join(here, s + '.py'), raw, os.path.join(tmp, s + '.json')],
                   check=True, stdout=subprocess.DEVNULL)
got = {s: json.load(open(os.path.join(tmp, s + '.json'))) for s in ('analysis', 'exploratory', 'posthoc')}
exp = json.load(open(os.path.join(root, 'data', 'expected.json')))
n = bad = 0
def cmp(a, b, path):
    global n, bad
    if isinstance(a, dict):
        for k in a: cmp(a[k], b.get(k), path + '.' + k)
    elif isinstance(a, list):
        for i, x in enumerate(a): cmp(x, b[i], f'{path}[{i}]')
    else:
        n += 1
        ok = (abs(a - b) <= 1e-6 * max(1, abs(a))) if isinstance(a, (int, float)) and not isinstance(a, bool) else a == b
        if not ok: bad += 1; print('MISMATCH', path, a, b)
cmp(exp, got, '')
print(f'{n - bad}/{n} values match'); sys.exit(1 if bad else 0)
