#!/usr/bin/env python3
"""Fail if a Lean file's declarations depend on an axiom outside Lean's standard three.

  python3 tools/lean_audit.py <file.lean | dir> ...

Each file is compiled in the shared workspace (lean/) with an appended command that
collects the axioms of every declaration the file defines. Exit 1 when any of these
is true: the file does not compile, a declaration uses sorryAx or a project axiom,
or the source uses debug.skipKernelTC, #exit, an axiom declaration or a
_native name. native_decide axioms pass with a warning: a
paper that uses native_decide must say so. Adapted from ProofAudit.lean in
1337isnot1337/solved-conjectures (MIT).
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent / "lean"
CHALLENGE = "Challenge.lean"  # sorry by design; lake comparator checks the proof against it

AUDIT = r"""

open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let std : List Name := [`propext, `Classical.choice, `Quot.sound]
  let native : List Name := [`Lean.ofReduceBool, `Lean.trustCompiler]
  let mut n : Nat := 0
  for (c, _) in env.constants.map₂.toList do
    n := n + 1
    for a in (← collectAxioms c) do
      if native.contains a || (a.toString.splitOn "._native.native_decide.ax_").length > 1 then
        logInfo m!"LEAN_AUDIT native {c} {a}"
      else unless std.contains a do
        logInfo m!"LEAN_AUDIT bad {c} {a}"
  logInfo m!"LEAN_AUDIT checked {n}"
"""


# Source text that can hide a project axiom from the audit or stop the audit early.
# Genuine native_decide axioms get generated names, so source never needs `_native`.
FORBIDDEN = {
    "sets debug.skipKernelTC": r"skipKernelTC",
    "uses #exit": r"#exit\b",
    "declares an axiom": r"^\s*(@\[[^\]]*\]\s*)?((private|protected|noncomputable|unsafe|partial|public)\s+)*axiom\s",
    "names a _native declaration": r"_native\b",
}
HEADER = re.compile(r"^\s*(module\b|((public|private|meta)\s+)*import\s)")


def strip_comments(text):
    """Replace Lean comments (nested /- -/ blocks and -- lines) with spaces; keep newlines."""
    out, i, depth = [], 0, 0
    while i < len(text):
        two = text[i:i + 2]
        if two == "/-":
            depth, i = depth + 1, i + 2
            out.append("  ")
        elif depth and two == "-/":
            depth, i = depth - 1, i + 2
            out.append("  ")
        elif not depth and two == "--":
            j = text.find("\n", i)
            j = len(text) if j < 0 else j
            out.append(" " * (j - i))
            i = j
        else:
            out.append(text[i] if text[i] == "\n" or not depth else " ")
            i += 1
    return "".join(out)


def header_end(text):
    """Character offset just after the last `module`/`import` line of the header.

    Comments are ignored. The offset is in `text` itself, because strip_comments keeps
    every character position."""
    stripped, end, pos = strip_comments(text), 0, 0
    for line in stripped.split("\n"):
        if line.strip():
            if not HEADER.match(line):
                break
            end = pos + len(line.rstrip())
        pos += len(line) + 1
    return end

def audit(path):
    text = path.read_text()
    for reason, pattern in FORBIDDEN.items():
        if re.search(pattern, text, re.MULTILINE):
            return False, reason
    cut = header_end(text)
    with tempfile.NamedTemporaryFile("w", suffix=".lean", dir=WORKSPACE, delete=False) as f:
        f.write(text[:cut] + "\nimport Lean\n" + text[cut:] + AUDIT)
        tmp = Path(f.name)
    try:
        proc = subprocess.run(["lake", "env", "lean", str(tmp)], cwd=WORKSPACE,
                              capture_output=True, text=True)
    finally:
        tmp.unlink(missing_ok=True)
    out = proc.stdout + proc.stderr
    lines = re.findall(r"LEAN_AUDIT (\w+) ?(.*)", out)
    bad = sorted({rest for kind, rest in lines if kind == "bad"})
    native = sorted({rest.split()[-1] for kind, rest in lines if kind == "native"})
    checked = [rest for kind, rest in lines if kind == "checked"]
    if proc.returncode != 0 or not checked:
        return False, "does not compile:\n" + out[-3000:]
    if bad:
        return False, "non-standard axioms:\n  " + "\n  ".join(bad[:40])
    note = f"{checked[0]} declarations, no project axioms"
    if native:
        note += f"; WARNING native_decide axioms {', '.join(native)}: the paper must say so"
    return True, note


def main(args):
    files = []
    for a in map(Path, args):
        files += sorted(p for p in a.rglob("*.lean")
                        if ".lake" not in p.parts and p.name != CHALLENGE) if a.is_dir() else [a]
    if not files:
        print("lean-audit: no .lean files", file=sys.stderr)
        return 2
    ok_all = True
    for p in files:
        ok, msg = audit(p.resolve())
        ok_all &= ok
        print(f"{'PASS' if ok else 'FAIL'} {p}: {msg}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
