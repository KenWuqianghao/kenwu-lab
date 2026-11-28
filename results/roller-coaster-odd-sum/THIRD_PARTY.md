# Third-party material

No third-party source code, data or figures are copied into this folder.

- The definitions in `lean/`, the checkers and the paper follow T. Ahmed and H. Snevily, *Some properties of Roller Coaster permutations* ([preprint](https://tanbir.github.io/files/preprints/ahmed_snevily_roller_coaster_permutations.pdf)). The paper quotes Conjecture 2.4 word for word, with citation.
- The witness permutation is from F. Botler and B. L. Netto, *New bounds on Roller Coaster permutations*, ETC 2021, Table 1 ([doi:10.5753/etc.2021.16378](https://doi.org/10.5753/etc.2021.16378)), and from B. R. L. Netto's master's thesis (2022), Table 2.1. The paper quotes one sentence of the thesis, with citation. `checks/check_lists.py` contains five permutations from these sources and from Ahmed and Snevily, as numbers, to check the values that the paper quotes.
- The Lean proof uses [Lean](https://github.com/leanprover/lean4) and [Mathlib](https://github.com/leanprover-community/mathlib4) (Apache-2.0). They are not redistributed here.
- `checks/validate_bb.py` uses [NumPy](https://numpy.org) (BSD-3-Clause). `checks/requirements.txt` pins the version. It is not redistributed here.
- The paper uses LaTeX with the packages listed in `paper/paper.tex`. They are not redistributed here.
