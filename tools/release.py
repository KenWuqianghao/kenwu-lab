#!/usr/bin/env python3
"""Archive new result versions on Zenodo and write the DOIs back.

A result needs a release when the git tag <slug>-v<version> does not exist.

  release.py --mode draft     create the Zenodo draft, upload, set metadata, then delete
                              the draft. Proves every step except the publish call.
  release.py --mode publish   publish, then update result.json, README.md and
                              CHANGELOG.md. Prints the tags to create, one per line,
                              into released.txt.

Env: ZENODO_TOKEN, ZENODO_URL (default https://zenodo.org), GITHUB_REPOSITORY.
"""

import argparse
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = os.environ.get("ZENODO_URL", "https://zenodo.org").rstrip("/") + "/api"
REPO = os.environ.get("GITHUB_REPOSITORY", "KenWuqianghao/kenwu-lab")
AUTHOR = {"name": "Wu, Ken"}


def call(method, url, data=None, raw=None, ctype="application/json"):
    body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
    req = urllib.request.Request(url, data=body, method=method, headers={
        "Authorization": f"Bearer {os.environ['ZENODO_TOKEN']}",
        "Content-Type": ctype if body is not None else "application/json",
        "User-Agent": "kenwu-lab-release/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            text = r.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"Zenodo {method} {url} -> {e.code}: {e.read().decode(errors='replace')[:800]}")
    return json.loads(text) if text else {}


def existing_tags():
    out = subprocess.run(["git", "-C", str(ROOT), "tag", "-l"], capture_output=True, text=True, check=True)
    return set(out.stdout.split())


def pending():
    tags = existing_tags()
    for meta_path in sorted(ROOT.glob("results/*/result.json")):
        meta = json.loads(meta_path.read_text())
        tag = f"{meta['slug']}-v{meta['version']}"
        if tag not in tags:
            yield meta_path.parent, meta, tag


def bundle(folder, tag):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and ".lake" not in p.parts:
                z.write(p, f"{tag}/{p.relative_to(folder)}")
    return buf.getvalue()


def metadata(meta, tag):
    tree = f"https://github.com/{REPO}/tree/{tag}/results/{meta['slug']}"
    related = [{"identifier": tree, "relation": "isSupplementedBy", "resource_type": "software"}]
    related += [{"identifier": r["doi"], "relation": r.get("relation", "cites"), "scheme": "doi"}
                for r in meta.get("related", [])]
    return {"title": meta["title"], "upload_type": "publication", "publication_type": "preprint",
            "description": f"<p>{meta['abstract']}</p><p>Code, checks and source: <a href=\"{tree}\">{tree}</a></p>",
            "creators": [AUTHOR], "keywords": meta["keywords"], "license": "cc-by-4.0",
            "version": f"v{meta['version']}", "related_identifiers": related, "prereserve_doi": True}


def deposit(folder, meta, tag, mode):
    if meta.get("zenodo_id"):
        res = call("POST", f"{API}/deposit/depositions/{meta['zenodo_id']}/actions/newversion")
        draft = call("GET", res["links"]["latest_draft"])
        for f in draft.get("files", []):
            call("DELETE", f"{API}/deposit/depositions/{draft['id']}/files/{f['id']}")
    else:
        draft = call("POST", f"{API}/deposit/depositions", data={})
    draft_id, bucket = draft["id"], draft["links"]["bucket"]
    try:
        call("PUT", f"{bucket}/{meta['slug']}.pdf", raw=(folder / "paper/paper.pdf").read_bytes(),
             ctype="application/octet-stream")
        call("PUT", f"{bucket}/{tag}.zip", raw=bundle(folder, tag), ctype="application/octet-stream")
        updated = call("PUT", f"{API}/deposit/depositions/{draft_id}", data={"metadata": metadata(meta, tag)})
        reserved = updated["metadata"]["prereserve_doi"]["doi"]
        files = call("GET", f"{API}/deposit/depositions/{draft_id}/files")
        print(f"{tag}: draft {draft_id}, reserved DOI {reserved}, files {[f['filename'] for f in files]}")
        if mode == "draft":
            return None
        return call("POST", f"{API}/deposit/depositions/{draft_id}/actions/publish")
    finally:
        if mode == "draft":
            call("DELETE", f"{API}/deposit/depositions/{draft_id}")
            print(f"{tag}: draft {draft_id} deleted (draft mode)")


def write_back(folder, meta, record, today):
    doi = record["doi"]
    meta.update({"doi": doi, "concept_doi": record.get("conceptdoi"), "zenodo_id": record["id"],
                 "doi_version": meta["version"]})
    (folder / "result.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    line = f"Archived on Zenodo: [doi:{doi}](https://doi.org/{doi})"
    readme = (folder / "README.md").read_text()
    if re.search(r"^Archived on Zenodo:.*$", readme, re.M):
        readme = re.sub(r"^Archived on Zenodo:.*$", line, readme, count=1, flags=re.M)
    else:
        readme = readme.rstrip("\n") + f"\n\n{line}\n"
    (folder / "README.md").write_text(readme)

    changelog = ROOT / "CHANGELOG.md"
    head = "# Changelog\n\nEach result is versioned on its own and tagged `<slug>-vN`.\n"
    old = changelog.read_text()[len(head):] if changelog.exists() else ""
    entry = (f"\n## {meta['slug']} v{meta['version']} ({today})\n\n- {meta['summary']}\n"
             f"- Zenodo: [{doi}](https://doi.org/{doi})\n")
    changelog.write_text(head + entry + old)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("draft", "publish"), required=True)
    mode = ap.parse_args().mode
    today = dt.date.today().isoformat()
    tags = []
    for folder, meta, tag in pending():
        if meta.get("doi") and meta.get("doi_version") == meta["version"]:
            print(f"{tag}: already archived as {meta['doi']}; tag only")
            tags.append(tag)
            continue
        record = deposit(folder, meta, tag, mode)
        if record:
            write_back(folder, meta, record, today)
            print(f"{tag}: published {record['doi']}")
            tags.append(tag)
    if mode == "publish":
        (ROOT / "released.txt").write_text("".join(t + "\n" for t in tags))
    if not tags and mode == "publish":
        print("nothing to release")


if __name__ == "__main__":
    main()
