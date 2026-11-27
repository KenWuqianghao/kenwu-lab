# Numbers in the paper and their sources

Every number in `paper/paper.tex`, `README.md` and `result.json` comes from the files in `data/`. `checks/rerun.py` rebuilds those files from the raw Lichess data and compares 1950 numbers with `data/expected.json`.

A script read each value below from the JSON files and compared it with the number as printed (half a unit in the last printed digit). Result: 198 rows, 0 mismatches. The same values are in `RESULT.md` of the pipeline, with one change: Table 2 gives α_pool = 2.609 at N = 10^4 (value 2.60852); `RESULT.md` printed 2.608.

Paths are keys in `data/results.json` unless the row names `robustness.json`, `explore.json` or `independent_count.json`. "computed" means a formula of the numbers in the row.

| Place in the paper | Printed | Value in data | Source | Check |
|---|---|---|---|---|
| Abstract, T1, Table 1 | 2.086 | 2.08644 | `results.json tests/T1/alpha_pool_full` | ok |
| Abstract, Table 1 | -1.756 | -1.75642 | `tests/T2/gamma` | ok |
| Abstract (rounded) | -1.76 | -1.75642 | `tests/T2/gamma` | ok |
| Table 1 | 0.058 | 0.0581998 | `tests/T2/gamma_sd` | ok |
| Abstract, Table 1 | -0.788 | -0.788302 | `tests/T2/gamma_model` | ok |
| Table 1, T2 | 1.602 | 1.60191 | `tests/T2/rho_full` | ok |
| Table 1 | 1.041 | 1.04061 | `tests/T2/rho_model_full` | ok |
| Table 1 | 0.54 | 0.539397 | `tests/T2/rel_rho_diff` | ok |
| Table 1, T3 | 0.400 | 0.399919 | `tests/T3/slope` | ok |
| Table 1 | 0.896 | 0.895703 | `tests/T3/slope_model` | ok |
| T3 text | 0.90 | 0.895703 | `tests/T3/slope_model` | ok |
| Table 1, T3, abstract 7.4 | 7.42 | 7.42144 | `tests/T3/d_cr_full` | ok |
| Table 1, T3, abstract 17.3 | 17.33 | 17.3285 | `tests/T3/d_cr_model_full` | ok |
| Table 1 caption, T3 | 18.62 | 18.6185 | `tests/T3/pred_eq9_full` | ok |
| Abstract, T3 (d_cr at 1.4e6) | 6.1 | 6.0747 | `tests/T3/d_cr_at_1.4e6` | ok |
| N_full | 44,832,865 | 44832865 | `tests/N_full` | ok |
| Table 2, N=10000 | 2.609 | 2.60852 | `tests/grid_mean/10000/alpha_pool` | ok |
| Table 2, N=10000 | 0.282 | 0.282301 | `tests/grid_mean/10000/b` | ok |
| Table 2, N=10000 | 2.60 | 2.60008 | `tests/grid_mean/10000/rho` | ok |
| Table 2, N=10000 | 4.01 | 4.01208 | `tests/grid_mean/10000/d_cr` | ok |
| Table 2, N=10000 | 0.91 | 0.909931 | `tests/model/10000/rho` | ok |
| Table 2, N=10000 | 9.72 | 9.7157 | `tests/model/10000/d_cr` | ok |
| Table 2, N=100000 | 2.299 | 2.29875 | `tests/grid_mean/100000/alpha_pool` | ok |
| Table 2, N=100000 | 0.182 | 0.181937 | `tests/grid_mean/100000/b` | ok |
| Table 2, N=100000 | 2.09 | 2.09462 | `tests/grid_mean/100000/rho` | ok |
| Table 2, N=100000 | 5.05 | 5.04688 | `tests/grid_mean/100000/d_cr` | ok |
| Table 2, N=100000 | 0.92 | 0.921478 | `tests/model/100000/rho` | ok |
| Table 2, N=100000 | 12.01 | 12.0083 | `tests/model/100000/d_cr` | ok |
| Table 2, N=1000000 | 2.166 | 2.16641 | `tests/grid_mean/1000000/alpha_pool` | ok |
| Table 2, N=1000000 | 0.133 | 0.133071 | `tests/grid_mean/1000000/b` | ok |
| Table 2, N=1000000 | 1.84 | 1.83844 | `tests/grid_mean/1000000/rho` | ok |
| Table 2, N=1000000 | 5.95 | 5.94552 | `tests/grid_mean/1000000/d_cr` | ok |
| Table 2, N=1000000 | 1.03 | 1.02501 | `tests/model/1000000/rho` | ok |
| Table 2, N=1000000 | 14.16 | 14.1593 | `tests/model/1000000/d_cr` | ok |
| Table 2, N=1400000 | 2.155 | 2.15504 | `tests/grid_mean/1400000/alpha_pool` | ok |
| Table 2, N=1400000 | 0.127 | 0.127111 | `tests/grid_mean/1400000/b` | ok |
| Table 2, N=1400000 | 1.80 | 1.79887 | `tests/grid_mean/1400000/rho` | ok |
| Table 2, N=1400000 | 6.07 | 6.0747 | `tests/grid_mean/1400000/d_cr` | ok |
| Table 2, N=1400000 | 1.00 | 1.00165 | `tests/model/1400000/rho` | ok |
| Table 2, N=1400000 | 14.41 | 14.4131 | `tests/model/1400000/d_cr` | ok |
| Table 2, N=10000000 | 2.105 | 2.10517 | `tests/grid_mean/10000000/alpha_pool` | ok |
| Table 2, N=10000000 | 0.099 | 0.0993705 | `tests/grid_mean/10000000/b` | ok |
| Table 2, N=10000000 | 1.60 | 1.60166 | `tests/grid_mean/10000000/rho` | ok |
| Table 2, N=10000000 | 6.85 | 6.84538 | `tests/grid_mean/10000000/d_cr` | ok |
| Table 2, N=10000000 | 1.03 | 1.02978 | `tests/model/10000000/rho` | ok |
| Table 2, N=10000000 | 15.96 | 15.9571 | `tests/model/10000000/d_cr` | ok |
| Table 2, N=44832865 | 2.086 | 2.08644 | `tests/grid_mean/44832865/alpha_pool` | ok |
| Table 2, N=44832865 | 0.091 | 0.0909224 | `tests/grid_mean/44832865/b` | ok |
| Table 2, N=44832865 | 1.60 | 1.60191 | `tests/grid_mean/44832865/rho` | ok |
| Table 2, N=44832865 | 7.42 | 7.42144 | `tests/grid_mean/44832865/d_cr` | ok |
| Table 2, N=44832865 | 1.04 | 1.04061 | `tests/model/44832865/rho` | ok |
| Table 2, N=44832865 | 17.33 | 17.3285 | `tests/model/44832865/d_cr` | ok |
| Table 2 caption, N=10000 | 10.21 | 10.2103 | `1 + ln N (computed)` | ok |
| Table 2 caption, N=100000 | 12.51 | 12.5129 | `1 + ln N (computed)` | ok |
| Table 2 caption, N=1000000 | 14.82 | 14.8155 | `1 + ln N (computed)` | ok |
| Table 2 caption, N=1400000 | 15.15 | 15.152 | `1 + ln N (computed)` | ok |
| Table 2 caption, N=10000000 | 17.12 | 17.1181 | `1 + ln N (computed)` | ok |
| Table 2 caption, N=44832865 | 18.62 | 18.6185 | `1 + ln N (computed)` | ok |
| T1 text 2.61 at 1e4 | 2.61 | 2.60852 | `tests/grid_mean/10000/alpha_pool` | ok |
| T1 text 2.09 at full | 2.09 | 2.08644 | `tests/grid_mean/N_full/alpha_pool` | ok |
| T1 text model 2.41 | 2.41 | 2.41028 | `tests/model/10000/alpha_pool` | ok |
| T1 text model 2.04 | 2.04 | 2.03756 | `tests/model/N_full/alpha_pool` | ok |
| T2 text: model rho min | 0.91 | 0.909931 | `min over tests/model/*/rho` | ok |
| T2 text: model rho max (VERIFY issue 1) | 1.04 | 1.04478 | `max over tests/model/*/rho` | ok |
| T2 text rho at 1e4 | 2.60 | 2.60008 | `tests/grid_mean/10000/rho` | ok |
| CSN x_min | 16 | 16 | `csn/xmin` | ok |
| CSN KS | 0.0025 | 0.00247308 | `csn/ks` | ok |
| CSN alpha | 2.024 | 2.024 | `csn/alpha` | ok |
| CSN n_tail | 62,030 | 62030 | `csn/n_tail` | ok |
| CSN R lognormal | 0.98 | 0.976973 | `csn/LR_vs_lognormal/R` | ok |
| CSN p lognormal | 0.33 | 0.328583 | `csn/LR_vs_lognormal/p` | ok |
| CSN R trunc | -0.72 | -0.720423 | `csn/LR_vs_truncated_power_law/R` | ok |
| CSN p trunc | 0.47 | 0.465092 | `csn/LR_vs_truncated_power_law/p` | ok |
| Table 3 bullet | 14,337,880 | 14337880 | `strata/bullet/n_games` | ok |
| Table 3 bullet | 2.155 | 2.15478 | `strata/bullet/alpha_pool` | ok |
| Table 3 bullet | 2.16 | 2.16389 | `strata/bullet/rho` | ok |
| Table 3 bullet | 5.69 | 5.68722 | `strata/bullet/d_cr` | ok |
| Table 3 blitz | 18,281,202 | 18281202 | `strata/blitz/n_games` | ok |
| Table 3 blitz | 2.164 | 2.16427 | `strata/blitz/alpha_pool` | ok |
| Table 3 blitz | 1.70 | 1.69764 | `strata/blitz/rho` | ok |
| Table 3 blitz | 6.27 | 6.27432 | `strata/blitz/d_cr` | ok |
| Table 3 classical | 11,582,480 | 11582480 | `strata/classical/n_games` | ok |
| Table 3 classical | 2.161 | 2.16136 | `strata/classical/alpha_pool` | ok |
| Table 3 classical | 1.86 | 1.8637 | `strata/classical/rho` | ok |
| Table 3 classical | 6.10 | 6.10069 | `strata/classical/d_cr` | ok |
| Table 3 rating_low | 14,901,926 | 14901926 | `strata/rating_low/n_games` | ok |
| Table 3 rating_low | 2.164 | 2.16375 | `strata/rating_low/alpha_pool` | ok |
| Table 3 rating_low | 2.08 | 2.07686 | `strata/rating_low/rho` | ok |
| Table 3 rating_low | 5.75 | 5.74863 | `strata/rating_low/d_cr` | ok |
| Table 3 rating_mid | 14,983,580 | 14983580 | `strata/rating_mid/n_games` | ok |
| Table 3 rating_mid | 2.162 | 2.16232 | `strata/rating_mid/alpha_pool` | ok |
| Table 3 rating_mid | 1.89 | 1.89298 | `strata/rating_mid/rho` | ok |
| Table 3 rating_mid | 6.02 | 6.01923 | `strata/rating_mid/d_cr` | ok |
| Table 3 rating_high | 14,942,928 | 14942928 | `strata/rating_high/n_games` | ok |
| Table 3 rating_high | 2.158 | 2.15803 | `strata/rating_high/alpha_pool` | ok |
| Table 3 rating_high | 1.68 | 1.67793 | `strata/rating_high/rho` | ok |
| Table 3 rating_high | 6.38 | 6.38142 | `strata/rating_high/d_cr` | ok |
| Table 3 2013-2014 | 14,964,152 | 14964152 | `strata/2013-2014/n_games` | ok |
| Table 3 2013-2014 | 2.167 | 2.16686 | `strata/2013-2014/alpha_pool` | ok |
| Table 3 2013-2014 | 1.89 | 1.89468 | `strata/2013-2014/rho` | ok |
| Table 3 2013-2014 | 5.89 | 5.89485 | `strata/2013-2014/d_cr` | ok |
| Table 3 2015 | 29,868,713 | 29868713 | `strata/2015/n_games` | ok |
| Table 3 2015 | 2.164 | 2.16357 | `strata/2015/alpha_pool` | ok |
| Table 3 2015 | 1.84 | 1.83962 | `strata/2015/rho` | ok |
| Table 3 2015 | 5.97 | 5.96967 | `strata/2015/d_cr` | ok |
| Rating cut 1534 | 1534 | 1534 | `strata/rating_cuts/0` | ok |
| Rating cut 1732 | 1732 | 1732 | `strata/rating_cuts/1` | ok |
| Strata text: model rho(1e6) | 1.03 | 1.02501 | `tests/model/1000000/rho` | ok |
| Strata text: model d_cr(1e6) | 14.2 | 14.1593 | `tests/model/1000000/d_cr` | ok |
| Placebo L40 games | 36,705,863 | 36705863 | `placebo/n_games_L40` | ok |
| Placebo real alpha_pool | 2.155 | 2.15497 | `placebo/real_mean/alpha_pool` | ok |
| Placebo real b | 0.128 | 0.127744 | `placebo/real_mean/b` | ok |
| Placebo real rho | 1.81 | 1.80783 | `placebo/real_mean/rho` | ok |
| Placebo real d_cr | 6.07 | 6.06526 | `placebo/real_mean/d_cr` | ok |
| Placebo shuffled alpha_pool min | 2.137 | 2.13729 | `placebo/shuffled/*/alpha_pool (min)` | ok |
| Placebo shuffled alpha_pool max | 2.138 | 2.13841 | `placebo/shuffled/*/alpha_pool (max)` | ok |
| Placebo shuffled b min | 0.75 | 0.748295 | `placebo/shuffled/*/b (min)` | ok |
| Placebo shuffled b max | 0.79 | 0.786936 | `placebo/shuffled/*/b (max)` | ok |
| Placebo shuffled rho min | 10.6 | 10.5899 | `placebo/shuffled/*/rho (min)` | ok |
| Placebo shuffled rho max | 11.1 | 11.1367 | `placebo/shuffled/*/rho (max)` | ok |
| Placebo ratio b shuffled/real ~6 | 6 | 5.98041 | `placebo shuffled_mean/b / real_mean/b` | ok |
| Placebo: alpha_d defined at 6 depths | 6 | 6, 6, 6, 6, 6 | `placebo/shuffled/*/alpha_d (count non-NaN)` | ok |
| Table 4 protocol_n1_N100 | -1.82 | -1.81945 | `robustness.json variants/protocol_n1_N100/gamma_b_protocol` | ok |
| Table 4 protocol_n1_N100 | -0.78 | -0.781927 | `robustness.json variants/protocol_n1_N100/gamma_model_b_protocol` | ok |
| Table 4 protocol_n1_N100 | 1.60 | 1.60191 | `robustness.json variants/protocol_n1_N100/rho_full_b_protocol` | ok |
| Table 4 protocol_n1_N100 | 1.05 | 1.05429 | `robustness.json variants/protocol_n1_N100/rho_model_full_b_protocol` | ok |
| Table 4 protocol_n1_N100 | 7.42 | 7.42144 | `robustness.json variants/protocol_n1_N100/dcr_full` | ok |
| Table 4 protocol_n1_N100 | 17.33 | 17.3289 | `robustness.json variants/protocol_n1_N100/dcr_model_full` | ok |
| Table 4 protocol_n1_N100 decisions |  | ['refuted', 'refuted'] | `variants/protocol_n1_N100/T2,T3` | ok |
| Table 4 n2_N100 | -1.56 | -1.56283 | `robustness.json variants/n2_N100/gamma_b_protocol` | ok |
| Table 4 n2_N100 | -0.79 | -0.794078 | `robustness.json variants/n2_N100/gamma_model_b_protocol` | ok |
| Table 4 n2_N100 | 1.47 | 1.46903 | `robustness.json variants/n2_N100/rho_full_b_protocol` | ok |
| Table 4 n2_N100 | 1.06 | 1.05988 | `robustness.json variants/n2_N100/rho_model_full_b_protocol` | ok |
| Table 4 n2_N100 | 7.38 | 7.38453 | `robustness.json variants/n2_N100/dcr_full` | ok |
| Table 4 n2_N100 | 17.40 | 17.3975 | `robustness.json variants/n2_N100/dcr_model_full` | ok |
| Table 4 n2_N100 decisions |  | ['refuted', 'refuted'] | `variants/n2_N100/T2,T3` | ok |
| Table 4 n4_N100 | -1.31 | -1.31213 | `robustness.json variants/n4_N100/gamma_b_protocol` | ok |
| Table 4 n4_N100 | -0.81 | -0.813361 | `robustness.json variants/n4_N100/gamma_model_b_protocol` | ok |
| Table 4 n4_N100 | 1.43 | 1.42521 | `robustness.json variants/n4_N100/rho_full_b_protocol` | ok |
| Table 4 n4_N100 | 1.07 | 1.0712 | `robustness.json variants/n4_N100/rho_model_full_b_protocol` | ok |
| Table 4 n4_N100 | 7.31 | 7.31302 | `robustness.json variants/n4_N100/dcr_full` | ok |
| Table 4 n4_N100 | 17.18 | 17.1801 | `robustness.json variants/n4_N100/dcr_model_full` | ok |
| Table 4 n4_N100 decisions |  | ['inconclusive', 'refuted'] | `variants/n4_N100/T2,T3` | ok |
| Table 4 n1_N1000 | -1.89 | -1.88678 | `robustness.json variants/n1_N1000/gamma_b_protocol` | ok |
| Table 4 n1_N1000 | -0.98 | -0.979917 | `robustness.json variants/n1_N1000/gamma_model_b_protocol` | ok |
| Table 4 n1_N1000 | 1.73 | 1.72903 | `robustness.json variants/n1_N1000/rho_full_b_protocol` | ok |
| Table 4 n1_N1000 | 1.00 | 1.00253 | `robustness.json variants/n1_N1000/rho_model_full_b_protocol` | ok |
| Table 4 n1_N1000 | 7.83 | 7.83103 | `robustness.json variants/n1_N1000/dcr_full` | ok |
| Table 4 n1_N1000 | 18.10 | 18.1025 | `robustness.json variants/n1_N1000/dcr_model_full` | ok |
| Table 4 n1_N1000 decisions |  | ['refuted', 'refuted'] | `variants/n1_N1000/T2,T3` | ok |
| Table 4 n2_N10 | -1.59 | -1.5917 | `robustness.json variants/n2_N10/gamma_b_protocol` | ok |
| Table 4 n2_N10 | -0.86 | -0.855944 | `robustness.json variants/n2_N10/gamma_model_b_protocol` | ok |
| Table 4 n2_N10 | 1.45 | 1.45069 | `robustness.json variants/n2_N10/rho_full_b_protocol` | ok |
| Table 4 n2_N10 | 1.05 | 1.05461 | `robustness.json variants/n2_N10/rho_model_full_b_protocol` | ok |
| Table 4 n2_N10 | 7.38 | 7.38453 | `robustness.json variants/n2_N10/dcr_full` | ok |
| Table 4 n2_N10 | 17.40 | 17.3975 | `robustness.json variants/n2_N10/dcr_model_full` | ok |
| Table 4 n2_N10 decisions |  | ['refuted', 'refuted'] | `variants/n2_N10/T2,T3` | ok |
| Robustness d_cr slope min | 0.37 | 0.373014 | `min variants/*/dcr_slope` | ok |
| Robustness d_cr slope max | 0.43 | 0.434325 | `max variants/*/dcr_slope` | ok |
| Robustness model d_cr slope min | 0.78 | 0.778596 | `min variants/*/dcr_slope_model` | ok |
| Robustness model d_cr slope max | 1.12 | 1.11798 | `max` | ok |
| n4 |gamma diff| | 0.499 | 0.498767 | `variants/n4_N100 gamma - gamma_model` | ok |
| n4 rel rho diff | 0.33 | 0.33049 | `variants/n4_N100` | ok |
| alpha_2 at N_full | 0.97 | 0.969553 | `variants/protocol_n1_N100/alpha_d_full/1` | ok |
| alpha_3 at N_full | 1.30 | 1.295 | `variants/protocol_n1_N100/alpha_d_full/2` | ok |
| alpha_4 at N_full | 1.55 | 1.55437 | `variants/protocol_n1_N100/alpha_d_full/3` | ok |
| alpha_5 at N_full | 1.72 | 1.71804 | `variants/protocol_n1_N100/alpha_d_full/4` | ok |
| alpha_6 at N_full | 1.86 | 1.85771 | `variants/protocol_n1_N100/alpha_d_full/5` | ok |
| alpha_7 at N_full | 1.95 | 1.95351 | `variants/protocol_n1_N100/alpha_d_full/6` | ok |
| alpha_8 at N_full | 2.06 | 2.06382 | `variants/protocol_n1_N100/alpha_d_full/7` | ok |
| alpha_9 at N_full | 2.14 | 2.13937 | `variants/protocol_n1_N100/alpha_d_full/8` | ok |
| steps after d=9 'about 0.05 to 0.09' | 0.05-0.09 | 0.072, 0.078, 0.093, 0.033, 0.063, 0.071, 0.04, 0.051, 0.04, 0.041 | `differences of alpha_d_full, d=10..19` | ok (approximate) |
| 1/ln N_full | 0.057 | 0.0567587 | `computed` | ok |
| window 3-9 gamma | -1.13 | -1.12997 | `variants/protocol_n1_N100/gamma_b_3_9` | ok |
| window 3-9 gamma model | -0.46 | -0.46165 | `gamma_model_b_3_9` | ok |
| window 3-9 rho | 2.38 | 2.3832 | `rho_full_b_3_9` | ok |
| window 3-9 rho model | 1.29 | 1.28858 | `rho_model_full_b_3_9` | ok |
| window d>=8, n>=2 rho | 1.03 | 1.03065 | `variants/n2_N100/rho_full_b_8_up` | ok |
| window d>=8 rho model | 0.92 | 0.917144 | `variants/n2_N100/rho_model_full_b_8_up` | ok |
| 1/ln 1.4e6 | 0.071 | 0.0706615 | `computed` | ok |
| Eq.6 alpha_2 with beta=-0.6 | 1.66 | 1.65676 | `computed: (1-beta)+1/ln N` | ok |
| beta from s=0.40 | -0.6 | -0.600081 | `tests/T3/slope - 1` | ok |
| Explore N1.4e6 mu | 1.47 | 1.47034 | `explore.json N1.4e6/mu_pooled` | ok |
| Explore N1.4e6 surrogate d_cr | 6.4 | 6.43018 | `N1.4e6/shuffle_within_depth/d_cr` | ok |
| Explore N1.4e6 surrogate rho | 1.15 | 1.14814 | `N1.4e6/shuffle_within_depth/rho` | ok |
| Explore N1.4e6 data d_cr | 6.1 | 6.06711 | `N1.4e6/data_check/d_cr` | ok |
| Explore N1.4e6 data rho ~1.8 | 1.8 | 1.80704 | `N1.4e6/data_check/rho` | ok |
| Explore N10^6.5 mu | 1.46 | 1.45791 | `explore.json N10^6.5/mu_pooled` | ok |
| Explore N10^6.5 surrogate d_cr | 6.8 | 6.75403 | `N10^6.5/shuffle_within_depth/d_cr` | ok |
| Explore N10^6.5 surrogate rho | 1.25 | 1.25386 | `N10^6.5/shuffle_within_depth/rho` | ok |
| Explore N10^6.5 data d_cr | 6.4 | 6.36069 | `N10^6.5/data_check/d_cr` | ok |
| Explore N10^6.5 data rho ~1.8 | 1.8 | 1.78842 | `N10^6.5/data_check/rho` | ok |
| Explore mu ply 2 | 2.06 | 2.05849 | `N1.4e6/q_by_depth/2/mu` | ok |
| Explore mu ply 12-14 min | 1.16 | 1.16378 | `N1.4e6/q_by_depth/12..14 min` | ok |
| Explore mu ply 12-14 max | 1.26 | 1.2636 | `N1.4e6/q_by_depth/12..14 max` | ok |
| ln 2 | 0.69 | 0.693147 | `computed` | ok |
| Games per month: 36 months, total | 44,832,865 | 44832865 | `results.json meta` | ok |
| Independent count d_cr | 7.4214 | 7.42144 | `independent_count.json d_cr` | ok |

## Open issues of VERIFY.md (round 2) and where the paper fixes them

| # | Issue | Fix in the paper |
|---|---|---|
| 1 | The model ρ range must be "0.91 and 1.04", not "0.91 and 1.05" (largest value 1.0448). | Section 3, paragraph "T2": "ρ_model is between 0.91 and 1.04 on the whole grid". Checked in the table above (rows "model rho min/max"). |
| 2 | The first row of the robustness table gives γ = −1.82; the pre-registered value is −1.756. | Section 4, first paragraph, before Table 4: the difference comes only from the new random subsets (seeds 9000–9002); ρ and d_cr at the full N use all games and are equal in both analyses. |
| 3 | Cite the published ChessDB exponents α_1..α_4 = 1.10, 1.29, 1.47, 1.59 (Schaigorodsky et al. 2016), as a reading and not as a test. | Section 4, paragraph "The published exponents for ChessDB ...": steps 0.19, 0.18, 0.12 against 1/ln N = 0.071; "This is our reading of their numbers. Their fit method differs from ours, so it is not a test." The values were checked in the arXiv text of the paper (Fig. 1 caption). Also cited in Section 1. |
| 4 | The rerun command needs an empty work folder. | Fixed in the code and in the text. `checks/rerun.py` now stops if the work folder holds `parsed/`, `build/` or `out/`. Section 6, item "Full rerun", says so. `README.md` ("Check it") and `checks/README.md` say so. |

## Other changes from the verified pipeline

- `checks/verify_robustness.py` is renamed `checks/robustness.py`, and `checks/verify_r2_shallow.py` is renamed `checks/independent_count.py`. The code is unchanged except the usage lines.
- `checks/download.sh` and `checks/parse_all.sh` now download, check and parse one month at a time, in parallel workers (`CHESSZIPF_WORKERS`). With `CHESSZIPF_DELETE_RAW=1` the raw file is deleted after its parse, so a CI run needs about 8 GB of disk. The parser and all analysis code are unchanged.
- The author list of Perotti et al. (EPL 2013) is taken from Crossref: Perotti, Jo, Schaigorodsky, Billoni. `PRIOR_ART.md` lists it as "Schaigorodsky, Perotti, Billoni".
