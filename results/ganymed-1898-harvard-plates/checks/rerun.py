"""Reproduce every number from the public data: JPL Horizons predictions, DASCH DR7 cutouts, HDAP (Heidelberg) cutouts
and ATLAS stars are downloaded again into a new directory (about 6 min; 18 DASCH and 15 HDAP cutout requests, 3 s
apart), then the round-1 measurement, the round-2 measurement, the astrometry (two methods and 6 variants), the shapes,
the round-3 (Hektor, HDAP) measurement and the 1901-08-23 motion check run, and the results are compared with
data/expected.json. It also checks that each prediction is the Horizons row at the DASCH midpoint (0 min offset).
Usage: python3 checks/rerun.py [--data DIR]   (--data reuses a directory from an earlier run). Exit 1 on a mismatch."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
root = Path(__file__).resolve().parent.parent; src = root / "src"
if "--data" in sys.argv:
    data = Path(sys.argv[sys.argv.index("--data") + 1])
else:
    data = Path(tempfile.mkdtemp(prefix="precovery_", dir=os.environ.get("TMPDIR")))
env = dict(os.environ, PRECOVERY_DATA=str(data), PYTHONWARNINGS="ignore")
run = lambda *a: subprocess.run([sys.executable, *map(str, a)], env=env, check=True, capture_output=True, text=True).stdout
print("data dir:", data)
run(src / "predict.py", "1"); run(src / "predict.py", "2")
run(src / "fetch.py", "1"); run(src / "fetch.py", "2")
run(src / "measure.py"); run(src / "measure2.py", data / "predictions2.json", data / "results2.json")
run(src / "astrometry.py", "i21050", "i21576", "i21780", "ac00115", "i22152")
run(src / "shapes.py", "i21050", "i21576", "i21780", "ac00115", "i22152", "ac00044")
run(src / "hdap.py", "predict"); run(src / "hdap.py", "fetch"); run(src / "hdap.py", "measure"); run(src / "motion_check.py")
r1 = json.load(open(data / "results.json")); r2 = json.load(open(data / "results2.json")); ast = json.load(open(data / "astrometry.json"))
got = {}
for p in r1["plates"]:
    got[f"r1.{p['plate']}.S"] = round(p["S"], 1); got[f"r1.{p['plate']}.pass"] = p["pass"]; got[f"r1.{p['plate']}.p0"] = round(p["p0"], 3)
for o, v in r1["objects"].items():
    got[f"r1.{o}.k_pass"] = v["k_pass"]; got[f"r1.{o}.P_null"] = float(f"{v['P_null']:.3g}"); got[f"r1.{o}.detected"] = v["detected"]
for p in r2["plates"]:
    got[f"r2.{p['plate']}.measurable"] = p["measurable"]
    if p["measurable"]:
        got[f"r2.{p['plate']}.z5"] = round(p["z5"], 1); got[f"r2.{p['plate']}.p"] = round(p["p"], 4)
got["r2.p_comb"] = float(f"{r2['summary']['p_comb']:.3g}"); got["r2.detected"] = r2["summary"]["detected"]
for meth, plates in ast.items():
    for pid, a in plates.items():
        k = f"ast.{meth}.{pid}"
        got[f"{k}.ra_deg"] = round(a["ra_deg"], 5); got[f"{k}.dec_deg"] = round(a["dec_deg"], 5); got[f"{k}.n_ref"] = a["n_ref"]
        for q in ("o_c_ra_cosdec_arcsec", "o_c_dec_arcsec", "o_c_total_arcsec", "along_track_arcsec", "time_offset_min"):
            got[f"{k}.{q}"] = round(a[q], 2 if q != "time_offset_min" else 1)
# secondary numbers quoted in RESULT.md
var = json.load(open(data / "astrometry_variants.json"))
for pid in ast["region"]:
    vals = [v[pid] for v in var.values()]
    got[f"astvar.{pid}.o_c_min_arcsec"] = round(min(vals), 2); got[f"astvar.{pid}.o_c_max_arcsec"] = round(max(vals), 2)
for pid, o in json.load(open(data / "shapes.json")).items():
    got[f"shape.{pid}.source_pa_deg"] = round(o["source"]["pa_deg"]); got[f"shape.{pid}.source_length_arcsec"] = round(o["source"]["length_arcsec"])
    got[f"shape.{pid}.stars_n"] = o["stars_n"]; got[f"shape.{pid}.trail_pa_deg"] = round(o["trail_pred_pa_deg"]); got[f"shape.{pid}.trail_length_arcsec"] = round(o["trail_pred_length_arcsec"])
    if o["stars_n"]:
        got[f"shape.{pid}.stars_pa_deg"] = round(o["stars_pa_mean_deg"]); got[f"shape.{pid}.stars_length_arcsec"] = round(o["stars_length_median_arcsec"])
sys.path.insert(0, str(src)); os.environ["PRECOVERY_DATA"] = str(data)
from measure import poisson_binomial_tail
gp = [p for p in r1["plates"] if p["object"] == "Ganymed"]
got["r1.Ganymed.P_null_p0_floor_1_300"] = float(f"{poisson_binomial_tail([max(p['p0'], 1 / 300) for p in gp], r1['objects']['Ganymed']['k_pass']):.3g}")
import math
pos = [(a["ra_deg"], a["dec_deg"]) for a in ast["region"].values()]
sep = lambda a, b: math.degrees(math.acos(min(1, math.sin(math.radians(a[1])) * math.sin(math.radians(b[1])) + math.cos(math.radians(a[1])) * math.cos(math.radians(b[1])) * math.cos(math.radians(a[0] - b[0])))))
got["ast.max_separation_deg"] = round(max(sep(a, b) for a in pos for b in pos), 1)
# every prediction must be the Horizons row at the DASCH midpoint itself (VERIFY.md round 1, issue 1)
from astropy.time import Time
for f in ("predictions.json", "predictions2.json"):
    for p in json.load(open(data / f)):
        dmin = min(abs(t["jd"] - Time(p["mid"] + ":00").jd) for t in p["track"]) * 1440
        got[f"pred.{p['plate']}.midpoint_row_offset_min"] = round(dmin, 2)
r3 = json.load(open(data / "hdap" / "results.json"))
for p in r3["plates"]:
    got[f"r3.{p['plate']}.measurable"] = p["measurable"]
    if p["measurable"]:
        got[f"r3.{p['plate']}.S"] = round(p["S"], 2); got[f"r3.{p['plate']}.p"] = round(p["p"], 4)
for k, v in r3["summary"].items():
    got[f"r3.{k}.p_comb"] = float(f"{v['p_comb']:.3g}"); got[f"r3.{k}.n_p_lt_0.01"] = v["n_p_lt_0.01"]; got[f"r3.{k}.detected"] = v["detected"]
for p in json.load(open(data / "hdap" / "predictions.json")):  # no Horizons row dropped: 2-min steps throughout
    tj = [t["jd"] for t in p["track"]]
    got[f"pred3.{p['plate']}.max_step_min"] = round(max(b - a for a, b in zip(tj, tj[1:])) * 1440, 2)
for k, v in json.load(open(data / "hdap" / "motion_check.json")).items():
    if k == "separation_arcsec":
        got["motion.separation_arcsec"] = round(v)
    elif v is not None:
        got[f"motion.{k}.z"] = round(v["z"], 2); got[f"motion.{k}.frac_random_ge"] = round(v["frac_random_ge"], 4)
exp_file = root / "data" / "expected.json"
if "--write-expected" in sys.argv:
    exp_file.write_text(json.dumps(got, indent=1)); print("wrote", exp_file); sys.exit(0)
exp = json.load(open(exp_file)); bad = 0
for k, v in exp.items():
    g = got.get(k)
    pval = k.rsplit(".", 1)[-1] in ("p", "p0", "p_comb", "P_null", "frac_random_ge") or k.startswith("r1.Ganymed.P_null")
    tol = 0.0 if pval else 2e-5 if (".ra_deg" in k or ".dec_deg" in k) else 0.051
    ok = g == v if not isinstance(v, float) else (g is not None and abs(g - v) <= max(tol, abs(v) * 0.02))
    print(("OK  " if ok else "DIFF"), k, v, "" if ok else f"got {g}"); bad += not ok
print(f"{len(exp) - bad} of {len(exp)} checks match"); sys.exit(1 if bad else 0)
