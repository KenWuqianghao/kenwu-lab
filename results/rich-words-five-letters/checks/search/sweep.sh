#!/bin/bash
# sweep h0..h4 in 1..$1, target u-length $2
M=$1; T=$2
for a in $(seq 1 $M); do for b in $(seq 1 $M); do for c in $(seq 1 $M); do for d in $(seq 1 $M); do for e in $(seq 1 $M); do
 h5=$((a+e)); h6=$((b-e+2*h5)); h7=$((c-e+2*h6)); h8=$((d-e+2*h7));
 if [ $h6 -lt 1 ] || [ $h7 -lt 1 ] || [ $h8 -lt 1 ] || [ $h8 -gt 80 ]; then continue; fi
 out=$(./dfs $T 80 1 $a $b $c $d $e 2>&1)
 if echo "$out" | grep -q "SOL\|CAP"; then echo "H $a $b $c $d $e : $h5 $h6 $h7 $h8"; echo "$out" | head -20; fi
done; done; done; done; done
