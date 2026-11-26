#!/usr/bin/env python3
"""Check that a result folder has the required files and a valid result.json.

Usage: check_result.py results/<slug> [...]
"""

import json
import re
import sys
from pathlib import Path

from lean_audit import strip_comments

TIERS = ("Proved in Lean", "Computer-assisted", "Public data")
REQUIRED = {"slug": str, "title": str, "tier": str, "version": int, "date": str,
            "summary": str, "abstract": str, "keywords": list}
OPTIONAL = {"doi": (str, type(None)), "concept_doi": (str, type(None)),
            "zenodo_id": (int, type(None)), "doi_version": (int, type(None)),
            "related": list}
FORBIDDEN_LEAN = re.compile(r"\b(sorry|admit)\b|^\s*axiom\s|implemented_by|debug\.skipKernelTC", re.M)


STANDARD_AXIOMS = {"propext", "Quot.sound", "Classical.choice"}
COMPARATOR_KEYS = {"challenge_module", "solution_module", "theorem_names", "permitted_axioms"}


def imported_modules(text):
    """Module names in the Lean header, with comments and line breaks ignored.

    Each `import` takes one module name, optionally after `all`. The header ends at the
    first token that is not `module`, an import modifier, or an import."""
    tokens, mods, i = strip_comments(text).split(), [], 0
    while i < len(tokens):
        if tokens[i] in {"module", "public", "private", "meta"}:
            i += 1
        elif tokens[i] == "import":
            i += 2 if i + 1 < len(tokens) and tokens[i + 1] == "all" else 1
            if i < len(tokens):
                mods.append(tokens[i])
            i += 1
        else:
            break
    return mods


def lean_problems(folder, lean):
    """A Lean result is one proof file plus the challenge that CI compares it with.

    lean/Challenge.lean states the main theorems with `sorry` proofs and repeats every
    definition they use. lean/comparator.json names the theorems for `lake comparator`."""
    if not lean:
        return []
    out = []
    challenge = folder / "lean" / "Challenge.lean"
    solutions = [f for f in lean if f.name != "Challenge.lean"]
    if not challenge.is_file():
        out.append(f"{folder}: missing lean/Challenge.lean")
    elif set(imported_modules(challenge.read_text())) - {"Mathlib"}:
        out.append(f"{challenge}: may import only Mathlib")
    if len(solutions) != 1:
        out.append(f"{folder}: lean/ must hold exactly one proof file besides Challenge.lean")
    for f in solutions:
        hit = FORBIDDEN_LEAN.search(f.read_text())
        if hit:
            out.append(f"{f}: forbidden token '{hit.group(0).strip()}'")
    config = folder / "lean" / "comparator.json"
    try:
        cfg = json.loads(config.read_text())
    except (OSError, json.JSONDecodeError) as e:
        return out + [f"{config}: missing or invalid ({e})"]
    if set(cfg) - COMPARATOR_KEYS - {"definition_names"} or not COMPARATOR_KEYS <= set(cfg):
        out.append(f"{config}: keys must be {sorted(COMPARATOR_KEYS)} (+ optional definition_names)")
    if cfg.get("challenge_module") != "Challenge" or cfg.get("solution_module") != "Solution":
        out.append(f"{config}: modules must be 'Challenge' and 'Solution'")
    if not cfg.get("theorem_names"):
        out.append(f"{config}: theorem_names must not be empty")
    if not set(cfg.get("permitted_axioms", [])) <= STANDARD_AXIOMS:
        out.append(f"{config}: permitted_axioms must be a subset of {sorted(STANDARD_AXIOMS)}")
    return out


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
    out += lean_problems(folder, lean)
    big = [p for p in folder.rglob("*") if p.is_file() and p.stat().st_size > 20_000_000]
    if big:
        out.append(f"{folder}: files over 20 MB: {[str(p) for p in big]}")
    return out


if __name__ == "__main__":
    errors = [e for arg in sys.argv[1:] for e in problems(Path(arg))]
    print("\n".join(errors) if errors else f"ok: {len(sys.argv) - 1} result(s)")
    sys.exit(1 if errors else 0)
