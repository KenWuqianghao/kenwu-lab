"""Reproduce every number of the paper from the public data and compare it with data/expected.json.
Into a new directory, the script downloads again the DASCH DR7 cutouts of the 6 registered plates (b27808 returns
HTTP 422), the ATLAS-REFCAT2 stars, the 6 control-plate cutouts and the plate lists for the controls. It then runs:
  src/measure.py, src/decide.py   the registered test (S, p0, pass, P_null, decision)
  src/controls.py                 the other-date control plates (max z within 5")
  src/posthoc.py                  centroid, shape and track profile of the source (after the decision)
  src/horizons_check.py           fresh JPL Horizons positions vs the fixed predictions (data/predictions.json)
  src/skybot.py                   known asteroids near each position (IMCCE SkyBoT)
The plate list (data/coverage.json) and the predictions (data/predictions.json) are fixed registered inputs.
Usage: python3 checks/rerun.py [--data DIR] [--write-expected]. Exit 1 on a mismatch."""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
root = Path(__file__).resolve().parent.parent; src = root / "src"
if "--data" in sys.argv:
    data = Path(sys.argv[sys.argv.index("--data") + 1]); data.mkdir(parents=True, exist_ok=True)
else:
    data = Path(tempfile.mkdtemp(prefix="ivar_", dir=os.environ.get("TMPDIR")))
env = dict(os.environ, PRECOVERY_DATA=str(data), PYTHONWARNINGS="ignore")
def run(*a):
    print("run", *[Path(x).name if str(x).startswith(str(root)) else x for x in a], flush=True)
    return subprocess.run([sys.executable, "-I", *map(str, a)], env=env, check=True, capture_output=True, text=True).stdout
print("data dir:", data)
shutil.copy(root / "data" / "predictions.json", data / "predictions.json")
run(src / "fetch.py"); run(src / "measure.py"); run(src / "decide.py")
run(src / "controls.py")
run(src / "posthoc.py", "b27907", "b28342", "b28520", "b28598")
run(src / "horizons_check.py")
skybot_ok = True
try:
    run(src / "skybot.py")
except subprocess.CalledProcessError as e:
    skybot_ok = False; print("SkyBoT service failed; its values are not checked:", e.stderr.strip().splitlines()[-1:])
J = lambda n: json.load(open(data / n))
got = {}
for r in J("results.json")["plates"]:
    k = f"plate.{r['plate']}"
    got[f"{k}.S"] = round(r["S"], 1); got[f"{k}.pass"] = r["pass"]; got[f"{k}.p0"] = round(r["p0"], 4)
    got[f"{k}.peak_from_mid_arcsec"] = round(r["peak_from_mid_arcsec"], 1); got[f"{k}.fit"] = r["fit"].get("kind")
log = [json.loads(l) for l in open(data / "cutouts" / "log.jsonl")]
got["plate.b27808.covered"] = any(e["ok"] for e in log if e["payload"]["plate_id"] == "b27808")
for s, d in J("decision.json").items():
    got[f"set.{s}.n"] = d["n"]; got[f"set.{s}.k_pass"] = d["k_pass"]; got[f"set.{s}.P_null"] = float(f"{d['P_null']:.3g}")
    got[f"set.{s}.detected"] = d["detected"]; got[f"set.{s}.earliest_pass"] = d["earliest_pass"]
# Robustness of P_null for set E (verification stage, not registered): 95% upper Clopper-Pearson limit of each p0
# (300 offsets), and P_null without b27907.
sys.path.insert(0, str(src)); from measure import poisson_binomial_tail, NCTRL
from scipy.stats import beta
E = [r for r in J("results.json")["plates"] if r["mid"][:4] in ("1901", "1906")]
cp = [float(beta.ppf(0.95, round(r["p0"] * NCTRL) + 1, NCTRL - round(r["p0"] * NCTRL))) for r in E]
got["set.E.p0_cp95"] = [round(x, 3) for x in cp]
got["set.E.P_null_cp95"] = float(f"{poisson_binomial_tail(cp, sum(r['pass'] for r in E)):.3g}")
E3 = [r for r in E if r["plate"] != "b27907"]
got["set.E_without_b27907.P_null"] = float(f"{poisson_binomial_tail([r['p0'] for r in E3], sum(r['pass'] for r in E3)):.3g}")
import math
pos = [(p["ra"], p["dec"]) for p in json.load(open(data / "predictions.json")) if p["plate"] in ("b27907", "b28342", "b28520", "b28598")]
gc = lambda a, b: math.degrees(math.acos(min(1, math.sin(math.radians(a[1])) * math.sin(math.radians(b[1])) + math.cos(math.radians(a[1])) * math.cos(math.radians(b[1])) * math.cos(math.radians(a[0] - b[0])))))
got["max_separation_1901_deg"] = round(max(gc(a, b) for a in pos for b in pos), 1)
for pl, e in J("controls.json").items():
    got[f"ctrl.{pl}.target_z5"] = round(e["target"]["z5"], 2)
    got[f"ctrl.{pl}.controls"] = [c["plate"] for c in e["controls"]]
    for c in e["controls"]:
        got[f"ctrl.{pl}.{c['plate']}.z5"] = round(c["z5"], 2)
for pl, e in J("posthoc.json").items():
    k = f"post.{pl}"
    got[f"{k}.peak_z"] = e["r40"]["peak_z"]; got[f"{k}.centroid_offset_arcsec"] = e["r10"]["centroid_offset_arcsec"]
    got[f"{k}.track_hours_z_ge_10"] = e["track_hours_z_ge_10"]; got[f"{k}.nearest_star_brighter_16_arcsec"] = e["nearest_star_brighter_16_arcsec"]
    got[f"{k}.mag_estimate"] = e.get("mag_estimate"); got[f"{k}.mag_rms"] = e.get("mag_rms")
    for q in ("major_extent_arcsec", "axis_ratio", "angle_to_motion_deg", "predicted_trail_arcsec"):
        got[f"{k}.{q}"] = e["shape"][q]
for pl, e in J("horizons_check.json").items():
    k = f"hz.{pl}"
    got[f"{k}.site_offset_arcsec"] = e["site"]["offset_arcsec"]; got[f"{k}.geocentre_offset_arcsec"] = e["geocentre"]["offset_arcsec"]
    got[f"{k}.other_site_offset_arcsec"] = e["other_site"]["offset_arcsec"]; got[f"{k}.V"] = round(e["site"]["V"], 2)
    got[f"{k}.solution"] = e["solution"]
if skybot_ok:
    for pl, e in J("skybot.json").items():
        near = [o for o in e["objects"] if o["d_arcsec"] <= 180]
        got[f"skybot.{pl}.within_180"] = [o["name"] for o in near]
        got[f"skybot.{pl}.ivar_d_arcsec"] = next((o["d_arcsec"] for o in near if o["num"] == "1627"), None)
exp_f = root / "data" / "expected.json"
if "--write-expected" in sys.argv:
    if not skybot_ok: sys.exit("SkyBoT failed: expected values not written")
    exp_f.write_text(json.dumps(got, indent=1) + "\n"); print("wrote", exp_f, len(got), "values"); sys.exit(0)
exp = json.load(open(exp_f))
def same(k, v, g):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not isinstance(g, (int, float)) or isinstance(g, bool):
        return v == g
    if k.startswith("hz.") and k.endswith("_arcsec"): return abs(v - g) <= 0.1
    if k.endswith(".p0") or k.endswith("P_null"): return abs(v - g) <= 0.02 * abs(v) + 1e-12
    return abs(v - g) <= max(0.15, 0.02 * abs(v))
bad = []; n = 0
for k, v in exp.items():
    if k.startswith("skybot.") and not skybot_ok: continue
    n += 1
    if not same(k, v, got.get(k)): bad.append((k, v, got.get(k)))
for k, v, g in bad: print("MISMATCH", k, "expected", v, "got", g)
print(f"{n - len(bad)} of {n} checks match" + ("" if skybot_ok else f" ({sum(k.startswith('skybot.') for k in exp)} SkyBoT values skipped)"))
sys.exit(1 if bad else 0)
