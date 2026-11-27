# Checks

Run the commands from the result folder with Python 3.10 or later. All checks use only
the standard library ([requirements.txt](requirements.txt) lists no packages). They use
exact integers and `fractions.Fraction`; no floating point and no LP solver.

| Command | What it checks | Time |
|---|---|---|
| `python3 -I checks/instance.py` | Prints the main instance and its fractional point; equals [instance.json](instance.json). | < 0.1 s |
| `python3 -I checks/check_certificate.py checks/instance.json` | Steps of the proof (paper, Section 3.1): the point with value 1/3 is in CLP(P,3); 36 > 12·2, so LP(P) = 3; 36 = 12·3, so support configurations are full; all 36 full configurations have 0 or 3 point jobs of copy 0; 8 is not a multiple of 3. | < 0.1 s |
| `python3 -I checks/vcheck.py main checks/instance.json` | Second checker. Builds the instance from its description, enumerates the configurations from eq. (8) of the source, decides feasibility of CLP(P,3) and CLP(P,2) with an exact simplex method, and searches all half-integral points (no argument modulo 3). Control: the same search finds a half-integral point at T = 4. | 0.4 s |
| `python3 -I checks/vcheck.py file checks/instance_small.json` | The same for the second counterexample (5 machines, 14 jobs, T = 14). | 1.6 s |
| `python3 -I checks/check_small.py` | The second counterexample with the search in `check_counterexample.py`, which shares no code with `vcheck.py`. | 0.1 s |
| `python3 -I checks/check_ip.py checks/instance.json` | An assignment of the main instance with makespan 4, so IP(P) = 4. | < 0.1 s |
| `python3 -I checks/control.py 1` and `python3 -I checks/control.py 2` | The pruned search of `vcheck.py` agrees with a search without pruning on 400 random small instances per seed. | 3 s each |
| `bash checks/ci.sh` | All of the above. Each output must equal the file in [expected/](expected/), and the numbers in the paper must match the outputs. | 6 s |

Times are for one core of a Steam Deck (AMD Zen 2).

## Files

- [instance.json](instance.json): the main instance. `p` are the sizes, `M[j]` the machines
  of job `j` (0-indexed), `T = 3`, and `x` lists the nonzero entries of the fractional point
  as `[machine, jobs, value]`. Jobs 0 to 11 are the point jobs `P(c,k)` (index `4c + k`);
  jobs 12 to 19 are the fillers `F(0)` to `F(7)`. Machine `(c,t)` has index `4c + t`.
- [instance_small.json](instance_small.json): the second counterexample, in the same format.
- `check_counterexample.py`: the point check and the half-integral search that
  `check_certificate.py` and `check_small.py` use.

## Lean

The Lean proof in [../lean/Solution.lean](../lean/Solution.lean) does not depend on these
checks. See the result [README](../README.md#check-it) for the command.

## What the checks do not prove

The Python checks of the main instance support the hand proof; the Lean proof is the
formal check. The second counterexample is checked only by the two exhaustive searches.
It came from a random walk among small instances; that search script is not part of this
folder, and its other counts are not used.
