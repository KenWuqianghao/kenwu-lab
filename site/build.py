#!/usr/bin/env python3
"""Build the lab notebook site from entries/*.md into _site/.

An entry is Markdown with a front matter block:

---
title: The longest one-swipe ride on the New York subway
date: 2026-11-23
tags: transit, optimization
status: Audited
summary: One sentence for the index.
image: assets/allstations-longride/route.png
---
"""

import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
SITE = {"name": "Ken Wu Lab", "tagline": "Small findings from AI-assisted research. Not reviewed by experts."}
STATUSES = ("Published", "Proved", "Audited", "Checked", "Not audited")
RESULTS = ROOT.parent / "results"
REPO = "https://github.com/KenWuqianghao/kenwu-lab"
URL = "https://kenwu-lab.wooqianghao.workers.dev"
CARD = "assets/card.png"


def parse(path):
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        sys.exit(f"{path}: missing front matter")
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines() if line.strip())
    for key in ("title", "date", "tags", "status", "summary"):
        if key not in meta:
            sys.exit(f"{path}: missing {key}")
    if meta["status"] not in STATUSES:
        sys.exit(f"{path}: status must be one of {STATUSES}")
    meta["slug"] = path.stem
    meta["tags"] = [t.strip() for t in meta["tags"].split(",")]
    meta["body"] = m.group(2)
    return meta


def markdown(text):
    return subprocess.run(["pandoc", "-f", "markdown", "-t", "html5", "--mathml"],
                          input=text, capture_output=True, text=True, check=True).stdout


CSS = """
:root{--bg:#fbfaf7;--fg:#1c1b19;--muted:#6b665d;--line:#e4e0d8;--accent:#9a3412;--chip:#f1ede5}
@media (prefers-color-scheme:dark){:root{--bg:#141311;--fg:#ece8e1;--muted:#a19a8e;--line:#2c2a26;--accent:#fb923c;--chip:#211f1b}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.6 Charter,"Iowan Old Style",Georgia,serif}
main,header,footer{max-width:720px;margin:0 auto;padding:0 16px}
header{padding-top:48px;padding-bottom:8px}
header a{color:inherit;text-decoration:none}
.site{font:600 15px/1 ui-sans-serif,system-ui,sans-serif;letter-spacing:.02em}
.tagline{color:var(--muted);font-size:15px;margin:6px 0 0}
h1{font-size:30px;line-height:1.2;margin:32px 0 8px}
h2{font-size:21px;margin:36px 0 8px}
a{color:var(--accent)}
.meta{font:13px/1.4 ui-sans-serif,system-ui,sans-serif;color:var(--muted);display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.chip{background:var(--chip);border-radius:4px;padding:2px 7px}
.status{border:1px solid var(--line);border-radius:4px;padding:1px 7px}
ul.entries{list-style:none;padding:0;margin:24px 0}
ul.entries li{border-top:1px solid var(--line);padding:18px 0}
ul.entries a.t{font-size:19px;font-weight:600;text-decoration:none;color:var(--fg)}
ul.entries a.t:hover{color:var(--accent)}
ul.entries p{margin:4px 0 8px;color:var(--muted)}
img,video{max-width:100%;height:auto;border-radius:4px}
img[src$=".svg"]{background:#fff;padding:8px}
figure{margin:24px 0}figcaption{font-size:14px;color:var(--muted)}
pre,code{font:14px/1.5 ui-monospace,Menlo,monospace}
pre{background:var(--chip);padding:12px;overflow-x:auto;border-radius:4px}
table{border-collapse:collapse;font-size:15px;display:block;overflow-x:auto}
td,th{border-bottom:1px solid var(--line);padding:6px 10px;text-align:left}
footer{color:var(--muted);font-size:14px;padding-top:48px;padding-bottom:48px}
math{font-size:1.05em}
"""


def social_tags(title, description, path, image):
    """Open Graph tags for link previews; X reads them with twitter:card. path and image are site-relative."""
    tags = {"og:type": "article" if path else "website", "og:site_name": SITE["name"], "og:title": title,
            "og:description": description, "og:url": f"{URL}/{path}", "og:image": f"{URL}/{image}"}
    out = [f'<meta name="description" content="{html.escape(description)}">',
           '<meta name="twitter:card" content="summary_large_image">']
    out += [f'<meta property="{k}" content="{html.escape(v)}">' for k, v in tags.items()]
    return "\n".join(out)


def page(title, body, depth, description, path, image=CARD):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
{social_tags(title, description, path, image)}
<link rel="stylesheet" href="{up}style.css">
</head><body>
<header><a class="site" href="{up}index.html">{SITE['name']}</a>
<p class="tagline">{SITE['tagline']}</p></header>
<main>{body}</main>
<footer>The computations and the text were produced by AI models (from Anthropic and OpenAI) under the author's direction.
Corrections are welcome.<br>
Status: <b>Published</b> has a DOI. <b>Audited</b> means an independent audit checked the main number. <b>Checked</b> means a validator or a rerun confirmed it. <b>Not audited</b> means only the project's own checks ran. A paper without a DOI is <b>Not archived</b> yet.</footer>
</body></html>
"""


def meta_line(e, depth=0):
    tags = "".join(f'<span class="chip">{html.escape(t)}</span>' for t in e["tags"])
    return f'<div class="meta"><span>{e["date"]}</span><span class="status">{e["status"]}</span>{tags}</div>'


def load_results():
    papers = []
    for meta_path in sorted(RESULTS.glob("*/result.json")):
        r = json.loads(meta_path.read_text())
        r["folder"] = meta_path.parent
        r["status"] = "Published" if r.get("doi") else "Not archived"
        r["tags"] = [r["tier"]]
        papers.append(r)
    return sorted(papers, key=lambda r: (r["date"], r["title"]), reverse=True)


def paper_page(r):
    """Render a result README; local links go to the PDF copy or to the folder on GitHub."""
    readme = (r["folder"] / "README.md").read_text()
    readme = re.sub(r"\A#\s.*\n", "", readme)

    def link(m):
        target = m.group(2)
        if re.match(r"[a-z]+:|#", target):
            return m.group(0)
        if target == "paper/paper.pdf":
            return f"{m.group(1)}(paper.pdf)"
        return f"{m.group(1)}({REPO}/blob/main/results/{r['slug']}/{target})"

    readme = re.sub(r"(!?\[[^\]]*\])\(([^)\s]+)\)", link, readme)
    d = OUT / "papers" / r["slug"]
    d.mkdir(parents=True)
    shutil.copy(r["folder"] / "paper/paper.pdf", d / "paper.pdf")
    doi = f'<p>DOI: <a href="https://doi.org/{r["doi"]}">{r["doi"]}</a></p>' if r.get("doi") else ""
    body = f"<h1>{html.escape(r['title'])}</h1>{meta_line(r)}{doi}" + markdown(readme)
    (d / "index.html").write_text(page(r["title"], body, 2, r["summary"], f"papers/{r['slug']}/"))


def build():
    papers = load_results()
    entries = sorted((parse(p) for p in (ROOT / "entries").glob("*.md")),
                     key=lambda e: (e["date"], e["title"]), reverse=True)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "style.css").write_text(CSS)
    if (ROOT / "assets").exists():
        shutil.copytree(ROOT / "assets", OUT / "assets")
    for e in entries:
        body = (f"<h1>{html.escape(e['title'])}</h1>{meta_line(e)}"
                + markdown(e["body"].replace("](assets/", "](../assets/").replace('src="assets/', 'src="../assets/')))
        d = OUT / e["slug"]
        d.mkdir()
        image = e["image"] if e.get("image", "").endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")) else CARD
        (d / "index.html").write_text(page(e["title"], body, 1, e["summary"], f"{e['slug']}/", image))
    for r in papers:
        paper_page(r)

    def items(rows, prefix):
        return "".join(f'<li><a class="t" href="{prefix}{x["slug"]}/">{html.escape(x["title"])}</a>'
                       f'<p>{html.escape(x["summary"])}</p>{meta_line(x)}</li>' for x in rows)

    index = ""
    if papers:
        index += f'<h2>Papers</h2><ul class="entries">{items(papers, "papers/")}</ul><h2>Notes</h2>'
    index += f'<ul class="entries">{items(entries, "")}</ul>'
    (OUT / "index.html").write_text(page(SITE["name"], index, 0, SITE["tagline"], ""))
    for e in entries:
        for ref in re.findall(r"\]\((assets/[^)\s]+)", e["body"]) + re.findall(r'src="(assets/[^"]+)"', e["body"]) + [e.get("image", CARD)]:
            if not (ROOT / ref).exists():
                sys.exit(f"{e['slug']}: missing {ref}")
    print(f"built {len(papers)} papers and {len(entries)} entries into {OUT}")


if __name__ == "__main__":
    build()
