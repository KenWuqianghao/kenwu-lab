# Numbers in the paper and their sources

Sources: `checks/expected/verify_A.txt` (V), `checks/expected/crosscheck_A.txt` (X),
`checks/expected/independent_check_A.txt` (I), `checks/expected/prefix_check_A.txt` (P),
`RESULT.md` and `STATEMENT.md` of the problem folder (R), arXiv:2611.13676v1 (S).
V, X, I and P were rerun on 2026-11-26 and equal the saved outputs except the time lines.

| Number in the paper | Value | Source |
|---|---|---|
| Λ | 2.0559673967 | V line "Lam = 2.0559673967128187031"; R |
| q = 1/(3 − Λ) | 1.0592854490 | V "q = 1/(3-Lam) = 1.05928544895"; R |
| E*(u₉) = 1 + q | 2.0592854490 | V "E*(u_9) = 1 + q = 2.05928544895"; R |
| letter lengths h | 2, 3, 1, 2, 4, 6, 11, 19, 36 | V "h = [...]" |
| RT(C₂), RT(C₃), RT(C₄) | 2.70710678, 2.25876324, 2.1197196907 | S, pages 1 and 4 |
| modulus of other roots of P5 | ≤ 0.8886 | V "modulus <= 0.888584" |
| real root β of Q4 | 1.9276 | I "max \|Q4 root\| = 1.927562" |
| prefix φ²¹(0), its length, certified length | 2 310 194; 4153 | V line 3 |
| two-letter factors of u₉, in φ⁹(0) | 17; j0 = 9 | V line 3 |
| multi nodes and their lengths | 7; 0, 1, 3, 7, 15, 31, 63 | V "multi-extension bispecial factors" |
| seeds and their lengths | 16; 1, 2, 2, 4, 4, 8, 8, 16, 16, 32, 32, 64, 64, 127, 128, 128 | V "chain seeds" |
| direct bispecials of u of length ≤ 40 | 36 | V "direct 36, tree 36" |
| factors from multi nodes | 51 | V "finite part: 51" |
| nonempty 0-free bispecial factors of z | 15 | V "0-free bispecial factors of z: 15" |
| return words per seed | 9 | V (check "seed has 9 return words" passes); I "exactly 9 return words" |
| period of the chain types | 8, from n = 0 | V "preperiod 0, period 8" (all 16 seeds) |
| exact chain check | n ≤ 60 (V); n ≤ 1000 (I) | V "exact up to n=60"; I "n <= 1000" |
| pairs with κ_Λ > 0 / = 0 | 142 / 2 | V: κ_Λ = 0 for 1/9 return words on seeds 1 and 127, 0/9 on the other 14 (16 × 9 = 144) |
| smallest nonzero κ_Λ | 2.14 | V "min kappa_Lam(nonzero)=2.14"; I "2.1400329" |
| min c_i where κ_Λ = 0 | 2/5 | V "c_i = 2/5 (exact min)" |
| largest ε in the two critical pairs | 0.5454 | V "eps = 0.545427" (seed 1, m = 3) and "eps = 0.330842" (seed 127, m = 0) |
| ε ρ³ < 2/5 | 0.383 | computed: 0.545427 × 0.888584³ = 0.3827 |
| ε ρ⁶⁰ < 2·10⁻³ | 1.46·10⁻³ | computed with max ε = 1.7489281 (I): 1.7489281 × 0.888584⁶⁰ |
| ε ρ¹⁰⁰⁰ < 10⁻⁵⁰ | 8.7·10⁻⁵² | computed: 1.7489281 × 0.888584¹⁰⁰⁰ |
| largest ratio met | 1.0592854490 at seed 127, n = 60 | V "largest ratio" line |
| brute-force bispecials of z, length ≤ 60 | 64 | X "(a) ... 64; predicted: 64" |
| predicted factors confirmed, length ≤ 3000 | 149 | X "149/149" |
| brute-force bispecials of u, length ≤ 300 | 75 | I |
| brute-force bispecials of z, length ≤ 2000 | 146 | I |
| certified ratios and the largest one | 125; 18/17 | I |
| prefix of z: letters of u, letters of z | 3 000 000; 9 727 357 | P line 1 |
| distinct nonempty palindromes | 9 727 357 | P line 2 |
| largest exponent in the prefix | 3684955/1789434 ≈ 2.0592852265 | P line 3 |
| figure bands | k = 0, …, 20 | P (the band k = 21 is cut by the end of the prefix and is not drawn) |
| search survivors on 1200 letters of u₉ | 3 | R ("3 candidates (A, B, C) survive u-prefix 1200", LOG.md) |
| date of the last novelty search | 2026-11-25 | arXiv API queries in the write session (author and keyword queries, newest first: no newer paper than the source of 2026-11-10); PRIOR_ART.md (2026-11-24); VERIFY.md (2026-11-25) |

## VERIFY.md issues and where the paper fixes them

| Issue (VERIFY.md, round 1) | Fix |
|---|---|
| 1. Cited theorems must be listed as assumptions; no Lean proof | Paper Section 2 (T1)–(T3); Section 6 "Limits", item 1 and item 3; status line after the abstract. README "What the proof assumes". |
| 2. Tail bound uses floating point, not interval arithmetic | Paper Section 6 "Limits", item 2, with the margins and the n ≤ 1000 exact run of `independent_check.py`; Section 5, item 1. |
| 3. The fact "exactly 9 return words" is not necessary | `checks/verify.py` now certifies the return words of each seed from the prefix (longest window without an occurrence). Paper Section 3, paragraph "Return words of the seeds"; (T3) no longer lists the fact. |
| 4. No claim of three distinct words | Paper Section 5, paragraph "Other projections": we did not check that the languages differ, so we do not claim three distinct words. |

## Clean-copy rerun (2026-11-26)

`release/` was copied to `/tmp/rwclean/rich-words-five-letters`. A new venv
(`uv venv --python 3.13`) was put first on `PATH`, and `bash checks/ci.sh` ran under
`run-heavy`. Output:

```
RESULT: ALL CHECKS PASSED
ok: checks/out/verify_A.txt matches checks/expected/verify_A.txt
RESULT: ALL CHECKS PASSED
ok: checks/out/verify_B.txt matches checks/expected/verify_B.txt
RESULT: ALL CHECKS PASSED
ok: checks/out/verify_C.txt matches checks/expected/verify_C.txt
ok: checks/out/crosscheck_A.txt matches checks/expected/crosscheck_A.txt
ok: checks/out/independent_check_A.txt matches checks/expected/independent_check_A.txt
ok: checks/out/prefix_check_A.txt matches checks/expected/prefix_check_A.txt
ci: all checks passed
real 126.96   user 117.68   sys 4.37
```

`python3 /Users/kenwu/research/kenwu-lab/tools/check_result.py /tmp/rwclean/rich-words-five-letters`
printed `ok: 1 result(s)`.
