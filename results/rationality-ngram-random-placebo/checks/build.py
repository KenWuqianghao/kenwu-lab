"""Merge extractor outputs into a compact word table (work/table.npz).
Usage: python build.py <extdir> <out.npz>"""
import sys, gzip, glob, os, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wordsets import A_ALL, B_ALL

EXT, OUT = sys.argv[1], sys.argv[2]
NY = 170
NCAND = 40000
POS4 = ["NOUN", "VERB", "ADJ", "ADV"]
FLAGS = set(A_ALL) | set(B_ALL)
KEEP_ALWAYS = FLAGS | {"an"}

def files(corp):
    fs = sorted(glob.glob(os.path.join(EXT, f"{corp}_*.tsv.gz")))
    assert fs, corp
    return fs

def totals(path):
    t = {}
    # totalcounts-1 is one line of tab-separated "year,match,pages,volumes"
    s = open(path).read().split()
    for e in s:
        y, m = e.split(",")[:2]
        t[int(y)] = int(m)
    return np.array([t[y] for y in range(1850, 2020)], dtype=np.float64)

# pass 1: totals per lowercase word, lowercase-form total, POS totals (eng only)
tot = collections.Counter(); low = collections.Counter()
pos = collections.defaultdict(lambda: np.zeros(5))
for f in files("eng"):
    with gzip.open(f, "rt") as fh:
        for line in fh:
            k, form, rest = line.split("\t", 2)
            w = form.lower()
            if k == "U":
                n = int(rest.split("\t", 1)[0])
                tot[w] += n
                if form == w:
                    low[w] += n
            else:
                tag, n = rest.split("\t"); n = int(n)
                pos[w][POS4.index(tag) if tag in POS4 else 4] += n
cands = [w for w, n in tot.most_common() if len(w) >= 2 and w not in FLAGS and low[w] >= 0.5 * n]
cands = set(cands[:NCAND]) | (KEEP_ALWAYS & set(tot))
print("pass1 words", len(tot), "candidates", len(cands), flush=True)

# pass 2: yearly counts for candidates in eng and fiction
def load(corp):
    arr = {}
    for f in files(corp):
        with gzip.open(f, "rt") as fh:
            for line in fh:
                if line[0] != "U":
                    continue
                _, form, rest = line.split("\t", 2)
                w = form.lower()
                if w not in cands:
                    continue
                v = np.array(rest.split("\t")[1:], dtype=np.int64)
                assert v.size == NY
                if w in arr: arr[w] += v
                else: arr[w] = v
    return arr
eng = load("eng"); fic = load("eng-fiction")
words = sorted(eng, key=lambda w: -tot[w])
E = np.array([eng[w] for w in words]); Fc = np.array([fic.get(w, np.zeros(NY, np.int64)) for w in words])
P = np.array([pos[w] for w in words])
np.savez_compressed(OUT, words=np.array(words), eng=E, fic=Fc, pos=P,
                    lowshare=np.array([low[w] / tot[w] for w in words]),
                    Neng=totals(os.path.join(EXT, "eng_totalcounts-1")),
                    Nfic=totals(os.path.join(EXT, "eng-fiction_totalcounts-1")))
print("saved", len(words), flush=True)
