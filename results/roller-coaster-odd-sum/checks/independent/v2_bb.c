/* Verifier round 2: my own exact search, written before I read checks/oddsum_bb.c.
   Positions 0..n-1, values 1..n. A triple of positions a<b<c is "lost" when the three values are monotone.
   t(pi) = base + Wtot - L(pi), base = sum_{m>=3} C(n,m), weight of (a,b,c) = 2^a * 2^(n-1-c),
   Wtot = sum of all weights, L = sum of the weights of the lost triples.
   Search: place the values at positions 0,1,2,... With positions 0..m-1 placed (the prefix), a lower bound
   on L is A + (B + D) + C, over four disjoint sets of triples:
     A = exact lost weight of the triples inside the prefix.
     B : triples (a,b in the prefix, c free). If value u goes to position c, their lost weight is
         2^(n-1-c) * g[u], g[u] = sum of 2^a over prefix pairs a<b such that (pi_a, pi_b, u) is monotone.
     D : triples (a in the prefix, b<c free). If value u goes to b and value y to c, the lost weight over
         all a is 2^(n-1-c) * lo[u] when y>u and 2^(n-1-c) * hi[u] when y<u, where lo[u] (hi[u]) is the
         sum of 2^a over prefix a with pi_a<u (pi_a>u). So position b loses at least
         h[u] * sum_{c>b} 2^(n-1-c) = h[u] * (2^(n-1-b) - 1), h[u] = min(lo[u], hi[u]).
         B + D >= sum over free b of [2^(n-1-b) * (g[u_b]+h[u_b])] - sum of h over the free values.
         The second sum does not depend on the assignment. The first is at least the sorted pairing
         (smallest g+h with the largest weight), by the rearrangement inequality. The Odd Sum rows only
         remove assignments, so the bound stays valid.
     C : triples with all three positions free. Take the first q = min(r, R0) free positions, r = number of
         free positions. The triples inside this block have weight 2^(n-q) * (weight of the same triple in
         a permutation of length q), so their lost weight is at least 2^(n-q) * Lmin[q], where Lmin[q] is
         the exact minimum of L over permutations of length q. Lmin[q] is computed at startup by this same
         search in optimisation mode (budget = best loss so far - 1), for q = 3..R0 in increasing order.
   Prune only if the bound > budget. In decision mode budget = base + Wtot - T, so every completion of a
   pruned prefix has t < T. All arithmetic is in 64-bit integers; every quantity is below 2^40.
   Usage: v2_bb n T mode first_lo first_hi     (mode 1: Odd Sum rows; pi_1 in [first_lo, first_hi]) */
/* no libc headers on this machine (leanc only): declare what is used */
int printf(const char*, ...); int atoi(const char*); long long atoll(const char*);
typedef long long i64; typedef unsigned long long u64;
#define R0 12
static int n, mode, opt, flo, fhi;
static i64 budget, baseW, T;
static int perm[32];
static u64 nodes, found;
static i64 best = -1;
static i64 Lmin[32];

static void rec(int m, unsigned used, i64 A, const i64 *g, const i64 *lo) {
  nodes++;
  if (m == n) {
    if (opt) { budget = A - 1; return; }   /* here A <= budget: a new best loss */
    i64 t = baseW - A;
    if (t >= T) {
      found++; if (t > best) best = t;
      printf("PERM t=%lld :", t);
      for (int i = 0; i < n; i++) printf(" %d", perm[i]);
      printf("\n");
    }
    return;
  }
  i64 all2 = ((i64)1 << (m + 1)) - 1;      /* sum of 2^a over the new prefix 0..m */
  int r = n - 1 - m;                        /* free positions after placing position m */
  int q = r < R0 ? r : R0;
  i64 Cc = q >= 3 ? Lmin[q] << (n - q) : 0;
  for (int v = 1; v <= n; v++) {
    if (used >> v & 1) continue;
    if (m == 0 && (v < flo || v > fhi)) continue;
    if (mode == 1 && 2 * m > n - 1 && ((v + perm[n - 1 - m]) & 1) == 0) continue;
    i64 A2 = A + (g[v] << (n - 1 - m));
    if (A2 + Cc > budget) continue;
    i64 g2[32], lo2[32], s[32]; int k = 0; i64 sumh = 0;
    i64 lov = lo[v], hiv = (((i64)1 << m) - 1) - lo[v];
    for (int u = 1; u <= n; u++) {
      if ((used >> u & 1) || u == v) continue;
      g2[u] = g[u] + (u > v ? lov : hiv);
      lo2[u] = lo[u] + (u > v ? (i64)1 << m : 0);
      i64 hi2 = all2 - lo2[u];
      i64 h = lo2[u] < hi2 ? lo2[u] : hi2;
      sumh += h;
      i64 key = g2[u] + h;
      int j = k++; while (j > 0 && s[j - 1] > key) { s[j] = s[j - 1]; j--; } s[j] = key;   /* ascending */
    }
    i64 BD = -sumh;
    for (int i = 0; i < k; i++) BD += s[i] << (n - 1 - (m + 1 + i));
    if (A2 + BD + Cc > budget) continue;
    perm[m] = v;
    rec(m + 1, used | 1u << v, A2, g2, lo2);
  }
}

static void setup(int nn) {
  n = nn;
  i64 base = ((i64)1 << n) - 1 - n - (i64)n * (n - 1) / 2, W = 0;
  for (int a = 0; a < n; a++) for (int c = a + 2; c < n; c++) W += (i64)(c - a - 1) << (a + n - 1 - c);
  baseW = base + W;
}

int main(int argc, char **argv) {
  if (argc < 6) return 2;
  int N = atoi(argv[1]); i64 TT = atoll(argv[2]); int md = atoi(argv[3]);
  int f1 = atoi(argv[4]), f2 = atoi(argv[5]);
  i64 zero[32] = {0};
  /* exact minimum loss for lengths 3..R0 (all permutations, no symmetry) */
  for (int q = 3; q <= R0 && q < N; q++) {
    setup(q); mode = 0; opt = 1; budget = baseW;     /* baseW >= Wtot >= any loss */
    flo = 1; fhi = q; rec(0, 0, 0, zero, zero);
    Lmin[q] = budget + 1;
    printf("LMIN q=%d Lmin=%lld tmax=%lld\n", q, Lmin[q], baseW - Lmin[q]);
  }
  setup(N); mode = md; opt = 0; T = TT; budget = baseW - T; nodes = 0;
  flo = f1; fhi = f2; rec(0, 0, 0, zero, zero);
  printf("SUMMARY n=%d T=%lld mode=%d first=%d..%d baseW=%lld budget=%lld nodes=%llu found=%llu best=%lld\n",
         n, T, mode, flo, fhi, baseW, budget, nodes, found, best);
  return 0;
}
