"""Core pipeline for the pre-registered test in PROTOCOL.md.

Stages: parse GHCN-Daily HCN PRCP -> dense (station, day) array; lunar elongation per day;
statistics (national R2_2, phase, station rate S); YRR null; placebo periods; injections.
"""
import datetime as dt
import os
import tarfile

import numpy as np
from scipy import stats

D0 = dt.date(1895, 1, 1)
D_END = dt.date(2026, 10, 31)
NDAY = (D_END - D0).days + 1
SYN = 29.530589
JD_REF = 2451550.26  # new moon 2000-01-06 18:14 UTC
PHASE_CLAIM_D = 4.04
HALF = SYN / 2
PERIODS = {"A": (dt.date(1895, 1, 1), dt.date(2008, 12, 31), 3650),
           "B": (dt.date(2009, 1, 1), dt.date(2026, 10, 31), 2000)}


def day_index(d):
    return (d - D0).days


def conus_ids(stations_txt):
    ids = {}
    with open(stations_txt) as f:
        for line in f:
            sid, st = line[0:11], line[38:40]
            if sid.startswith("US") and st not in ("AK", "HI"):
                ids[sid] = (float(line[12:20]), float(line[21:30]), st)
    return ids


def parse_archive(tar_path, stations_txt):
    """Return (ids, P) with P float32 (nstation, NDAY) in mm, NaN for missing/flagged."""
    meta = conus_ids(stations_txt)
    rows = {}
    with tarfile.open(tar_path, "r:gz") as tf:
        for m in tf:
            if not m.name.endswith(".dly"):
                continue
            sid = os.path.basename(m.name)[:11]
            if sid not in meta:
                continue
            raw = tf.extractfile(m).read()
            lines = [ln for ln in raw.split(b"\n") if ln[17:21] == b"PRCP"]
            if not lines:
                continue
            buf = np.frombuffer(b"".join(ln.ljust(269)[:269] for ln in lines), dtype=np.uint8).reshape(-1, 269)
            ym = buf[:, 11:17].copy().view("S6").ravel()
            month0 = np.array([f"{s[:4].decode()}-{s[4:].decode()}" for s in ym], dtype="datetime64[M]")
            mstart = month0.astype("datetime64[D]")
            ndm = ((month0 + 1).astype("datetime64[D]") - mstart).astype(int)
            out = np.full(NDAY, np.nan, dtype=np.float32)
            base = np.datetime64(D0.isoformat())
            for d in range(31):
                c = 21 + 8 * d
                vals = buf[:, c:c + 5].copy().view("S5").ravel().astype(int)
                qf = buf[:, c + 6]
                ok = (vals != -9999) & (qf == ord(" ")) & (d < ndm)
                di = (mstart + d - base).astype(int)
                ok &= (di >= 0) & (di < NDAY)
                out[di[ok]] = vals[ok] / 10.0
            rows[sid] = out
    ids = sorted(rows)
    return ids, np.stack([rows[i] for i in ids]), meta


def elongation_deg(ephem_path, hour=12, day_shift=0):
    """Apparent geocentric Moon-Sun ecliptic longitude difference (of date) per day.

    The value for observation day d is taken at `hour` UTC of day d + day_shift (protocol: 12, 0)."""
    from skyfield.api import load
    from skyfield.framelib import ecliptic_frame
    ts = load.timescale(builtin=True)
    eph = load(ephem_path)
    earth, moon, sun = eph["earth"], eph["moon"], eph["sun"]
    days = np.arange(NDAY)
    dates = [D0 + dt.timedelta(int(i) + day_shift) for i in days]
    t = ts.utc([d.year for d in dates], [d.month for d in dates], [d.day for d in dates], hour)
    e = earth.at(t)
    _, lm, _ = e.observe(moon).apparent().frame_latlon(ecliptic_frame)
    _, ls, _ = e.observe(sun).apparent().frame_latlon(ecliptic_frame)
    return (lm.degrees - ls.degrees) % 360.0


def jd_noon():
    return 2451545.0 - (dt.date(2000, 1, 1) - D0).days + np.arange(NDAY)  # JD 2451545.0 = 2000-01-01 12:00


def pseudo_bins(P):
    ph = ((jd_noon() - JD_REF) / P) % 1.0
    return np.minimum((ph * 100).astype(np.int64), 99)


# ---------- harmonic statistics ----------
ANG = 2 * np.pi * (np.arange(10) + 0.5) / 10


def harm(m):
    """m (..., 10) class means -> (R2_2, a2, b2)."""
    m = np.asarray(m, float)
    a = 0.2 * (m * np.cos(2 * ANG)).sum(-1)
    b = 0.2 * (m * np.sin(2 * ANG)).sum(-1)
    ss = ((m - m.mean(-1, keepdims=True)) ** 2).sum(-1)
    return 5 * (a ** 2 + b ** 2) / ss, a, b


def phase_days(a, b):
    th = (np.arctan2(b, a) / 2) % np.pi
    return th / (2 * np.pi) * SYN


def phase_ok(a, b):
    d = (phase_days(a, b) - PHASE_CLAIM_D) % HALF
    return np.minimum(d, HALF - d) <= HALF / 4


def f_p(r2):
    F = (r2 / 2) / ((1 - r2) / 7)
    return stats.f.sf(F, 2, 7)


def summarize(C, N):
    """C, N: (S, 10) class sums of z and counts. Returns dict of statistics."""
    m_nat = C.sum(0) / N.sum(0)
    r2, a, b = harm(m_nat)
    r2s, _, _ = harm(C / N)
    sig = f_p(r2s) < 0.05
    return dict(r2=float(r2), a2=float(a), b2=float(b), amp=float(np.hypot(a, b)),
                phase_d=float(phase_days(a, b)), phase_ok=bool(phase_ok(a, b)),
                p_F=float(f_p(r2)), S=float(sig.mean()), n_sig=int(sig.sum()), n_st=int(len(sig)),
                m=[float(x) for x in m_nat])


# ---------- period preparation ----------
class Period:
    def __init__(self, name, P, fbin):
        d0, d1, minvalid = PERIODS[name]
        i0, i1 = day_index(d0), day_index(d1) + 1
        x = P[:, i0:i1].astype(np.float64)
        valid = ~np.isnan(x)
        keep = valid.sum(1) >= minvalid
        x, valid = x[keep], valid[keep]
        mu = np.nanmean(x, 1)
        sd = np.nanstd(x, 1)
        self.name, self.keep, self.i0, self.i1 = name, keep, i0, i1
        self.z = np.where(valid, (x - mu[:, None]) / sd[:, None], 0.0)
        self.pz = np.where(valid, x / sd[:, None], 0.0)  # p/sd, for injection
        self.v = valid.astype(np.float64)
        self.fbin = fbin[i0:i1]
        years = np.array([(D0 + dt.timedelta(int(i))).year for i in range(i0, i1)])
        self.yidx = years - years.min()
        self.ny = self.yidx.max() + 1
        S = x.shape[0]
        from scipy import sparse
        key = self.yidx * 100 + self.fbin
        oh = sparse.csr_matrix((np.ones(len(key)), (np.arange(len(key)), key)), shape=(len(key), self.ny * 100))
        self.Hz = np.asarray((oh.T @ self.z.T).T).reshape(S, self.ny, 100)
        self.Hp = np.asarray((oh.T @ self.pz.T).T).reshape(S, self.ny, 100)
        self.Hn = np.asarray((oh.T @ self.v.T).T).reshape(S, self.ny, 100)

    def classes_from_bins(self, bins):
        """Class sums for a per-day fine-bin series over the full record (placebo)."""
        cls = bins[self.i0:self.i1] // 10
        oh = np.zeros((len(cls), 10))
        oh[np.arange(len(cls)), cls] = 1
        return self.z @ oh, self.v @ oh

    def rotated_fine(self, u, with_p=False):
        """u: (ny,) offsets. Fine-bin totals (S,100) of z, count (and p/sd) after rotation.

        Day in fine bin f of year y moves to bin (f + u_y) mod 100."""
        b = np.arange(100)
        src = (b[None, :] - u[:, None]) % 100  # (ny,100): new bin b' takes old bin b'-u
        yy = np.arange(self.ny)[:, None]
        out = [self.Hz[:, yy, src].sum(1), self.Hn[:, yy, src].sum(1)]
        if with_p:
            out.append(self.Hp[:, yy, src].sum(1))
        return out


def to_class(F):
    return F.reshape(F.shape[0], 10, 10).sum(-1)


FINE_ANG = 2 * np.pi * (np.arange(100) + 0.5) / 100
PHI0 = 2 * (2 * np.pi * PHASE_CLAIM_D / SYN)


def inject(Fz, Fp, c):
    return Fz + c * np.cos(2 * FINE_ANG - PHI0)[None, :] * Fp
