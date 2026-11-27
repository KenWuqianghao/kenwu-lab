import re
def wrap(x): return (x + 12) % 24 - 12
def lst(jd, lon_e): return ((280.46061837 + 360.98564736629 * (jd - 2451545.0) + lon_e) % 360) / 15
def parse_ra(s):
    if not s: return None
    try: return float(s) / 15
    except ValueError: pass
    m = re.match(r'\s*(\d+)[:h ]\s*(\d+)(?:[:m ]\s*([\d.]+))?', s)
    return int(m[1]) + int(m[2]) / 60 + float(m[3] or 0) / 3600 if m else None
