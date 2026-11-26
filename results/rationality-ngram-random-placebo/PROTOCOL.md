# Protocol: random-word placebo for the 1980 "rationality reversal"

Pre-registered on 2026-11-26, before any placebo or test statistic was computed.
At commit time, the only data seen are: the authors' word lists and their pickled
5000-word count tables (`jbollen/rise_and_fall_of_rationality_in_language`), a few
printed rows of those tables (`an`, `science`, `god` in 1850/1980/2019), and the
token names in the first lines of some v3 shards (to debug the extractor).

## 1. Claim under test

Scheffer, van de Leemput, Weinans, Bollen, PNAS 118(51) e2107848118 (2021): in Google
Books, the frequency of "rationality" words relative to "intuition" words rose from 1850
and reversed in the 1980s. The test asks one question: is the 1980 turn of this ratio
more extreme than the turn of word-set pairs that are drawn at random but matched in
frequency, part of speech, and fiction skew? If not, a change in corpus composition
(the fiction share) is sufficient to give a turn of this size.

## 2. Data

- Google Books Ngram v3 (version 20200217), 1-grams, corpora `eng` (24 shards) and
  `eng-fiction` (1 shard), plus their `totalcounts-1` files, from
  `https://storage.googleapis.com/books/ngrams/books/20200217/`. License CC BY 3.0.
- Years 1850-2019 (170 years). Count = match_count.
- Word count `n_w(t)`: the sum of the untagged 1-gram counts of all case variants whose
  lowercase form is `w` (case-insensitive), alphabetic forms only (`[A-Za-z]+`).
- Relative frequency `p_w(t) = n_w(t) / N(t)`, with `N(t)` from `totalcounts-1`.
- Non-fiction: `n_w(t) = n_w^eng(t) - n_w^fic(t)`, `N = N^eng - N^fic`. This corpus is used
  only if no pool or flag word has a negative non-fiction count in any year (a test that
  eng-fiction is a subset of eng). If the test fails, the non-fiction analyses are
  dropped and the failure is reported.
- POS tags: from the tagged 1-grams (`word_NOUN`, ...), summed over case variants and
  over 1850-2019 in `eng`. The dominant tag among NOUN, VERB, ADJ, ADV gives the class.
  If the sum of all other tags is larger than the largest of these four, class = OTHER.

## 3. Word sets

- Rationality set A: the authors' `science` + `quantification` lists (31 words).
  Intuition set B: the authors' `belief` + `senses` lists (48 words). The lists are
  copied from `Rise_fall_rationality_analysis_Figs.ipynb`, cells 6 and 8.
- As the authors do, a word is used only if it is in their 5000 most frequent English
  words (`most_frequent_words.pkl`). This gives |A| = 25 and |B| = 45.

## 4. Statistic

- `L(t) = ln(mean_{w in A} p_w(t)) - ln(mean_{w in B} p_w(t))`, t = 1850..2019.
  (The authors' ratio of mean `an`-scaled frequencies is `exp(L)`; the scaling cancels.)
- Fit by OLS: `L(t) = a + b (t - 1980) + g max(0, t - 1980)`.
- Primary statistic: `g` (change of slope at 1980). The claim predicts `g < 0`.
- Descriptive: `b`, `b + g`, "reversal" = (`b > 0` and `b + g < 0`), and the best hinge
  year `tau*` (grid 1900..2000, minimum SSE of the same model with 1980 replaced by tau).

## 5. Placebo pool and matching

- Pool: lowercase alphabetic words of length >= 2 that (i) are among the 20,000 words
  with the largest case-insensitive `eng` count 1850-2019, after filters (ii)-(iv);
  (ii) have a lowercase-form share >= 0.5 of their case-insensitive count (this removes
  most names and acronyms); (iii) have `n_w(t) > 0` in every year 1850-2019 in `eng`
  and in `eng-fiction`; (iv) are not in any of the 79 words of the A and B lists.
- Word features: `F_w = log10(mean_t p_w(t))` in `eng`; POS class; fiction skew
  `S_w = ln(sum_{1850..1974} n_w^fic / sum N^fic) - ln(sum_{1850..1974} n_w^eng / sum N^eng)`.
- Control FP (frequency + POS): for each flag word, candidates are the K = 40 pool words
  in the same POS class with the smallest `|F_w - F_flag|`. One candidate is drawn
  uniformly. A placebo pair (A', B') has one draw per flag word; a word is not used
  twice in one pair (redraw on collision).
- Control FPS (frequency + POS + fiction skew): as FP, but the distance is
  `sqrt(((F_w - F_flag)/sd_F)^2 + ((S_w - S_flag)/sd_S)^2)`, with `sd` over the pool.
- N = 10,000 placebo pairs per control. RNG: `numpy.random.default_rng`, seed 20261126
  for FP and 20261127 for FPS. The same pairs are evaluated on all corpora.

## 6. Tests and decision rule

- Primary test: corpus `eng`, control FPS, statistic `g`. One-sided p-value
  `p = (1 + #{g' <= g_obs}) / (N + 1)`. Threshold alpha = 0.05.
  - p < 0.05: SUPPORT. The 1980 turn is more extreme than in 95% of fiction-skew-matched
    random pairs. Fiction-skew composition is not sufficient to explain it.
  - p >= 0.05: REFUTATION of specificity. The turn is not distinguishable from the turns
    of matched random pairs. Composition is sufficient to give a turn of this size.
- Secondary tests (reported with their p-values, no multiplicity correction, they do not
  change the primary verdict): `eng` FP; `eng-fiction` FP and FPS; non-fiction FP and
  FPS; label shuffle on `eng` (10,000 random splits of the 70 flag words into 25 and 45,
  seed 20261128).
- Descriptive for each control and corpus: the share of placebo pairs with a reversal,
  and the share with `tau*` in 1975..1990.

## 7. Power and known-answer checks

- Power: for the first 1,000 FPS placebo pairs on `eng`, add `d max(0, t - 1980)` to
  `L(t)` with `d = g_obs` and `d = g_obs / 2`, refit, and report the share of fitted `g`
  below the 5% quantile of the 10,000 null `g` values (seed 20261129 not needed; the
  first 1,000 pairs are used). Check: the refitted `g` minus the null `g` equals `d`
  to 1e-9.
- Reproduction check: correlation between our `exp(L(t))` and the authors' ratio from
  `words5000eng_all.pkl` (mean of the A words / mean of the B words, raw counts),
  1850-2019. If r < 0.95, the result is reported, the cause is investigated and
  described, and the tests still run on our data.
- Extraction check: for 5 words, our 1850-2019 counts are compared with the authors'
  table (expected to be close but not necessarily equal; the ratio is reported).

## 8. Outputs

`checks/analysis.py` writes `data/results.json`. `checks/rerun.py` streams the raw
data again, re-runs the analysis, and compares every number with `data/expected.json`.
