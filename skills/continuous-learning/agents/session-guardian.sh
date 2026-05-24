#!/usr/bin/env bash
# knowledge-continuum — Observer Session Guard
# Exit 0 = proceed, Exit 1 = skip this observer cycle.
# Called by observer-loop.sh before spawning any Claude session.

set -euo pipefail

INTERVAL="${KNC_OBSERVER_INTERVAL_SECONDS:-300}"
LOG_PATH="${KNC_OBSERVER_LAST_RUN_LOG:-$HOME/.claude/knc-observer-last-run.log}"
ACTIVE_START="${KNC_ACTIVE_HOURS_START:-800}"
ACTIVE_END="${KNC_ACTIVE_HOURS_END:-2300}"
MAX_IDLE="${KNC_MAX_IDLE_SECONDS:-1800}"

# ── Gate 1: Time Window ──────────────────────────
if [ "$ACTIVE_START" -ne 0 ] || [ "$ACTIVE_END" -ne 0 ]; then
  current_hhmm=$(date +%k%M | tr -d ' ')
  current=$(( 10#${current_hhmm:-0} ))
  start=$(( 10#${ACTIVE_START:-800} ))
  end=$(( 10#${ACTIVE_END:-2300} ))
  within=0
  if [ "$start" -lt "$end" ]; then
    [ "$current" -ge "$start" ] && [ "$current" -lt "$end" ] && within=1
  else
    [ "$current" -ge "$start" ] || [ "$current" -lt "$end" ] && within=1
  fi
  [ "$within" -ne 1 ] && echo "session-guardian: outside active hours" >&2 && exit 1
fi

# ── Gate 2: Cooldown ──────────────────────────────
project_root="${PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")}"
project_name="$(basename "$project_root")"
now="$(date +%s)"
mkdir -p "$(dirname "$LOG_PATH")"
_lock_dir="${LOG_PATH}.lock"
if ! mkdir "$_lock_dir" 2>/dev/null; then
  echo "session-guardian: locked, skipping" >&2; exit 1
fi
trap 'rm -rf "$_lock_dir"' EXIT INT TERM

last_spawn=$(awk -F '\t' -v key="$project_root" '$1 == key { print $2 }' "$LOG_PATH" 2>/dev/null || echo 0)
last_spawn="${last_spawn:-0}"
[[ "$last_spawn" =~ ^[0-9]+$ ]] || last_spawn=0
elapsed=$(( now - last_spawn ))
if [ "$elapsed" -lt "$INTERVAL" ]; then
  echo "session-guardian: cooldown for ${project_name} (${elapsed}s < ${INTERVAL}s)" >&2
  exit 1
fi
tmp_log="$(mktemp "$(dirname "$LOG_PATH")/knc-observer.XXXXXX")"
awk -F '\t' -v key="$project_root" '$1 != key' "$LOG_PATH" > "$tmp_log" 2>/dev/null || true
printf '%s\t%s\n' "$project_root" "$now" >> "$tmp_log"
mv "$tmp_log" "$LOG_PATH"

# ── Gate 3: Idle Detection ────────────────────────
if [ "$MAX_IDLE" -gt 0 ]; then
  idle=0
  case "$(uname -s)" in
    Darwin) idle=$(ioreg -c IOHIDSystem 2>/dev/null | awk '/HIDIdleTime/ {print int($NF/1000000000); exit}' || echo 0) ;;
    Linux) command -v xprintidle >/dev/null 2>&1 && idle=$(($(xprintidle 2>/dev/null || echo 0)/1000)) || idle=0 ;;
  esac
  [ "$idle" -gt "$MAX_IDLE" ] && echo "session-guardian: idle ${idle}s > ${MAX_IDLE}s" >&2 && exit 1
fi

exit 0
