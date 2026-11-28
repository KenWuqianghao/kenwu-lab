"""Digitize the r-band DRW posterior contours (68% and 95%) of Liao et al. 2021 (arXiv:2008.12317v3),
file chain_4band.pdf of the arXiv source (the DRW parameter figure). The figure is vector, so the contour
paths are read exactly from the PDF. Axis calibration comes from the tick marks in the same PDF:
x ticks at log10(tau) = 2.4, 2.8, 3.2, 3.6; y ticks at sigma = 0.1 ... 0.5 mag.
Usage: digitize_drw.py <chain_4band.pdf> <out.json>"""
import sys, json
import numpy as np
import pymupdf

pdf, out = sys.argv[1], sys.argv[2]
page = pymupdf.open(pdf)[0]
XT = (616.55, 676.04, 735.53, 795.02)      # pixel x of log tau 2.4, 2.8, 3.2, 3.6 (r panel)
YT = (316.03, 268.62, 221.2, 173.79, 126.38)  # pixel y of sigma 0.1 ... 0.5 (r panel)
ax = np.polyfit(XT, [2.4, 2.8, 3.2, 3.6], 1)
ay = np.polyfit(YT, [0.1, 0.2, 0.3, 0.4, 0.5], 1)
FILLS = {(0.78, 0.21, 0.0): 'c68', (1.0, 0.38, 0.0): 'c95'}   # r-band dark (68%) and light (95%) fills
res = {'source': 'arXiv:2008.12317v3 source, chain_4band.pdf, r panel',
       'note': 'DRW-only fit of the paper (no periodic term); sigma in mag, tau observed frame in days'}
for d in page.get_drawings():
    f = tuple(round(x, 2) for x in d['fill']) if d.get('fill') else None
    if f not in FILLS:
        continue
    pts = []
    for it in d['items']:
        for q in it[1:]:
            if hasattr(q, 'x'):
                pts.append((q.x, q.y))
    a = np.array(pts)
    res[FILLS[f]] = {'log10_tau': np.round(np.polyval(ax, a[:, 0]), 4).tolist(),
                     'sigma': np.round(np.polyval(ay, a[:, 1]), 4).tolist()}
json.dump(res, open(out, 'w'), indent=0)
for k in ('c68', 'c95'):
    lt, s = np.array(res[k]['log10_tau']), np.array(res[k]['sigma'])
    print(k, 'n', len(lt), 'log tau %.2f-%.2f' % (lt.min(), lt.max()), 'sigma %.3f-%.3f' % (s.min(), s.max()))
    for L in (2.6, 2.855, 3.0, 3.2, 3.4):
        k2 = np.abs(lt - L) < 0.03
        if k2.any():
            print('   log tau %.2f: sigma %.3f-%.3f' % (L, s[k2].min(), s[k2].max()))
