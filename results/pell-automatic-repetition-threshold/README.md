# The repetition threshold for binary Pell-automatic sequences is 7/3

A word has *period* p if each letter equals the letter p places later. The *exponent* of a word is its length divided by its least period: `1001001` has period 3 and exponent 7/3. The *critical exponent* of an infinite word is the supremum of the exponents of its finite factors. For a set of infinite words, the *repetition threshold* is the smallest critical exponent that a word of the set can have (an infimum).

A sequence is *Pell-automatic* if a finite automaton computes its n-th term from n written in the Pell numeration system. That system writes n with the weights 1, 2, 5, 12, 29, 70, … (each weight is twice the previous one plus the one before), with digits 0, 1 and 2.

Allouche, Rampersad and Shallit ([arXiv:2406.06513](https://arxiv.org/abs/2406.06513)) proved that the repetition threshold is 7/3 for binary k-automatic sequences when k is not a power of 2, and also for binary Fibonacci-automatic and Tribonacci-automatic sequences. In their last section they wrote: "It seems likely that 7/3 is the critical exponent for many other binary generalized automatic sequences, such as the Pell-automatic sequences [3], but a general theorem seems hard to prove."

**Result.** The repetition threshold of the binary Pell-automatic sequences is 7/3, and one binary Pell-automatic sequence has critical exponent exactly 7/3.

The construction is a 4-state Pell automaton. Its output word over 4 letters starts

```
s = 010230131012010231202301023130102301310120231301310120102301...
```

and has no square (no factor of the form uu). A 21-uniform morphism of Karhumäki and Shallit turns s into a binary Pell-automatic word with critical exponent exactly 7/3. The lower bound follows the argument of Allouche, Rampersad and Shallit, with Durand's theorem for substitutions. The paper gives the non-erasing substitution that this argument needs for the Pell system. The method is the method of the source, applied to one more numeration system. The general question for other numeration systems remains open.

| state | δ(q,0) | δ(q,1) | δ(q,2) | output |
|---|---|---|---|---|
| 0 (initial) | 0 | 1 | 2 | 0 |
| 1 | 0 | 2 | 0 | 1 |
| 2 | 3 | 1 | 2 | 2 |
| 3 | 1 | 2 | 2 | 3 |

Computer-assisted; not yet reviewed by experts.

[Read the paper](paper/paper.pdf) · [LaTeX source](paper/paper.tex)

## Abstract

The critical exponent of an infinite word is the supremum of the exponents of its finite factors. The repetition threshold of a set of infinite words is the infimum of their critical exponents. Allouche, Rampersad and Shallit proved that the repetition threshold of the binary Fibonacci-automatic sequences and of the binary Tribonacci-automatic sequences is 7/3. They wrote that 7/3 is likely the critical exponent for many other binary generalized automatic sequences, such as the Pell-automatic sequences. We prove that the repetition threshold of the binary Pell-automatic sequences is 7/3, and that one Pell-automatic sequence attains it. The upper bound uses a 4-state Pell automaton whose output word **s** over 4 letters is squarefree. The theorem prover Walnut proves that **s** is squarefree, and a separate decision procedure that does not use Walnut confirms it. A 21-uniform morphism of Karhumäki and Shallit then gives a binary Pell-automatic sequence with critical exponent exactly 7/3. The lower bound follows the argument of Allouche, Rampersad and Shallit, with Durand's theorem for substitutions. We give the non-erasing substitution that this argument needs for the Pell numeration system. The proof is computer-assisted and uses published lemmas that we do not prove again. The method is the method of Allouche, Rampersad and Shallit, applied to one more numeration system; the general question for other numeration systems remains open. This work has not yet been reviewed by experts. The computations, the proofs and the text were produced by AI models (from Anthropic and OpenAI), working under the author's direction.

## Check it

From this folder, with Python 3.10 or later and `numpy` (`pip install -r checks/requirements.txt`):

```sh
python3 -I checks/prefix.py data/PSQ.txt      # about 40 s: finite checks of s and h(s), two constructions of s
python3 -I checks/controls.py data/PSQ.txt    # about 20 s: the decision procedure finds a square in 32 changed automata
python3 -I checks/decide.py data/PSQ.txt square   # about 6 min: proves that the infinite word s has no square
bash checks/ci.sh                             # all three, and a check of the numbers in the paper (about 7 min)
```

The last line of `decide.py` must be `RESULT square : no (i,n) with n>=1 and all matches. reachable top states: 442377`.

The Walnut proofs, with git and a JDK 17 or later (about 3 GB of Java heap):

```sh
bash checks/walnut/run_walnut.sh              # builds Walnut c61231a from source, then about 4 min
```

It prints `TRUE` four times and `run_walnut.sh: all Walnut results TRUE`. Times are for one core of a Steam Deck (AMD Custom APU 0932). The [checking guide](checks/README.md) explains each check.

## Credits

J.-P. Allouche, N. Rampersad and J. Shallit posed the question and gave the method, the definitions and the lemmas that the proof uses ([arXiv:2406.06513](https://arxiv.org/abs/2406.06513)). The morphism h and its lemma are from J. Karhumäki and J. Shallit (J. Combin. Theory Ser. A 105, 2004). The structure theorem for 7/3-free words is from N. Rampersad, J. Shallit and A. M. Shur (EPTCS 63, 2011). The Cobham-type theorem is from F. Durand (J. Eur. Math. Soc. 13, 2011). The Pell numeration system in Walnut is from A. R. Baranwal and J. Shallit (WORDS 2019). The proofs use [Walnut](https://github.com/Walnut-Theorem-Prover/Walnut) (H. Mousavi and others). Apache-2.0 (see the repository's LICENSE); [THIRD_PARTY.md](THIRD_PARTY.md) lists the third-party tools.

## Cite

```bibtex
@misc{WuPellRepetitionThreshold_2026,
  author       = {Wu, Qianghao},
  title        = {{The repetition threshold for binary Pell-automatic sequences is 7/3}},
  year         = {2026},
  howpublished = {\url{https://github.com/KenWuqianghao/kenwu-lab/tree/main/results/pell-automatic-repetition-threshold}}
}
```
