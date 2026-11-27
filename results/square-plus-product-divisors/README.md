# Divisor sums over N − k² modulo 4 for N ≡ 6 (mod 8)

Write a number N as a square plus a product: N = k² + ab, with k, a, b positive integers. For each k, the number of pairs (a, b) is the number of divisors of N − k², so the number of these representations is

> S(N) = ∑_{1≤k<√N} σ0(N − k²),

where σ0(m) is the number of positive divisors of m. Hooley studied this sum in 1958. In 2026, Jirattikansakul, Kittipassorn, Kongsiri, Moonwichit and Sriamorn ([arXiv:2604.25394](https://arxiv.org/abs/2604.25394)) connected it with partitions of N into exactly two part sizes. They proved that 4 divides S(N) when N is in one of five arithmetic progressions, among them N = 16n + 14. Their computations suggested that 4 divides S(N) for all N ≡ 6 (mod 8), and they stated the open half as Conjecture 7:

> Let N = 16n + 6 for some nonnegative integer n. Then ∑_{1≤k<√N} σ0(N − k²) ≡ 0 (mod 4).

**Result.** S(N) ≡ 0 (mod 4) for every N ≡ 6 (mod 8). This proves Conjecture 7. For N ≡ 14 (mod 16) the result was already known, and this is a new proof.

| N | 6 | 14 | 22 | 30 | 38 | 46 | 54 | 62 |
|---|---|---|---|---|---|---|---|---|
| S(N) | 4 | 8 | 16 | 16 | 16 | 32 | 28 | 20 |

The proof is elementary. It counts the triples (k, a, b) with k² + ab = N, and it pairs them off with involutions. For odd k it uses the involution from Zagier's one-sentence proof of Fermat's two-squares theorem. Both halves (k odd and k even) reduce, modulo 2, to the same number F of solutions of 2k² + 4y² = N, so S(N) ≡ 2F + 2F ≡ 0 (mod 4).

Proved in Lean; not yet reviewed by experts.

[Read the paper](paper/paper.pdf) · [LaTeX source](paper/paper.tex)

## Abstract

Let S(N) = ∑_{1≤k<√N} σ0(N − k²), where σ0(m) is the number of positive divisors of m. Jirattikansakul, Kittipassorn, Kongsiri, Moonwichit and Sriamorn proved that S(N) ≡ 0 (mod 4) for N = An + B with (A, B) ∈ {(16, 14), (36, 30), (72, 42), (196, 70), (252, 114)}, and they conjectured that S(N) ≡ 0 (mod 4) for all N = 16n + 6 (their Conjecture 7). We prove this conjecture. More generally, we prove that S(N) ≡ 0 (mod 4) for every N ≡ 6 (mod 8), as their computations suggest. The class N ≡ 14 (mod 16) is their case (16, 14), so for that class our proof is a new proof of a known result. Their proof uses a congruence of Keith for partitions into exactly two part sizes, which was proved with modular forms. Our proof is elementary. It counts the solutions of k² + ab = N with involutions, one of which is Zagier's involution from his one-sentence proof of Fermat's two-squares theorem. Lean 4 with Mathlib checks the theorem and Conjecture 7 from the definitions, with only the standard axioms. With Theorem 4 of the source, the result gives ν2(N) ≡ −σ1(N)/2 (mod 4) for all N ≡ 6 (mod 8), where ν2(N) is the number of partitions of N with exactly two part sizes. This consequence is not checked in Lean. This work has not yet been reviewed by experts. The computations, the proofs and the text were produced by AI models (from Anthropic and OpenAI), working under the author's direction.

## Check it

The Lean proof, with [elan](https://github.com/leanprover/elan) and a Lean project on Mathlib tag v4.36.0 (Lean v4.36.0). Run it from the root of the Lean project, with the path to the file:

```sh
lake env lean lean/Solution.lean
```

It takes about 1 minute after Mathlib is built (41 s measured). It prints `'sum_card_divisors_mod_four' depends on axioms: [propext, Classical.choice, Quot.sound]` and the same for `conjecture_7`. `lake comparator` with `lean/Challenge.lean` and `lean/comparator.json` checks that the proof proves exactly the stated theorems.

The numerical checks, from this folder, with Python 3.10 or later (the sieve needs numpy, pinned in `checks/requirements.txt`):

```sh
python3 -I checks/check_statement.py 3000    # about 10 s: the statement from the definitions, N <= 3000
python3 -I checks/check_lean_route.py 4000   # about 9 s: each step of the proof, N <= 4000
bash checks/ci.sh                            # about 1 min: all checks, and the numbers in the paper
```

Times are for one core of a Steam Deck (AMD Zen 2). The [checking guide](checks/README.md) explains each check. The Lean result does not depend on the Python checks.

## Credits

S. Jirattikansakul, T. Kittipassorn, K. Kongsiri, N. Moonwichit and K. Sriamorn stated the conjecture and proved the case N ≡ 14 (mod 16) ([arXiv:2604.25394](https://arxiv.org/abs/2604.25394)). W. J. Keith proved the congruences for partitions into two part sizes that their proof uses ([doi:10.1142/S1793042117500130](https://doi.org/10.1142/S1793042117500130)); E. R. DeWitt and W. J. Keith gave a combinatorial proof of the case 16n + 14 ([arXiv:2507.13566](https://arxiv.org/abs/2507.13566)). The main involution is from D. Zagier's one-sentence proof ([doi:10.2307/2323918](https://doi.org/10.2307/2323918)). C. Hooley studied the sum S(N) ([doi:10.1007/BF01187402](https://doi.org/10.1007/BF01187402)). The Lean proof uses [Lean](https://github.com/leanprover/lean4) and [Mathlib](https://github.com/leanprover-community/mathlib4). Apache-2.0 (see the repository's LICENSE); [THIRD_PARTY.md](THIRD_PARTY.md) lists the third-party material.

## Cite

```bibtex
@misc{WuSquarePlusProduct2026,
  author       = {Wu, Qianghao},
  title        = {{Divisor sums over $N-k^2$ modulo 4 for $N \equiv 6 \pmod 8$: a proof of a conjecture of Jirattikansakul, Kittipassorn, Kongsiri, Moonwichit and Sriamorn}},
  year         = {2026},
  howpublished = {\url{https://github.com/KenWuqianghao/kenwu-lab/tree/main/results/square-plus-product-divisors}}
}
```
