# Checks

Run `bash checks/ci.sh` from the result folder. It runs `python3 -I checks/rerun.py`, which downloads the raw data into memory, computes every number of the paper, and compares the full set with `data/expected.json`. The comparison is exact: the JSON of the run must equal the stored JSON. The script prints `MATCH expected.json` and exits 0, or prints `MISMATCH expected.json` and exits 1.

`rerun.py` uses the Python standard library only. The Fisher tests use exact rational arithmetic (`fractions.Fraction`). The shuffle test uses `random.Random(20261128)` and 20,000 permutations.

To run from local copies of the raw files:

```sh
python3 -I checks/rerun.py --cache DIR
```

`DIR` must hold `s1985.json` ... `s2026.json` (one MLB Stats API response per season) and `cdc_births.csv`. A file that is missing from `DIR` is downloaded.

## Raw data

| File | Source |
|---|---|
| `sYYYY.json`, YYYY = 1985..2026 | `https://statsapi.mlb.com/api/v1/sports/1/players?season=YYYY` |
| `cdc_births.csv` | `https://raw.githubusercontent.com/jakevdp/data-CDCbirths/master/births.csv` |

The numbers of the paper come from a download on 2026-11-28. The MLB Stats API does not publish versions. A later correction of a birth date, a birth country or a debut date can change a count.

## What `data/expected.json` holds

| Key | Content | In the paper |
|---|---|---|
| `n_C`, `n_T`, `months_C`, `months_T` | cohort sizes and monthly counts | Table 1, Section 4 |
| `primary` | primary 2x2 table, log OR, CI, Fisher p, r_C | Section 4 |
| `placebo_split`, `placebo_months`, `shuffle_p_greater`, `known_answer` | pre-registered controls | Section 4 |
| `decision` | `SUPPORT` | Section 4 |
| `exploratory_age26` | debut before 26 (first exploratory variant) | Table 3 |
| `exploratory_verify_round1` | birth-year bins and single years, gap cohort, debut-age limits 22-27, players not born in the USA, month groups, leave one year out, pre-trend, US birth seasonality | Section 5, Tables 2 and 3 |

`release/NUMBERS.md` maps each number of the paper to its key.

## Independent recounts (`checks/verify/`)

An independent check wrote these scripts with its own code. CI does not run them.

| Script | Input | What it checks |
|---|---|---|
| `own_recount.py RAWDIR` | the 42 season files | primary table, placebos, monthly counts (needs scipy) |
| `retrosheet_recount.py biofile0.csv` | Retrosheet `biofile0.csv` from https://www.retrosheet.org/biofile.zip | primary table and gap cohort from a second source: 113/112 against 303/445, p = 0.0062 (needs scipy) |
| `round2_recount.py RAWDIR data/expected.json` | the 42 season files, `cdc_births.csv`, and `538_1994_2003.csv` (FiveThirtyEight `US_births_1994-2003_CDC_NCHS.csv`) | every exploratory number (standard library only) |

To fill `RAWDIR`, download each season URL above to `RAWDIR/sYYYY.json`, and the CDC file to `RAWDIR/cdc_births.csv`.

## Figure

`paper/figures/make_figure.py` draws Figure 1 from `data/expected.json`. It needs matplotlib (3.10.9 was used), which CI does not install.
