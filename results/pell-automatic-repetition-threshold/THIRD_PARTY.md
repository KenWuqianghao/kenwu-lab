# Third-party material

No third-party source code or figures are copied into this folder.

- The definitions, the method and the quoted question come from J.-P. Allouche, N. Rampersad, J. Shallit, *Repetition threshold for binary automatic sequences*, [arXiv:2406.06513v3](https://arxiv.org/abs/2406.06513). The paper and the README quote one sentence of its Section 4, with citation.
- The four images of the morphism h are copied from J. Karhumäki, J. Shallit, *Polynomial versus exponential growth in repetition-free binary words*, J. Combin. Theory Ser. A 105 (2004), Section 5 (also Lemma 5 of arXiv:2406.06513). They appear in `checks/prefix.py`, `checks/walnut/hb.txt` and the paper, with citation.
- `checks/walnut/run_walnut.sh` downloads and builds [Walnut](https://github.com/Walnut-Theorem-Prover/Walnut) (GPL-3.0) at commit c61231a. Walnut is not redistributed here. `data/PSQ.txt` and the files in `checks/walnut/` are inputs in Walnut's file format, written for this result.
- `checks/decide.py`, `checks/controls.py`, `checks/prefix.py` and `checks/search/Sqf.java` were written for this result. `checks/requirements.txt` pins [NumPy](https://numpy.org) (BSD-3-Clause), which is not redistributed here.
- The paper uses LaTeX with the packages listed in `paper/paper.tex`. They are not redistributed here.
