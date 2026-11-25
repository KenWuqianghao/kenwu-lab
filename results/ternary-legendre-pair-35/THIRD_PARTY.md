# Third-party material

No third-party source code or figures are copied into this folder. The only third-party data are the eight cited pairs that `checks/check.py` uses as positive controls (see below).

- The definitions in `lean/TernaryLP35.lean`, the checkers and the paper follow I. S. Kotsireas, H. Liu, A. Winterhof, *k-ary Legendre pairs*, [arXiv:2611.31067v1](https://arxiv.org/abs/2611.31067). The paper quotes two short passages of it (the open cases and Conjecture 10) with citation.
- `checks/check.py` contains the eight exponent-word pairs printed in that paper (lengths 5, 11, 14, 17, 20, 23, 29 and 32). They are used only as positive controls, with citation.
- The Lean proof uses [Lean](https://github.com/leanprover/lean4) and [Mathlib](https://github.com/leanprover-community/mathlib4) (Apache-2.0). They are not redistributed here.
- The paper uses LaTeX with the packages listed in `paper/paper.tex`. They are not redistributed here.
