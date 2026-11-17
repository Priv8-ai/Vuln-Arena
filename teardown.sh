#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT"
RUN_ID=""
[ -f runs/current-run.txt ] && RUN_ID=$(sed -n '1p' runs/current-run.txt)
if [ -n "$RUN_ID" ]; then
  python3 arena.py stop --machines all --run-id "$RUN_ID"
else
  python3 arena.py stop --machines all
fi
if [ "${1:-}" != "--keep-hosts" ] && grep -q '# BEGIN VULN ARENA MANAGED HOSTS' /etc/hosts; then
  TMP_FILE=$(mktemp)
  trap 'rm -f "$TMP_FILE"' EXIT HUP INT TERM
  awk '/# BEGIN VULN ARENA MANAGED HOSTS/{skip=1} /# END VULN ARENA MANAGED HOSTS/{skip=0;next} !skip{print}' /etc/hosts > "$TMP_FILE"
  sudo cp "$TMP_FILE" /etc/hosts
  rm -f "$TMP_FILE"
  trap - EXIT HUP INT TERM
fi
echo "Vuln Arena stopped; images and run evidence were preserved."
