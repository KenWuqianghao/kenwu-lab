# The configuration LP of restricted assignment need not have a half-integral point at the LP makespan

In the restricted assignment problem, each job has a size and a set of machines on which it can run, and the goal is to assign all jobs so that the most loaded machine has the smallest possible load (the makespan). The configuration LP is a strong linear relaxation of this problem: each machine chooses a fractional mix of job sets ("configurations") that fit within a makespan bound T. How far the LP value can be from the true optimum (the integrality gap) is a known open question.

In September 2026, Encz, Mastrolilli and Vercesi ([arXiv:2609.19967](https://arxiv.org/abs/2609.19967v1), page 23:10) stated Conjecture 10:

> For every instance P of the restricted assignment problem, the polyhedron CLP(P, LP(P)) contains a half-integral feasible solution; that is, a vector x such that x_{i,C} ∈ {0, 1/2, 1} for all i ∈ [m] and C ∈ 𝒞_i(P, LP(P)).

Here LP(P) is the smallest integer T for which CLP(P, T) is feasible. If the conjecture were true, the gap question would reduce to the graph balancing case (each job on at most two machines), where the bound 1.749 of Jansen and Rohwedder is known.

**Result.** The conjecture is false. The counterexample has 12 machines and 20 jobs:

| Jobs | Size | Allowed machines |
|---|---|---|
| 12 point jobs P(c,k), c ∈ {0,1,2}, k ∈ {0,1,2,3} | 1 | the 3 machines (c,t) with t ≠ k |
| 8 filler jobs F(f), f ∈ {0,…,7} | 3 | the 3 machines (0,⌊f/2⌋), (1,⌊f/2⌋), (2,⌊f/2⌋) |

The total size is 36 = 12 · 3, and LP(P) = 3. Because the total size fills every machine exactly, every configuration that a feasible point uses has load exactly 3. Such a configuration is one filler or three point jobs of one copy. So it holds 0 or 3 of the 4 point jobs of copy 0. In a half-integral point, count the coverings of these 4 jobs in units of 1/2. Each job is covered by 2 units, so the total is 8. Each unit of a configuration adds 0 or 3 to the total. But 8 is not a multiple of 3. A second counterexample, with 5 machines and 14 jobs, was found by computer search.

The counterexample does not change the known bounds on the integrality gap: this instance has gap 4/3.

Proved in Lean; not yet reviewed by experts.

[Read the paper](paper/paper.pdf) · [LaTeX source](paper/paper.tex)

## Abstract

Encz, Mastrolilli and Vercesi conjectured that for every instance P of the restricted assignment problem, the configuration LP CLP(P, LP(P)) at the smallest feasible integer makespan LP(P) contains a half-integral point (their Conjecture 10). If it were true, the integrality gap of the configuration LP would reduce to the graph balancing case. We show that the conjecture is false. Our counterexample has 12 machines and 20 jobs with processing times 1 and 3, and LP(P) = 3. The total processing time is 36 = 12 · 3, so every configuration in the support of a feasible point has load exactly 3. Each such configuration contains 0 or 3 jobs of a fixed set of 4 jobs. In a half-integral point these 4 jobs are covered 8 times in total, with weights 1/2, and 8 is not a multiple of 3. Lean 4 with Mathlib checks the disproof from the definitions, with only the standard axioms. We also give a second counterexample with 5 machines and 14 jobs, found by a random search and checked by an exhaustive search. The counterexample does not change the known bounds on the integrality gap.

This work has not yet been reviewed by experts. The computations, the proofs and the text were produced by AI models (from Anthropic and OpenAI), working under the author's direction.

## Check it

The Lean proof, with [elan](https://github.com/leanprover/elan) and a Lean project on Mathlib tag v4.36.0 (Lean v4.36.0). Run it from the root of the Lean project, with the path to the file:

```sh
lake env lean lean/Solution.lean
```

It takes about 20 s after Mathlib is built (18 s measured). It prints `'HalfIntegralCLP.not_conjecture10' depends on axioms: [propext, Classical.choice, Quot.sound]`. `lake comparator` with `lean/Challenge.lean` and `lean/comparator.json` checks that the proof proves exactly the stated theorem (about 90 s measured).

The exact checks, from this folder, with Python 3.10 or later (standard library only):

```sh
python3 -I checks/check_certificate.py checks/instance.json   # < 0.1 s: each step of the proof
python3 -I checks/vcheck.py main checks/instance.json          # 0.4 s: exact simplex and exhaustive search
python3 -I checks/vcheck.py file checks/instance_small.json    # 1.6 s: the second counterexample
bash checks/ci.sh                                              # 6 s: all checks, and the numbers in the paper
```

Times are for one core of a Steam Deck (AMD Zen 2). The [checking guide](checks/README.md) explains each check. The Lean result does not depend on the Python checks.

## Credits

K. I. Encz, M. Mastrolilli and E. Vercesi stated the conjecture and its consequence for graph balancing ([arXiv:2609.19967](https://arxiv.org/abs/2609.19967v1)). The bounds on the integrality gap that the paper recalls come from O. Svensson ([doi:10.1145/1993636.1993718](https://doi.org/10.1145/1993636.1993718)), K. Jansen and L. Rohwedder ([arXiv:1611.01934](https://arxiv.org/abs/1611.01934)) and others cited in the source; the graph balancing bound 1.749 is by K. Jansen and L. Rohwedder ([arXiv:1811.00955](https://arxiv.org/abs/1811.00955)). The Lean proof uses [Lean](https://github.com/leanprover/lean4) and [Mathlib](https://github.com/leanprover-community/mathlib4). Apache-2.0 (see the repository's LICENSE); [THIRD_PARTY.md](THIRD_PARTY.md) lists the third-party material.

## Cite

```bibtex
@misc{WuHalfIntegralCLP2026,
  author       = {Wu, Qianghao},
  title        = {{The configuration LP of restricted assignment need not have a half-integral point at the LP makespan}},
  year         = {2026},
  howpublished = {\url{https://github.com/KenWuqianghao/kenwu-lab/tree/main/results/half-integral-configuration-lp}}
}
```
