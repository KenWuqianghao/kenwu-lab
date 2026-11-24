# Ken Wu Lab

Short papers on open problems, and small findings, from AI-assisted research.
Not yet reviewed by experts. Corrections are welcome as issues or pull requests.

Site: https://kenwu-lab.wooqianghao.workers.dev

The computations, proofs and text are produced by AI models (from Anthropic and
OpenAI) working under the author's direction.

## Layout

- `results/<slug>/` holds one result: `result.json`, `README.md`, `paper/paper.tex`,
  `paper/paper.pdf`, `checks/ci.sh`, and `lean/*.lean` when Lean checks the proof.
- `lean/` is the shared Lean workspace (Lean v4.36.0, Mathlib v4.36.0).
- `site/` builds the website: notes in `site/entries/`, papers from `results/`.
- `tools/check_result.py` checks a result folder. `tools/release.py` archives a new
  result version on Zenodo.

## How a result is published

1. A pull request adds or changes `results/<slug>/`.
2. The `Checks` workflow checks the folder, compiles its Lean files against Mathlib, and
   runs `checks/ci.sh`.
3. Merging the pull request starts `Release and deploy`. For each result whose tag
   `<slug>-v<version>` does not exist, it deposits the paper and the folder on Zenodo,
   writes the DOI into `result.json`, `README.md` and `CHANGELOG.md`, tags the commit,
   and deploys the site to Cloudflare.

The repository variable `ZENODO_MODE` selects `draft` (every step except publishing; the
draft is deleted) or `publish`. A Zenodo record cannot be deleted after publishing.

Code: Apache-2.0 (see `LICENSE`). Papers: CC BY 4.0. Third-party material is listed in
each result's `THIRD_PARTY.md`.
