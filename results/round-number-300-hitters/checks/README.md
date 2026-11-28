# Checks

Run `bash checks/ci.sh` from the result folder. It installs scipy 1.18.1 (`checks/requirements.txt`) and runs `python3 -I checks/rerun.py`. The script downloads the raw files into `work/` in the result folder, computes every number of the paper, and compares the full output with `data/expected.json`. Integers and strings must be equal. Floats must agree to a relative tolerance of 1e-9, because the last bits of a p-value can depend on the platform. The script prints `MATCH expected.json` and exits 0, or prints `MISMATCH expected.json` and exits 1.

To keep the downloads in another folder, or to use local copies:

```sh
python3 -I checks/rerun.py --cache DIR
```

A file that is missing from `DIR` is downloaded. `DIR/raw/` holds `YYYYeve.zip`; `DIR/val/` holds `mlbYYYY.json`, `people-H.csv`, `Batting.csv` and `People.csv`.

Run time: 125 s on a Steam Deck (1 thread, fresh virtual environment, all downloads, 2026-11-28). A verification run on the same machine under load took 258 s. With the files in the cache, about 45 s.

## Raw data

| File | Source |
|---|---|
| `raw/YYYYeve.zip`, YYYY = 2009..2025 | `https://www.retrosheet.org/events/YYYYeve.zip` (SHA-256 of each file: `expected.json`, key `retrosheet_sha256`) |
| `val/mlbYYYY.json` | `https://statsapi.mlb.com/api/v1/stats?stats=season&group=hitting&season=YYYY&sportId=1&gameType=R&limit=3000&playerPool=ALL` |
| `val/people-H.csv`, H = 0..9, a..f | Chadwick register, commit `ba48ce101349a2156c7a5420f54d13e8ef3a4256` |
| `val/Batting.csv`, `val/People.csv` | Baseball Databank (Lahman) mirror `cbwinslow/baseballdatabank`, commit `8a908d51833ee99b56fce165c93dc99ee8886d6f` |

The MLB Stats API has no versions. A later correction can change `validation_mlb_api`. On 2026-11-28 one batter-season differed (`gonzl005`, 2022: 79 H in Retrosheet, 78 H in the API, 311 AB in both). The cause is not known.

## What `data/expected.json` holds

| Key | Content | In the paper |
|---|---|---|
| `retrosheet_sha256`, `n_rule_9_15b_reassigned` | file hashes; PAs changed by rule 9.15(b) (81) | Section 2, 4 |
| `validation_mlb_api`, `validation_lahman` | parsed (H, AB) against the official totals | Section 4 |
| `n_eligible`, `T1`, `S1_T1_official` | season-end counts, ratios, binomial p, CI; the same from MLB totals | Section 3.1, Table 1, Figure 1a |
| `L299`, `L300`, `LC`, `L299_walkers`, `T2_fisher_p`, `T3_fisher_p`, `C2_original_0_of_61_vs_heldout_fisher_two_sided` | last actual PA | Section 3.2 |
| `T4_B_below`, `T4_A_above`, `T4_hit_fisher_p`, `T4_walk_fisher_p` | selection control | Section 3.3 |
| `paper_comparisons` (P1–P6) | the paper's comparisons, post hoc | Section 3.1, 3.4, Table 2, Figure 1b |
| `exit_share_batter`, `exit_share_pa` | exit check: [ended at d, were at d] per displayed average d | Section 3.5 |

`NUMBERS.md` maps each number of the paper to its key.

## Independent recounts (`checks/verify/`)

A separate verification stage wrote these scripts with its own code. CI does not run them. They need scipy.

| Script | What it checks |
|---|---|
| `independent_check.py RAW LAH MLB FIX` | Own parser and own rule 9.15(b) detection. `RAW` = folder with `YYYYeve.zip`; `LAH` = folder with `Batting.csv`, `People.csv`; `MLB` = folder with `YYYY.json` (the MLB files renamed); the fourth argument turns on rule 9.15(b). Output: `out_rule_9_15b_fix.txt` (with the rule) and `out_no_fix.txt` (without). |
| `round2_check.py ROOT` | T1 from the MLB Stats API totals alone (reads `ROOT/work/val/mlbYYYY.json`), and every p-value, the CI and the Holm values from the counts. Output: `out_round2_check.txt`. |

`retrosheet_sha256.txt` holds the hashes of the Retrosheet files at the first verification.

## Figure

`paper/figures/make_figure.py` draws Figure 1 from `data/expected.json`. It needs matplotlib (3.11.2 was used). CI does not run it.
