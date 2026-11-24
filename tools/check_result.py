#!/usr/bin/env python3
"""Check that a result folder has the required files and a valid result.json.

Usage: check_result.py results/<slug> [...]
"""

import json
import re
import sys
from pathlib import Path

TIERS = ("Proved in Lean", "Computer-assisted", "Public data")
REQUIRED = {"slug": str, "title": str, "tier": str, "version": int, "date": str,
            "summary": str, "abstract": str, "keywords": list}
OPTIONAL = {"doi": (str, type(None)), "concept_doi": (str, type(None)),
            "zenodo_id": (int, type(None)), "doi_version": (int, type(None)),
            "related": list}
FORBIDDEN_LEAN = re.compile(r"\b(sorry|admit)\b|^\s*axiom\s|implemented_by|debug\.skipKernelTC", re.M)


def problems(folder):
    out = []
    meta_path = folder / "result.json"
    if not meta_path.is_file():
        return [f"{folder}: missing result.json"]
    try:
        meta = json.loads(meta_path.read_text())
    except json.JSONDecodeError as e:
        return [f"{meta_path}: invalid JSON ({e})"]
    for key, kind in REQUIRED.items():
        if not isinstance(meta.get(key), kind):
            out.append(f"{meta_path}: '{key}' must be {kind.__name__}")
    for key, kinds in OPTIONAL.items():
        if key in meta and not isinstance(meta[key], kinds):
            out.append(f"{meta_path}: '{key}' has the wrong type")
    unknown = set(meta) - set(REQUIRED) - set(OPTIONAL)
    if unknown:
        out.append(f"{meta_path}: unknown keys {sorted(unknown)}")
    if meta.get("slug") != folder.name:
        out.append(f"{meta_path}: slug must equal the folder name '{folder.name}'")
    if meta.get("tier") not in TIERS:
        out.append(f"{meta_path}: tier must be one of {TIERS}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(meta.get("date"))):
        out.append(f"{meta_path}: date must be YYYY-MM-DD")
    if isinstance(meta.get("version"), int) and meta["version"] < 1:
        out.append(f"{meta_path}: version must be 1 or more")
    for rel in ("README.md", "paper/paper.pdf", "paper/paper.tex", "checks/ci.sh"):
        if not (folder / rel).is_file():
            out.append(f"{folder}: missing {rel}")
    lean = sorted((folder / "lean").glob("*.lean")) if (folder / "lean").is_dir() else []
    if meta.get("tier") == "Proved in Lean" and not lean:
        out.append(f"{folder}: tier 'Proved in Lean' needs lean/*.lean")
    for f in lean:
        hit = FORBIDDEN_LEAN.search(f.read_text())
        if hit:
            out.append(f"{f}: forbidden token '{hit.group(0).strip()}'")
    big = [p for p in folder.rglob("*") if p.is_file() and p.stat().st_size > 20_000_000]
    if big:
        out.append(f"{folder}: files over 20 MB: {[str(p) for p in big]}")
    return out


if __name__ == "__main__":
    errors = [e for arg in sys.argv[1:] for e in problems(Path(arg))]
    print("\n".join(errors) if errors else f"ok: {len(sys.argv) - 1} result(s)")
    sys.exit(1 if errors else 0)
