"""Digitize the thick r-band model curve (q=0.11 bursty model) of Liao et al. 2021, Fig. 1.
Input: the raster image embedded in the arXiv source file burst_fit_J0252_rednoise_new-eps-converted-to.pdf
(extract with `pdfimages -png`). The raster is stored vertically flipped."""
import sys, json, numpy as np
from PIL import Image
im = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int)[::-1]  # flip vertically
H = im.shape[0]
# panel r (2nd from top after flip): rows between frame lines
# frame rows (raw) 2344-2351 and 3319-3326 -> flipped
top, bot = H-1-3319, H-1-2351
# y ticks (raw rows 2487, 2835, 3183 -> flipped) map to 21.4, 20.9, 20.4 after flip
ty = np.array([H-1-3183, H-1-2835, H-1-2487]); tm = np.array([20.4, 20.9, 21.4])
ya, yb = np.polyfit(ty, tm, 1)
# x ticks (MJD-50000 = 1000..8000 at raw cols 476..5155)
tx = np.array([476.0, 1144, 1813, 2481, 3150, 3818, 4486, 5155]); tv = 51000 + 1000*np.arange(8)
xa, xb = np.polyfit(tx, tv, 1)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
orange = (r > 230) & (g > 40) & (g < 95) & (b < 40)
pts = []
prev = None; lastc = -999
for c in range(415, 5750):
    if c - lastc > 40: prev = None
    rows = np.where(orange[top+8:bot-8, c])[0] + top + 8
    if len(rows) == 0: continue
    runs = np.split(rows, np.where(np.diff(rows) > 1)[0] + 1)
    runs = [u for u in runs if 8 <= len(u) <= 40]  # thick line segment
    if not runs: continue
    cent = [u.mean() for u in runs]
    k = int(np.argmin([abs(x - prev) for x in cent])) if prev is not None else int(np.argmax([len(u) for u in runs]))
    if prev is not None and abs(cent[k] - prev) > 25: continue
    prev = cent[k]; lastc = c
    pts.append((xa*c + xb, ya*cent[k] + yb))
pts = np.array(pts)
json.dump({'mjd': pts[:, 0].round(2).tolist(), 'mag': pts[:, 1].round(4).tolist(),
           'calib': {'x_slope': xa, 'x_int': xb, 'y_slope': ya, 'y_int': yb}}, open(sys.argv[2], 'w'))
print(len(pts), pts[:, 0].min(), pts[:, 0].max(), pts[:, 1].min(), pts[:, 1].max())
