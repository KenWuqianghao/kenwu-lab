# Third-party data and sources

No third-party data file is in this folder. `checks/rerun.py` downloads the raw data at run time. `data/expected.json` holds only derived counts and statistics.

| Source | Use | License or terms | Access date |
|---|---|---|---|
| MLB Stats API, `https://statsapi.mlb.com/api/v1/sports/1/players?season=YYYY`, seasons 1985-2026 | birth date, birth country and debut date of each MLB player | Public, no account. Copyright MLB Advanced Media. Terms for redistribution: Not confirmed, so the raw files are not included. | 2026-11-28 |
| CDC/NCHS natality counts by year, month and sex, 1969-2008, compiled by J. VanderPlas, `https://raw.githubusercontent.com/jakevdp/data-CDCbirths/master/births.csv` | expected odds ratio from US birth seasonality (exploratory) | US government data (public domain). The repository states no license. Not included; downloaded at run time. | 2026-11-28 |
| Retrosheet biographical file, `https://www.retrosheet.org/biofile.zip` | second-source recount (`checks/verify/retrosheet_recount.py`) | "The information used here was obtained free of charge from and is copyrighted by Retrosheet." Not included. | 2026-11-28 |
| FiveThirtyEight, `US_births_1994-2003_CDC_NCHS.csv` | second birth-count source for the seasonality check (`checks/verify/round2_recount.py`) | Not included. | 2026-11-28 |
| Little League release, October 2005, archived at `http://web.archive.org/web/20051223154010/http://www.littleleague.org:80/media/age_change_Oct05.asp` | July 31 for more than 55 years; April 30 from the 2006 season | quoted facts only | 2026-11-28 |
| Little League news, 13 November 2015, `https://www.littleleague.org/news/update-implementation-little-league-baseball-age-determination-date/` | August 31 from the 2018 season | quoted facts only | 2026-11-28 |
| G. Spira, "The Boys of Late Summer", Slate, 16 April 2008 | the 503/313 count and the May prediction | short quotation | 2026-11-28 |
| B. Jedlovec, Bill James Online, 4 November 2009, archived at `http://web.archive.org/web/20230531162307/https://www.billjamesonline.com/article1191/` | Dixie Youth change; school teams group by grade | facts only | 2026-11-28 |
| D. Siuda, Omni Calculator article (year not stated on the page) | statement that the question is open | short quotation | 2026-11-28 |
| Abstracts of Abel and Kruger (2005), Zhang et al. (2018), Herring et al. (2021), Hensley (2020); bibliographic record of Thompson et al. (1991); blog post of Collier (2016) | prior work | facts only | 2026-11-28 |

Code in this folder: `checks/rerun.py`, `checks/verify/*.py` and `paper/figures/make_figure.py` were written in this project. The paper and the README are original text.
