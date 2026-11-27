# Checking guide

Run every command from the result folder. All arithmetic is exact (integers and fractions). The paper's Section 5 describes the same checks.

| Command | What it checks | Time (one Steam Deck core) |
|---|---|---|
| `python3 -I checks/prefix.py data/PSQ.txt` | Finite checks of s and h(s) (below) | about 40 s |
| `python3 -I checks/controls.py data/PSQ.txt` | `decide.py` finds a real square in each changed automaton that has one | about 20 s |
| `python3 -I checks/decide.py data/PSQ.txt square` | The infinite word s has no square (decision procedure, no Walnut code) | about 6 min |
| `bash checks/ci.sh` | The three commands above; each result must equal `data/expected.json`, and the numbers must occur in `paper/paper.tex` | about 7 min |
| `bash checks/walnut/run_walnut.sh` | Builds Walnut at commit c61231a from source and reruns the Walnut proofs | build plus about 4 min, 3 GB heap |
| `javac checks/search/Sqf.java && java -Xss512m -cp checks/search Sqf 3000 4 4` | The search that found the automaton | seconds; prints the automaton of `data/PSQ.txt` and `FOUND` |

`data/PSQ.txt` is the automaton in Walnut's word-automaton format: the first line names the numeration system (`msd_pell`), and each block is `state output` followed by `digit -> next state`.

## Decision procedure (`decide.py`)

The verifier wrote this program from the definitions, without Walnut code or data. It reads automata that take representations most significant digit first, padded with leading zeros.

1. Pell adder. A state is a pending carry c1·α + c2 with α² = 2α + 1. The carries are bounded; the program checks that a doubled bound gives the same set of live states, and tests the adder against integer addition for many triples.
2. Mismatch automaton M(u, n): "s[u] ≠ s[u+n]". It is built as a nondeterministic automaton and determinized (151 states).
3. Automaton bad(i, n): "some u with i ≤ u < i+n satisfies M(u, n)".
4. A breadth-first search over all valid pairs (i, n) with n ≥ 1 looks for a pair where bad is false. Such a pair is a square s[i..i+2n−1]. The search ends with no such pair, after 442377 states. For a word that has a square, it prints `FOUND i=.. n=..`.

## Controls (`controls.py`)

The automaton has 12 transitions. The loop δ(0,0) = 0 must stay, so 11 transitions can change, each to 3 other states: 33 changed automata. A brute-force search finds a square in the first 4000 letters of 32 of them. For each of the 32, `decide.py` must print `FOUND`, and the reported factor must be a real square. In 11 cases the reported square has period 2 or 3. The change δ(1,2) = 1 is skipped: it computes s itself, because a digit 2 in a valid representation is always followed by a 0, and δ(0,0) = δ(1,0) = 0. `bash checks/ci.sh` fails on a changed `data/PSQ.txt` (tested with δ(0,1) = 2: `decide.py` prints `FOUND i=2 n=2`, and ci.sh exits with 1).

## Prefix checks (`prefix.py`)

1. Computes s(0..99999) from the greedy Pell representation of each n, and again as the coding of the fixed point of the non-erasing substitution of the paper (Lemma 8). The two agree. The same comparison passes for 200 random 4-state Pell automata (3000 letters each, seed 20261127).
2. s(0..49999) has no square.
3. For the first 200000 letters z of h(s), and for each period p, finds the longest run of positions j with z[j] = z[j−p]. This gives the exact largest exponent of a factor of z: 7/3. The first factor of exponent 7/3 starts at position 8 and has length 7 and period 3 (`1001001`).
4. Controls: s with one changed letter has a square; the first 20000 letters of the Thue–Morse word have largest exponent 2.

These are finite checks. They support the result but do not prove it.

## Walnut (`walnut/`)

`squarefree.txt` holds the two forms of the squarefree sentence; Walnut must print `TRUE` for both. `hb.txt` defines the Pell automaton for h(s) (1518 states) and checks its first four values and the letters of s; Walnut must print `TRUE` twice. `run_walnut.sh` clones Walnut, checks out commit `c61231a244090a75e0923defc574c5389f8a3686`, builds it with its Maven wrapper, copies `data/PSQ.txt` into Walnut's `Word Automata Library`, runs both files and fails unless each result is `TRUE`. It writes `squarefree.log` and `hb.log` next to the command files.

A direct Walnut proof that h(s) has no factor of exponent above 7/3 ran out of memory (3.2 GB heap). The proof does not need it: Lemma 4 of the paper (Karhumäki and Shallit) covers it.
