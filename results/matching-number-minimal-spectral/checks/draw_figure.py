"""Draw data/figure.svg: Construction 9 for k = 3, n = 6, and the path P_6.

Usage: python3 -I checks/draw_figure.py [--check]
With --check, compare the drawing with the file and exit 1 if they differ.
The figure is an illustration. It is not part of the proof.
"""
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "figure.svg"
X, Y, LEAF = "#1f4e79", "#ffffff", "#b0b0b0"


def node(x, y, fill, label):
    return (f'<circle cx="{x}" cy="{y}" r="11" fill="{fill}" stroke="#222" stroke-width="1.5"/>'
            f'<text x="{x}" y="{y + 30}" font-size="13" text-anchor="middle">{label}</text>')


def edge(x1, y1, x2, y2, width=2, color="#222"):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'


def draw():
    parts = []
    # Row 1: T1 = path x1 x2 x3, subdivided; f = (1, 0, 1) is the least choice; 7 vertices.
    y0 = 60
    row = [("x", "x₁"), ("y", "y₁"), ("x", "x₂"), ("y", "y₂"), ("x", "x₃")]
    xs = [140 + 70 * i for i in range(5)]
    parts.append(edge(70, y0, xs[0], y0, color="#888"))
    parts.append(edge(xs[-1], y0, xs[-1] + 70, y0, color="#888"))
    for a, b in zip(xs, xs[1:]):
        parts.append(edge(a, y0, b, y0))
    parts.append(node(70, y0, LEAF, "leaf"))
    parts.append(node(xs[-1] + 70, y0, LEAF, "leaf"))
    for x, (kind, label) in zip(xs, row):
        parts.append(node(x, y0, X if kind == "x" else Y, label))
    parts.append('<text x="530" y="56" font-size="14">2d+f ∈ {3,4}: f₁, f₃ ≥ 1</text>')
    parts.append('<text x="530" y="74" font-size="14">order ≥ 3 + 2 + 2 = 7</text>')
    # Row 2: P_6 with a perfect matching (thick edges); order 6, matching number 3.
    y1 = 160
    xs = [105 + 70 * i for i in range(6)]
    for i, (a, b) in enumerate(zip(xs, xs[1:])):
        parts.append(edge(a, y1, b, y1, width=6 if i % 2 == 0 else 2,
                          color="#c0504d" if i % 2 == 0 else "#222"))
    for i, x in enumerate(xs):
        parts.append(node(x, y1, "#ffffff", f"v{chr(0x2081 + i)}"))
    parts.append('<text x="530" y="156" font-size="14">P₆: order 6,</text>')
    parts.append('<text x="530" y="174" font-size="14">matching number 3</text>')
    body = "".join(parts)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="760" height="210" '
            'viewBox="0 0 760 210" font-family="sans-serif">'
            '<rect width="760" height="210" fill="#ffffff"/>' + body + "</svg>\n")


svg = draw()
if "--check" in sys.argv:
    same = OUT.read_text() == svg
    print("data/figure.svg matches the drawing" if same else "data/figure.svg differs")
    sys.exit(0 if same else 1)
OUT.write_text(svg)
print(f"wrote {OUT}")
