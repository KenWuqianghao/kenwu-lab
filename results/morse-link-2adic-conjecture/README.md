# A counterexample to Gao and Gu's 2-adic conjecture for weighted Morse link numbers

A [Dyck path](https://en.wikipedia.org/wiki/Dyck_language) is a walk of up and down steps that starts and ends at height 0 and never goes below 0. Give each up step a weight that depends on the height where it starts, and add up the products of the weights over all Dyck paths with 2n steps. The result is a *weighted Catalan number*. With the weight b(x) = (2x+1)², these numbers count the combinatorial types of Morse links, and Postnikov found a pattern in the power of 2 that divides L_n − C_n, where C_n is the ordinary [Catalan number](https://en.wikipedia.org/wiki/Catalan_number). Gao and Gu ([arXiv:1908.03914](https://arxiv.org/abs/1908.03914), Conjecture 4.12) conjectured that the same kind of pattern holds for every weight b(x) = (2x+1)^(2k):

> ξ₂(L^(k)_n − C_n) = s₂(n) + ξ₂(n − α_k) + c_k for all n ≥ 2,

for some 2-adic integer α_k and some integer c_k ≥ 0. Here ξ₂ is the exponent of 2 and s₂(n) is the number of 1s in the binary form of n.

**Result.** The conjecture is false for k = 2, that is, b(x) = (2x+1)⁴. Three exact values are enough:

| n | L^(2)_n − C_n | ξ₂ | s₂(n) |
|---|---|---|---|
| 2 | 80 = 2⁴ · 5 | 4 | 1 |
| 3 | 57344 = 2¹³ · 7 | 13 | 2 |
| 19 | 2¹¹ · (an odd number with 87 digits) | 11 | 3 |

The value at n = 2 gives c₂ ≤ 3. Then 2^(8−c₂) must divide both 3 − α₂ and 19 − α₂, so it divides 16, but 8 − c₂ ≥ 5. The failure comes only from n = 3: if the range starts at n = 4, the data for k ≤ 24 and n ≤ 200 fit the conjecture, and that version remains open. Postnikov's case k = 1 is not affected.

Proved in Lean; not yet reviewed by experts.

[Read the paper](paper/paper.pdf) · [LaTeX source](paper/paper.tex)

## Abstract

Let L^(k)_n be the weighted Catalan number with weight b(x) = (2x+1)^(2k), and let C_n be the Catalan number. The case k = 1 counts the combinatorial types of Morse links. Gao and Gu conjectured that for every positive integer k there are a 2-adic integer α_k and an integer c_k ≥ 0 such that ξ₂(L^(k)_n − C_n) = s₂(n) + ξ₂(n − α_k) + c_k for all n ≥ 2. This generalizes a conjecture of Postnikov for k = 1. We show that the conjecture is false for k = 2. The exact values ξ₂(L^(2)_n − C_n) = 4, 13 and 11 at n = 2, 3 and 19 are incompatible with every choice of α_2 and c_2. Lean 4 with Mathlib checks the theorem from the definition of weighted Catalan numbers by Dyck paths, with only the standard axioms. The failure comes from the index n = 3 alone. The version of the conjecture for n ≥ 4 remains open: it fits our data for k ≤ 24 and n ≤ 200. In the same data, the version for n ≥ 2 fails exactly for k ≡ 2 (mod 4). These two statements are computed, not proved. This work has not yet been reviewed by experts. The computations, the proofs and the text were produced by AI models (from Anthropic and OpenAI), working under the author's direction.

## Check it

From this folder, with Python 3.10 or later (standard library only):

```sh
python3 -I checks/certificate.py    # about 1 s: the exact values, the 2-adic test, a k = 1 control
bash checks/ci.sh                   # about 30 s: all Python checks, the survey for k <= 24, n <= 200, the numbers in the paper
```

The Lean proof, with [elan](https://github.com/leanprover/elan) and a Lean project on Mathlib tag v4.36.0 (Lean v4.36.0):

```sh
lake env lean lean/GaoGu412.lean
```

Run it from the root of the Lean project, with the path to this file. It takes about 3 minutes after Mathlib is built. It prints `'GaoGu.conjecture_4_12_false_k2' depends on axioms: [propext, Classical.choice, Quot.sound]` and the same line for `GaoGu.conjecture_4_12_false`. Times are for one core of an Apple M1 Pro. The [checking guide](checks/README.md) explains each check.

## Credits

Yibo Gao and Andrew Gu stated the conjecture and the definitions ([arXiv:1908.03914](https://arxiv.org/abs/1908.03914); J. Number Theory 226 (2021), [doi:10.1016/j.jnt.2021.03.007](https://doi.org/10.1016/j.jnt.2021.03.007)). Alexander Postnikov stated the case k = 1 ([Counting Morse curves and links](https://math.mit.edu/~apost/papers/morse-brief.pdf)). Ryota Inagaki and Dimana Pramatarova disproved a different conjecture of the same paper ([arXiv:2611.26953](https://arxiv.org/abs/2611.26953)); their paper led us to this one. The Lean proof uses [Lean](https://github.com/leanprover/lean4) and [Mathlib](https://github.com/leanprover-community/mathlib4). Apache-2.0 (see the repository's LICENSE); [THIRD_PARTY.md](THIRD_PARTY.md) lists the third-party material.

## Cite

```bibtex
@misc{WuMorseLink2adic2026,
  author       = {Wu, Qianghao},
  title        = {{A counterexample to Gao and Gu's 2-adic conjecture for weighted Morse link numbers}},
  year         = {2026},
  howpublished = {\url{https://github.com/KenWuqianghao/kenwu-lab/tree/main/results/morse-link-2adic-conjecture}}
}
```

Archived on Zenodo: [doi:10.5281/zenodo.24579593](https://doi.org/10.5281/zenodo.24579593)
