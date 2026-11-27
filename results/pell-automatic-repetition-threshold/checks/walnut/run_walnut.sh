#!/usr/bin/env bash
# Reruns the Walnut proofs of the paper. Needs git and a JDK 17 or later, and about
# 3 GB of Java heap. Run from the result folder: bash checks/walnut/run_walnut.sh
# Optional: WALNUT_DIR (default $TMPDIR/walnut-c61231a), WALNUT_HEAP (default 3g).
# 1. Clones Walnut at commit c61231a and builds Walnut-all.jar with its Maven wrapper.
# 2. Copies data/PSQ.txt into Walnut's "Word Automata Library".
# 3. Runs checks/walnut/squarefree.txt (expect TRUE twice) and checks/walnut/hb.txt
#    (expect TRUE twice), and fails if a result is not TRUE.
set -euo pipefail
cd "$(dirname "$0")/../.."
HERE=$(pwd)
COMMIT=c61231a244090a75e0923defc574c5389f8a3686
W=${WALNUT_DIR:-${TMPDIR:-/tmp}/walnut-c61231a}
if [ ! -f "$W/target/Walnut-all.jar" ]; then
  rm -rf "$W"
  git clone -q https://github.com/Walnut-Theorem-Prover/Walnut.git "$W"
  git -C "$W" checkout -q "$COMMIT"
  (cd "$W" && MAVEN_USER_HOME="$W/.mvnhome" ./mvnw -q -Dmaven.repo.local="$W/.m2" clean package -DskipTests -Pfat-jar)
fi
test "$(git -C "$W" rev-parse HEAD)" = "$COMMIT"
cp data/PSQ.txt "$W/Word Automata Library/PSQ.txt"
cd "$W"
java -version 2>&1 | head -1
for f in squarefree hb; do
  echo "== $f.txt"
  start=$(date +%s)
  java -Xmx"${WALNUT_HEAP:-3g}" -jar target/Walnut-all.jar < "$HERE/checks/walnut/$f.txt" | tee "$HERE/checks/walnut/$f.log"
  echo "time: $(( $(date +%s) - start )) s"
  n=$(grep -c '^TRUE$' "$HERE/checks/walnut/$f.log" || true)
  if [ "$n" != 2 ] || grep -q '^FALSE$' "$HERE/checks/walnut/$f.log"; then
    echo "run_walnut.sh: $f.txt did not give TRUE twice"; exit 1
  fi
done
hbfile=$(ls -t Session/*/"Automata Library"/hb.txt | head -1)
echo "states of the automaton hb: $(grep -cE '^[0-9]+ [0-9]+ *$' "$hbfile")"
echo "run_walnut.sh: all Walnut results TRUE"
