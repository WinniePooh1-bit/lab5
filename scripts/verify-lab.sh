#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p results

command -v node >/dev/null 2>&1 || { echo "Node.js олдсонгүй." >&2; exit 127; }
command -v newman >/dev/null 2>&1 || { echo "Newman олдсонгүй." >&2; exit 127; }

node -v 2>&1 | tee results/node-version.txt
newman -v 2>&1 | tee results/newman-version.txt
node scripts/validate-collections.js 2>&1 | tee results/collection-validation.txt

SERVER_PID=""
stop_server() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  SERVER_PID=""
}
trap stop_server EXIT

node server.js > results/server.log 2>&1 &
SERVER_PID="$!"

ready=0
for attempt in $(seq 1 30); do
  if node -e "fetch('http://127.0.0.1:3000/courses/__health').then(() => process.exit(0)).catch(() => process.exit(1))" >/dev/null 2>&1; then
    ready=1
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    cat results/server.log >&2
    echo "API сервер асаж чадсангүй." >&2
    exit 1
  fi
  sleep 1
done
if [[ "$ready" -ne 1 ]]; then
  echo "API сервер 30 секундэд бэлэн болсонгүй." >&2
  exit 1
fi

run_newman() {
  local collection="$1"
  local output="$2"
  local expected_exit="$3"
  local actual_exit

  set +e
  newman run "$collection" --color off > "$output" 2>&1
  actual_exit=$?
  set -e

  printf '\nexit_code=%s\n' "$actual_exit" >> "$output"
  cat "$output"

  if [[ "$actual_exit" -ne "$expected_exit" ]]; then
    echo "$collection: exit code $actual_exit, expected $expected_exit." >&2
    return 1
  fi
}

# PASS: all 27 assertions must succeed.
run_newman "lab05-collection.json" "results/newman-pass.txt" 0
grep -Eq 'assertions[[:space:]]*[│|][[:space:]]*27[[:space:]]*[│|][[:space:]]*0' results/newman-pass.txt

# FAIL: only the first successful registration's status-code oracle is intentionally wrong.
run_newman "lab05-collection-fail.json" "results/newman-fail.txt" 1
grep -Eq 'assertions[[:space:]]*[│|][[:space:]]*27[[:space:]]*[│|][[:space:]]*1' results/newman-fail.txt

# DOWN: stop the API and prove connection refusal is a transport/interface failure.
stop_server
run_newman "lab05-collection.json" "results/newman-down.txt" 1
grep -q 'ECONNREFUSED' results/newman-down.txt

printf 'PASS exit_code=0\nFAIL exit_code=1\nDOWN exit_code=1\n' | tee results/exit-codes.txt
echo "Lab05 Newman PASS / intentional FAIL / server DOWN шалгалт амжилттай дууслаа."
