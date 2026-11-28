"""Download one cutout per plate, centred on the predicted midpoint position, and the ATLAS reference stars
within 700 arcsec. Run only after PROTOCOL.md and data/predictions.json are committed."""
import os, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import dasch
D = Path(os.environ["PRECOVERY_DATA"]) if os.environ.get("PRECOVERY_DATA") else Path(__file__).resolve().parent.parent / "data"
preds = json.load(open(D / ("predictions2.json" if len(sys.argv) > 1 and sys.argv[1] == "2" else "predictions.json")))
cat = json.load(open(D / "refcat.json")) if (D / "refcat.json").exists() else {}
for p in preds:
    try:
        f = dasch.cutout(p["plate"], p["solnum"], p["ra"], p["dec"]); print("cutout", f.name)
    except RuntimeError as ex:  # 422: the plate does not cover the predicted position
        print("no cutout", p["plate"], ex); continue
    if p["plate"] not in cat:
        cat[p["plate"]] = dasch.querycat(p["ra"], p["dec"], 700)
        (D / "refcat.json").write_text(json.dumps(cat)); print("refcat", p["plate"], len(cat[p["plate"]]))
