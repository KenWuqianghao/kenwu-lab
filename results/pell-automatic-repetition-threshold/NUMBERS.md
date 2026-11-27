# Numbers in the paper and their sources

Paths without a prefix are in this folder. Paths that start with `project:` are in the factory project repository (`problems/pell-automatic-repetition-threshold`), which holds the full records.

## Numbers

| Number in the paper | Value | Source |
|---|---|---|
| DFAO of Table 1 | 4 states, transitions as in the table | `data/PSQ.txt`; `project:checks/PSQ.txt` |
| First 60 letters of s | `010230131012010231202301023130102301310120231301310120102301` | `checks/prefix.py` (`psq_prefix60`); `data/expected.json` |
| rep(3) = 11, s(3) = 2 | | arithmetic; prefix above |
| Search: at most 4 states, 4 letters, prefix 3000; first DFAO found | | `project:search/sqf_run.out`; VERIFY check 10 |
| Search with 3 states: none, longest prefix 11 | `NONE best=11` | VERIFY check 10 |
| Walnut commit | c61231a (23 November 2026) | `project:checks/walnut.log`; `git log -1` in the Walnut clone |
| Walnut squarefree sentences | `TRUE`, `TRUE` | `project:checks/walnut.log` (solver); `project:verify/walnut_rerun.log` (verifier); write-stage runs with a jar built from source, `project:write/walnut_build.out` and `project:write/walnut_clean.out` |
| Images of h | the four words of Section 3 | `project:work/refs/math_0304095.txt` (Karhumäki–Shallit, Section 5); ARS Lemma 5; `checks/ci.sh` compares them with `checks/walnut/hb.txt` |
| States of the automaton hb | 1518 | `project:write/walnut_clean.out` (`states of the automaton hb`); VERIFY check 9 |
| First four values of hb | 0, 1, 1, 0 | `checks/walnut/hb.txt` (`hbprefix`: `TRUE`) |
| Factor of exponent 7/3 | start 8, length 7, period 3, `1001001` | `checks/prefix.py` (`h_first_73_factor`); `project:verify/vcheck.out` |
| D_M states in decide.py | 151 | `checks/decide.py` output; `project:verify/decide_psq.out` |
| Reachable states, final search | 442377 | `project:write/decide_release.out` (write-stage run, 5 min 43 s); `project:write/ci.out`; `project:verify/decide_psq.out` (6 min 10 s) |
| Run time of decide.py | about 6 minutes | the two runs above |
| Changed DFAOs | 33 in total; 32 with a square in 4000 letters; 32 of 32 detected; 11 with period at least 2; δ(1,2) = 1 computes s itself (argument in Section 5; a write-stage CI run on it gives the same 442377 states, `project:write/neg_same_word.out`) | `checks/controls.py` output; `data/expected.json` |
| Bounded Walnut control n ≤ 6 | `FALSE` on the changed DFAO, `TRUE` on s | `project:verify/ctl2.log`; VERIFY check 4 |
| Unbounded Walnut control | out of memory at 3 GB | `project:verify/ctl.log`; VERIFY check 5 |
| Substitution route = greedy route | 100000 letters of s; 200 of 200 random DFAOs, 3000 letters each | `checks/prefix.py` |
| Substitution route, verifier | 3000000 letters of s | `project:verify/vcheck.out` (`morphism route equals greedy route on 3000000: true`) |
| Squarefree prefix of s | 50000 letters | `checks/prefix.py` |
| Largest exponent, prefix of h(s) | 7/3 in 200000 letters | `checks/prefix.py` |
| Thue–Morse control | largest exponent 2 in 20000 letters | `checks/prefix.py` |
| Verifier's Java checker | no square in 3000000 letters of s; nothing above 7/3 in 63000000 letters of h(s) | `project:verify/vcheck.out` |
| Direct Walnut (7/3)+ check of h(s) | out of memory, Java heap 3.2 GB | `project:RESULT.md`; `project:LOG.md` (sprint) |
| Binary DFAO search | at most 10 and at most 14 states, no prefix of length 100 in 9 minutes | `project:RESULT.md` (log not kept) |
| Pell numbers | 1, 2, 5, 12, 29, 70 | `checks/prefix.py` asserts the lengths of σ^m(A) |
| Walnut run time | about 4 min (207 s for the squarefree file) | `project:write/walnut_build.out` |
| CI on a changed DFAO δ(0,1) = 2 | exit 1; `FOUND i=2 n=2` | `project:write/neg_ci.out` |

## Facts quoted from the sources

| Fact | Place in the source |
|---|---|
| Definitions of period, exponent, ce, rt, α-free, α+-free | ARS arXiv:2406.06513v3, Section 1 |
| rt(A_k) = 2 or 7/3 | ARS Theorem 1 |
| rt(A_F) = 7/3 | ARS Theorem 11 |
| Tribonacci case 7/3 | ARS Theorem 13 |
| The Section 4 sentence | ARS Section 4, quoted word for word (`project:STATEMENT.md`; VERIFY check 1) |
| h and "h(a) is (7/3)+-free" | ARS Lemma 5; Karhumäki–Shallit Lemma 8 (ii) |
| x = pμ(y) for 7/3-free x | ARS Lemma 7; Rampersad–Shallit–Shur Theorem 1 |
| μ^i(0), μ^i(1) are factors | ARS Corollary 8 |
| Lexicographically least 7/3-free word starting with 1 is t̄ | ARS Lemma 9 |
| Orbit-closure lemma for addable systems | ARS Lemma 10 |
| Thue–Morse word has no factor of exponent above 2 | ARS Section 1 |
| Pell digit conditions | Baranwal–Shallit Section 2.1 |
| Pell addition automaton | Baranwal–Shallit Section 2.2 |
| Definition of α-substitutive | Durand Definition 2 |
| Main theorem | Durand Theorem 1 |
| Erasing morphisms fail | Durand, example after Corollary 6 |

## VERIFY issues (round 1) and where the paper fixes them

| Issue | Fix |
|---|---|
| W1. Step 4 names an erasing substitution | Section 4: the paragraph before Lemma 8 explains why A → AAB, B → A needs erasure; Lemma 8 gives the non-erasing substitution with a full proof and the eigenvalue; Remark 9 and `checks/prefix.py` check it numerically |
| W2. State the kind of proof | Abstract ("computer-assisted ... published lemmas"); Section 1, "Kind of result"; Section 6, "Limits"; README tier line |
| W3. Search command needs `-Xss512m`; wrong header comment | `checks/search/Sqf.java` header now says "no square" over K letters and gives the command with `-Xss512m`; `checks/README.md` gives the same command |
| W4. Numeration system wording; δ(q0,0) = q0 | Section 2: condition 1 (last digit 0 or 1), condition 2, and the paragraph after Definition 2 on adding a new initial state |
| W5. Controls | Section 5, "Controls": the unbounded Walnut control that ran out of memory, the bounded Walnut controls, and the 32 controls of `checks/controls.py` |
| W6. Scope and significance | Abstract and Section 1 ("The method is the method of ARS, applied to one more numeration system"; general question open); Section 6; attainment via the factor at position 8 (Corollary 6) |
