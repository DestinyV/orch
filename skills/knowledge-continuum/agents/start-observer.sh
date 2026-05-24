#!/usr/bin/env bash
# knowledge-continuum — Observer Agent Launcher
#
# Starts/stops the background observer agent that analyzes observations
# and creates instincts.
#
# Usage:
#   start-observer.sh          # Start observer for current project
#   start-observer.sh --reset  # Clear lock and restart
#   start-observer.sh stop     # Stop running observer
#   start-observer.sh status   # Check if observer is running

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OBSERVER_LOOP_SCRIPT="${SCRIPT_DIR}/observer-loop.sh"

# shellcheck disable=SC1091
. "${SKILL_ROOT}/scripts/detect-project.sh"

# shellcheck disable=SC1091
. "${SKILL_ROOT}/scripts/lib/homunculus-dir.sh"
CONFIG_DIR="$(_ecc_resolve_homunculus_dir)"

CONFIG_FILE="${KNC_CONFIG:-${CONFIG_DIR}/config.json}"
[ ! -f "$CONFIG_FILE" ] && CONFIG_FILE="${SKILL_ROOT}/config.json"

PID_FILE="${PROJECT_DIR}/.observer.pid"
LOG_FILE="${PROJECT_DIR}/observer.log"
OBSERVATIONS_FILE="${PROJECT_DIR}/observations.jsonl"
INSTINCTS_DIR="${PROJECT_DIR}/instincts/personal"

read_config() {
  if [ ! -f "$CONFIG_FILE" ]; then
    OBSERVER_INTERVAL_SECONDS=300; MIN_OBSERVATIONS=20; OBSERVER_ENABLED=false
    return
  fi
  local c
  c=$(python3 -c "
import json
with open('$CONFIG_FILE') as f:
    cfg = json.load(f)
obs = cfg.get('observer', {})
print(obs.get('run_interval_minutes', 5))
print(obs.get('min_observations_to_analyze', 20))
print(str(obs.get('enabled', False)).lower())
" 2>/dev/null || echo "5\n20\nfalse")
  OBSERVER_INTERVAL_SECONDS=$(($(echo "$c" | sed -n '1p') * 60))
  MIN_OBSERVATIONS=$(echo "$c" | sed -n '2p')
  OBSERVER_ENABLED=$(echo "$c" | sed -n '3p')
  [ -z "$OBSERVER_INTERVAL_SECONDS" ] && OBSERVER_INTERVAL_SECONDS=300
  [ -z "$MIN_OBSERVATIONS" ] && MIN_OBSERVATIONS=20
  [ "$OBSERVER_ENABLED" != "true" ] && OBSERVER_ENABLED=false
}

stop_observer() {
  if [ -f "$PID_FILE" ]; then
    pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
      echo "Stopping observer (PID: $pid)..."
      kill "$pid" 2>/dev/null || true
      rm -f "$PID_FILE"
      echo "Observer stopped."
      return 0
    fi
    echo "Stale PID file, removing."
    rm -f "$PID_FILE"
  fi
  echo "Observer not running."
  return 1
}

case "${1:-start}" in
  stop)
    stop_observer
    exit 0 ;;
  status)
    if [ -f "$PID_FILE" ]; then
      pid=$(cat "$PID_FILE")
      if kill -0 "$pid" 2>/dev/null; then
        inst_count=$(find "$INSTINCTS_DIR" -name "*.yaml" 2>/dev/null | wc -l)
        echo "Observer running (PID: $pid)"
        echo "Log: $LOG_FILE"
        echo "Instincts: $inst_count"
        exit 0
      fi
      rm -f "$PID_FILE"
    fi
    echo "Observer not running"
    exit 1 ;;
  start)
    if [ "$2" = "--reset" ]; then
      rm -f "${PROJECT_DIR}/.observer.lock"
    fi
    read_config
    if [ "$OBSERVER_ENABLED" != "true" ]; then
      echo "Observer disabled in config (observer.enabled: false)"
      exit 1
    fi
    if [ -f "$PID_FILE" ]; then
      pid=$(cat "$PID_FILE")
      if kill -0 "$pid" 2>/dev/null; then
        echo "Observer already running (PID: $pid)"
        exit 0
      fi
      rm -f "$PID_FILE"
    fi
    mkdir -p "$PROJECT_DIR" "$INSTINCTS_DIR"
    touch "$LOG_FILE"
    nohup env \
      CONFIG_DIR="$CONFIG_DIR" \
      PID_FILE="$PID_FILE" \
      LOG_FILE="$LOG_FILE" \
      OBSERVATIONS_FILE="$OBSERVATIONS_FILE" \
      INSTINCTS_DIR="$INSTINCTS_DIR" \
      PROJECT_DIR="$PROJECT_DIR" \
      PROJECT_NAME="$PROJECT_NAME" \
      PROJECT_ID="$PROJECT_ID" \
      MIN_OBSERVATIONS="$MIN_OBSERVATIONS" \
      OBSERVER_INTERVAL_SECONDS="$OBSERVER_INTERVAL_SECONDS" \
      "$OBSERVER_LOOP_SCRIPT" >> "$LOG_FILE" 2>&1 &
    sleep 2
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
      echo "Observer started (PID: $(cat "$PID_FILE"))"
    else
      echo "Failed to start observer (check $LOG_FILE)"
      exit 1
    fi
    ;;
esac
