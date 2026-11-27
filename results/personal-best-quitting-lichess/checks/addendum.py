"""Addendum A (PROTOCOL.md): period A (2013-2015) and period B (2016-02 to 2016-12) from the
2013-2016 build, and the difference test.

Usage: python addendum.py PLAYER_GAMES_2013_2016_PARQUET OUT_DIR
"""
import sys, os, json, subprocess, math

src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__))
periods = {"A": ("2013-01-01 00:00:00", "2015-12-30 23:59:59"),
           "B": ("2016-02-01 00:00:00", "2016-12-30 23:59:59")}
res = {}
for name, (lo, hi) in periods.items():
    path = os.path.join(outdir, f"period_{name}.json")
    subprocess.run([sys.executable, "-I", os.path.join(here, "analyze.py"), src, path], check=True,
                   env={**os.environ, "TS_FROM": lo, "TS_TO": hi}, stdout=subprocess.DEVNULL)
    res[name] = json.load(open(path))
a, b = res["A"]["primary"], res["B"]["primary"]
d = b["jump"] - a["jump"]
se = math.sqrt(a["se"] ** 2 + b["se"] ** 2)
res["difference_B_minus_A"] = {"diff": d, "se": se, "ci": [d - 1.96 * se, d + 1.96 * se], "z": d / se,
                               "salience_prediction_supported": bool(d - 1.96 * se > 0)}
json.dump(res, open(os.path.join(outdir, "addendum.json"), "w"), indent=1)
for name in ("A", "B"):
    p = res[name]["primary"]
    print(name, {k: p[k] for k in ("jump", "se", "ci", "left_limit", "n", "players", "decision")})
print("B-A", res["difference_B_minus_A"])
