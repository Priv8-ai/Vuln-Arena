#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$ROOT"
MACHINES=all
INSTALL_HOSTS=1
BUILD=1
VERIFY=1
for arg in "$@"; do
  case "$arg" in
    --no-hosts) INSTALL_HOSTS=0 ;;
    --no-build) BUILD=0 ;;
    --quick) VERIFY=0 ;;
    --machines=*) MACHINES=${arg#*=} ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

command -v docker >/dev/null 2>&1 || { echo "Docker is required." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required." >&2; exit 1; }
docker info >/dev/null 2>&1 || { echo "Docker Engine is not running." >&2; exit 1; }

python3 scripts/build_findings_baseline.py
python3 scripts/build_machine_manifest.py
python3 scripts/build_router_assets.py

if [ "$INSTALL_HOSTS" -eq 1 ]; then
  HOSTS_FILE=/etc/hosts
  TMP_FILE=$(mktemp)
  trap 'rm -f "$TMP_FILE"' EXIT HUP INT TERM
  awk '/# BEGIN VULN ARENA MANAGED HOSTS/{skip=1} /# END VULN ARENA MANAGED HOSTS/{skip=0;next} !skip{print}' "$HOSTS_FILE" > "$TMP_FILE"
  printf '\n' >> "$TMP_FILE"
  cat config/hosts.arena.test >> "$TMP_FILE"
  sudo cp "$TMP_FILE" "$HOSTS_FILE"
  rm -f "$TMP_FILE"
  trap - EXIT HUP INT TERM
fi

python3 arena.py doctor
RUN_ID="local-$(date -u +%Y%m%d-%H%M%S)"
if [ "$BUILD" -eq 1 ]; then
  python3 arena.py start --machines "$MACHINES" --run-id "$RUN_ID" --wait-seconds 120
else
  python3 arena.py start --machines "$MACHINES" --run-id "$RUN_ID" --wait-seconds 120 --no-build
fi
python3 scripts/verify_domains.py --json-out "runs/$RUN_ID/domains.json"
if [ "$VERIFY" -eq 1 ]; then
  python3 arena.py verify --machines "$MACHINES" --mode full --run-id "$RUN_ID" --out-dir "runs/$RUN_ID/verification"
fi
printf '%s\n' "$RUN_ID" > runs/current-run.txt
echo "Vuln Arena is ready: http://arena.test:18080"
echo "Zero-config dashboard: http://arena.localhost:18080"
