#!/usr/bin/env bash
set -euo pipefail
n=$(python3 -c "print(sum(all(k % d for d in range(2, int(k**0.5) + 1)) for k in range(2, 100)))")
[ "$n" = 25 ] && echo "ok: 25 primes below 100" || { echo "expected 25, got $n"; exit 1; }
