"""Check that each number in paper/paper.tex equals its source value.

Each entry gives the text in the paper, the source file and the value. JSON values are
formatted the way the paper prints them and must give the same text. Log values must appear in
the log. Every text must appear in paper/paper.tex. With --markdown, print the table of
release/NUMBERS.md. Usage: python3 checks/paper_numbers.py [--markdown]"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p)))
R, A, B = J("data/results.json"), J("data/addendum/addendum.json"), J("data/addendum/period_B.json")
LOG = lambda p: open(os.path.join(ROOT, "checks/independent", p)).read()
paper = open(os.path.join(ROOT, "paper/paper.tex")).read()
pp = lambda v: f"{100 * v:+.2f}"
se = lambda v: f"{100 * v:.2f}"
z = lambda v: f"{v:.2f}"
pct = lambda v: f"{100 * v:.2f}\\%"
n = lambda v: f"{v:,}".replace(",", "{,}")
nc = lambda v: f"{v:,}"
P, PB, RB = R["primary"], B["primary"], B["robustness"]

rows = [  # (what, text in paper, source, value as text)
 ("primary jump", "$+0.51$", "data/results.json primary.jump", f"${pp(P['jump'])}$"),
 ("primary SE", "(standard error 0.45", "primary.se", f"(standard error {se(P['se'])}"),
 ("primary CI", "$[-0.38, +1.39]$", "primary.ci", f"$[{pp(P['ci'][0])}, {pp(P['ci'][1])}]$"),
 ("primary left limit", "18.55\\%", "primary.left_limit", pct(P["left_limit"])),
 ("primary relative", "$+2.7\\%$", "primary.relative", f"${100*P['relative']:+.1f}\\%$"),
 ("primary n", "$n = 185{,}385$ (14,903 players)", "primary.n, players", f"$n = {n(P['n'])}$ ({nc(P['players'])} players)"),
 ("MDE", "& 1.26 &", "injection.mde_80pct_power", f"& {se(R['injection']['mde_80pct_power'])} &"),
 ("sample size", "10,755,282", "sample.blitz_after_pb_filter", nc(R["sample"]["blitz_after_pb_filter"])),
 ("new PBs", "37,391", "sample.blitz_new_pb_events", nc(R["sample"]["blitz_new_pb_events"])),
 ("players", "26,722", "sample.blitz_players", nc(R["sample"]["blitz_players"])),
 ("round number", "$+2.83$ & 0.10 & $z = 28.6$; relative $+23.5\\%$; $n = 3{,}406{,}437$", "round_number",
  f"${pp(R['round_number']['jump'])}$ & {se(R['round_number']['se'])} & $z = {R['round_number']['z']:.1f}$; relative ${100*R['round_number']['relative']:+.1f}\\%$; $n = {n(R['round_number']['n'])}$"),
 ("injection", "$+5.17$ & 0.48 & returned addition $+4.66$~pp", "injection",
  f"${pp(R['injection']['jump'])}$ & {se(R['injection']['se'])} & returned addition ${pp(R['injection']['recovered_minus_primary'])}$~pp"),
]
for k, s_ in (("PB-50", "PB$-50$"), ("PB-35", "PB$-35$"), ("PB-25", "PB$-25$"), ("PB+10", "PB$+10$")):
    d = R["placebo"][k]
    rows.append((f"placebo {k}", f"Placebo {s_} & ${pp(d['jump'])}$ & {se(d['se'])} & $z={d['z']:.2f}$", f"placebo.{k}",
                 f"Placebo {s_} & ${pp(d['jump'])}$ & {se(d['se'])} & $z={d['z']:.2f}$"))
sh = R["shuffle"]
rows.append(("shuffle", "mean $+0.24$, SD 0.38; $p=0.28$", "shuffle", f"mean ${pp(sh['mean'])}$, SD {se(sh['sd'])}; $p={sh['p_two_sided']:.2f}$"))
bal = R["balance"]
rows += [
 ("balance gain", "($-0.29$ points, $z=-2.37$)", "balance.gain", f"(${bal['gain']['jump']:+.2f}$ points, $z={bal['gain']['z']:.2f}$)"),
 ("balance oppdiff", "$-13.9$ points, $z=-4.38$", "balance.oppdiff", f"${bal['oppdiff']['jump']:+.1f}$ points, $z={bal['oppdiff']['z']:.2f}$"),
 ("balance log_idx", "$+0.054$, $z=3.74$", "balance.log_idx", f"${bal['log_idx']['jump']:+.3f}$, $z={bal['log_idx']['z']:.2f}$"),
 ("balance prior_games", "$+69.6$ prior blitz games, $z=3.90$", "balance.prior_games", f"${bal['prior_games']['jump']:+.1f}$ prior blitz games, $z={bal['prior_games']['z']:.2f}$"),
 ("balance log_prev_gap", "($z=0.44$)", "balance.log_prev_gap", f"($z={bal['log_prev_gap']['z']:.2f}$)"),
]
lab = {"quit_24h": "Quit = no new game within 24 h (left limit 3.84\\%)", "quit_90min_start_to_start": "Quit = next start more than 90 min after this start",
       "h10": "Bandwidth $h = 10$", "h25": "Bandwidth $h = 25$", "no_tournament": "Without tournament games",
       "gain_covariate": "Rating gain as a covariate", "bullet": "Bullet", "classical": "Classical"}
for k, l in lab.items():
    d = R["robustness"][k]
    text = f"{l} & ${pp(d['jump'])}$ & {se(d['se'])} \\\\"
    rows.append((f"robustness {k}", text, f"robustness.{k}", text))
rows.append(("24 h left limit", "(left limit 3.84\\%)", "robustness.quit_24h.left_limit", f"(left limit {pct(R['robustness']['quit_24h']['left_limit'])})"))
ab = R["robustness"]["adjacent_bins_x0_x1"]
rows += [
 ("adjacent bins", "Adjacent bins, $x=0$ versus $x=1$ & $+0.81$ & 0.69 \\\\", "robustness.adjacent_bins_x0_x1",
  f"Adjacent bins, $x=0$ versus $x=1$ & ${pp(ab['diff'])}$ & {se(ab['se'])} \\\\"),
 ("adjacent bin rates", "18.46\\% at $x=0$ and 19.27\\% at $x=1$", "robustness.adjacent_bins_x0_x1", f"{pct(ab['quit_x0'])} at $x=0$ and {pct(ab['quit_x1'])} at $x=1$"),
 ("adjacent upper bound", "2.17~pp (adjacent bins)", "robustness.adjacent_bins_x0_x1", f"{100*(ab['diff']+1.96*ab['se']):.2f}~pp (adjacent bins)"),
]
# Addendum A.
a, b, d = A["A"]["primary"], A["B"]["primary"], A["difference_B_minus_A"]
rows += [
 ("period A row", "$+0.51$ (0.45) & $[-0.38, +1.39]$", "data/addendum/addendum.json A.primary", f"${pp(a['jump'])}$ ({se(a['se'])}) & $[{pp(a['ci'][0])}, {pp(a['ci'][1])}]$"),
 ("period B row", "$+0.88$ (0.32) & $[+0.25, +1.52]$", "addendum.json B.primary", f"${pp(b['jump'])}$ ({se(b['se'])}) & $[{pp(b['ci'][0])}, {pp(b['ci'][1])}]$"),
 ("period B left, n", "left limit 19.86\\%; $n=407{,}350$ (37,708 players)", "addendum.json B.primary", f"left limit {pct(b['left_limit'])}; $n={n(b['n'])}$ ({nc(b['players'])} players)"),
 ("B-A row", "$+0.37$ (0.55) & $[-0.71, +1.46]$", "addendum.json difference_B_minus_A", f"${pp(d['diff'])}$ ({se(d['se'])}) & $[{pp(d['ci'][0])}, {pp(d['ci'][1])}]$"),
 ("period B relative", "$+4.4\\%$ relative", "period_B.json primary.relative", f"${100*b['relative']:+.1f}\\%$ relative"),
]
lb = {"h10": "Bandwidth $h = 10$", "h25": "Bandwidth $h = 25$", "quit_24h": "Quit = no new game within 24 h",
      "quit_90min_start_to_start": "Quit = next start more than 90 min after this start", "no_tournament": "Without tournament games",
      "gain_covariate": "Rating gain as a covariate", "bullet": "Bullet", "classical": "Classical"}
rowB = lambda l, d: f"{l} & ${pp(d['jump'])}$ & {se(d['se'])} & {d['z']:.2f} \\\\"
rows.append(("period B primary", rowB("Primary ($h=15$)", PB), "data/addendum/period_B.json primary", rowB("Primary ($h=15$)", PB)))
for k, l in lb.items():
    rows.append((f"period B {k}", rowB(l, RB[k]), f"period_B.json robustness.{k}", rowB(l, RB[k])))
abB = RB["adjacent_bins_x0_x1"]
t = f"Adjacent bins, $x=0$ versus $x=1$ & ${pp(abB['diff'])}$ & {se(abB['se'])} & {abB['diff']/abB['se']:.2f} \\\\"
rows.append(("period B adjacent bins", t, "period_B.json robustness.adjacent_bins_x0_x1", t))
for k, s_ in (("PB-50", "PB$-50$"), ("PB-35", "PB$-35$"), ("PB-25", "PB$-25$"), ("PB+10", "PB$+10$")):
    t = rowB(f"Placebo {s_}", B["placebo"][k]).replace(f"& {B['placebo'][k]['z']:.2f}", f"& ${B['placebo'][k]['z']:.2f}$" if B['placebo'][k]['z'] < 0 else f"& {B['placebo'][k]['z']:.2f}")
    rows.append((f"period B placebo {k}", t, f"period_B.json placebo.{k}", t))
for k, l in (("round_number", "Round-number control"), ("injection", "Injected 4.5~pp step")):
    t = rowB(l, B[k]); rows.append((f"period B {k}", t, f"period_B.json {k}", t))
rows += [
 ("period B shuffle", "($p<0.005$)", "period_B.json shuffle.p_two_sided", "($p<0.005$)" if B["shuffle"]["p_two_sided"] < 0.005 else "FAIL"),
 ("period B balance", "(gain $z=-4.38$, opponent rating difference $z=-3.44$, prior blitz games $z=3.09$, log game index $z=3.39$)", "period_B.json balance",
  f"(gain $z={B['balance']['gain']['z']:.2f}$, opponent rating difference $z={B['balance']['oppdiff']['z']:.2f}$, prior blitz games $z={B['balance']['prior_games']['z']:.2f}$, log game index $z={B['balance']['log_idx']['z']:.2f}$)"),
]
# Values from the independent checker logs.
L1, LE, LS = LOG("rdcheck_2013_2015.log"), LOG("extra_2013_2015.log"), LOG("stream_2013_2015.log")
def logrow(what, text, logname, logtext, needle):
    rows.append((what, text, f"checks/independent/{logname}", text if needle in logtext else f"MISSING {needle}"))
logrow("independent primary", "$+0.5083$~pp (SE 0.4509)", "rdcheck_2013_2015.log", L1, "jump +0.5083 pp  se 0.4509")
logrow("independent period B", "$+0.8833$~pp (SE 0.3235)", "rdcheck_period_B.log", LOG("rdcheck_period_B.log"), "jump +0.8833 pp  se 0.3235")
logrow("independent round number", "$+2.8344$~pp", "rdcheck_2013_2015.log", L1, "jump +2.8344 pp")
logrow("independent counts", "90,085,152 player-games, 917 self-play games", "stream_2013_2015.log", LS, "'selfplay': 917, 'nodiff_pg': 447358, 'pg': 90085152")
logrow("no RatingDiff", "447,358 player-games (0.5\\%)", "stream_2013_2015.log", LS, "'nodiff_pg': 447358")
logrow("games", "45,043,493 games", "stream_2013_2015.log", LS, "'games': 45043493")
for y, v in ((2013, "$+0.38$~pp (SE 0.39) in 2013"), (2014, "$+1.54$ (0.17) in 2014"), (2015, "$+3.42$ (0.12) in 2015")):
    m = re.search(rf"round number {y} ([+-][\d.]+) pp \(se ([\d.]+)\)", LE)
    val = f"{float(m.group(1)):+.2f}" ; sev = f"{float(m.group(2)):.2f}"
    text = v; ok = (val in v and sev in v)
    rows.append((f"round number {y}", text, "checks/independent/extra_2013_2015.log", text if ok else "FAIL"))
for lbl, text in (("ALT PB (max of pre and post)", "($+0.46$~pp, SE 0.47)"), ("ALT r (next blitz pre)", "($+0.52$~pp, SE 0.45)"),
                  ("rows with confirmed r", "($+0.56$~pp, SE 0.45)")):
    m = re.search(re.escape(lbl) + r"\s+jump ([+-][\d.]+) pp  se ([\d.]+)", L1)
    ok = f"{float(m.group(1)):+.2f}" in text and f"{float(m.group(2)):.2f}" in text
    rows.append((f"variant: {lbl}", text, "checks/independent/rdcheck_2013_2015.log", text if ok else "FAIL"))
for lbl, text in (("primary + covariates", "it is $+0.65$~pp (0.46)"), ("player fixed effects", "it is $+0.24$~pp (0.44)")):
    m = re.search(re.escape(lbl) + r".*?: ([+-][\d.]+) pp \(se ([\d.]+)\)", LE)
    ok = f"{float(m.group(1)):+.2f}" in text and f"{float(m.group(2)):.2f}" in text
    rows.append((f"extra: {lbl}", text, "checks/independent/extra_2013_2015.log", text if ok else "FAIL"))
for y, text in ((2013, "$+2.42$~pp (SE 2.03) in 2013"), (2014, "$+1.31$ (1.05) in 2014"), (2015, "$+0.15$ (0.51) in 2015")):
    m = re.search(rf"year {y}\s+jump ([+-][\d.]+) pp  se ([\d.]+).*?n (\d+)", L1)
    ok = f"{float(m.group(1)):+.2f}" in text and f"{float(m.group(2)):.2f}" in text
    rows.append((f"primary by year {y}", text, "checks/independent/rdcheck_2013_2015.log", text if ok else "FAIL"))
m = re.search(r"year 2015\s+jump .*? n (\d+)", L1)
rows.append(("2015 rows in bandwidth", "143,186 of 185,385", "rdcheck_2013_2015.log", f"{int(m.group(1)):,} of {P['n']:,}"))
# Rating chain (1-in-50 sample): codes 0 exact, 1 and 2 small, 3 more than 5 points.
ch = {(int(y), int(c)): int(v) for y, c, v in re.findall(r"chain \((\d+), 'blitz', (\d)\) (\d+)", LS)}
ex, big = [], []
for y in (2013, 2014, 2015):
    tot = sum(ch.get((y, c), 0) for c in range(4))
    ex.append(f"{100*ch[(y,0)]/tot:.1f}\\%"); big.append(f"{100*ch[(y,3)]/tot:.1f}\\%")
t = f"{ex[0]} of cases in 2013, {ex[1]} in 2014 and {ex[2]} in 2015. In {big[0]}, {big[1]} and {big[2]}"
rows.append(("rating chain", t, "checks/independent/stream_2013_2015.log", t))
m = re.search(r"mean\s+([\d.\s]+)\n", L1)
r99, r00 = m.group(1).split()[7], m.group(1).split()[8]
t = f"{r99}\\% at ratings that end in 99 and {r00}\\% at ratings that end in 00"
rows.append(("round-number bins", t, "checks/independent/rdcheck_2013_2015.log", t))

bad = []
E = J("data/expected.json")
if E["primary"] != R or E["addendum"] != A:
    bad.append("data/results.json or data/addendum/addendum.json differs from data/expected.json")
for what, text, src, val in rows:
    if text != val:
        bad.append(f"{what}: paper text {text!r} != source {val!r}")
    elif text not in paper:
        bad.append(f"{what}: {text!r} not in paper.tex")
if "--markdown" in sys.argv:
    print("| Quantity | Text in the paper | Source |\n|---|---|---|")
    for what, text, src, val in rows:
        print(f"| {what} | `{text}` | `{src}` |")
print(f"paper numbers checked: {len(rows)}, mismatches: {len(bad)}", file=sys.stderr)
for b_ in bad:
    print("  ", b_, file=sys.stderr)
sys.exit(1 if bad else 0)
