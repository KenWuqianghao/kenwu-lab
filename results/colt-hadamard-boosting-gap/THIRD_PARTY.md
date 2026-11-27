# Third-party material

## Hadamard matrix Had.16.3

`checks/had.16.3.txt` is a copy, without changes, of the file `had.16.3.txt` from
N. J. A. Sloane's [Library of Hadamard Matrices](http://neilsloane.com/hadamard/),
downloaded on 2026-11-27. It is a 16 × 16 matrix of `+` and `-` signs with two lines of
description. The library page states no license. The file is included so that
`checks/check_extra.py` can show where the matrix *U* comes from; the proof does not depend
on it, because the certificate and the Lean file contain *U* in full.

## Lean and Mathlib

The proof uses [Lean](https://github.com/leanprover/lean4) and
[Mathlib](https://github.com/leanprover-community/mathlib4), distributed under Apache-2.0.
Lake downloads them with the pinned versions (Lean v4.36.0, Mathlib tag v4.36.0); their
source trees and licenses are not redistributed in this folder.

## Python packages

`checks/vcheck.py --lp` uses [NumPy](https://numpy.org/) (BSD-3-Clause) and
[SciPy](https://scipy.org/) (BSD-3-Clause), which includes the
[HiGHS](https://highs.dev/) solver (MIT). `pip` installs them with the versions in
`checks/requirements.txt`; they are not redistributed here.

## Quoted text

`README.md`, `paper/paper.tex` and the Lean doc comments quote the statement of
Conjecture 2, equation (1) and short phrases from J. Nie, M. K. Warmuth,
S. V. N. Vishwanathan and X. Zhang, "Open Problem: Lower bounds for Boosting with Hadamard
Matrices", COLT 2013, PMLR 30:1076–1079, with citation. `paper/paper.tex` quotes one
sentence of A. Grønlund, K. G. Larsen and A. Mathiasen, arXiv:1901.10789, with citation.
