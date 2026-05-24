#!/usr/bin/env bash
# continuous-learning — Observer background loop
# Analyzes observations and creates instincts.

set +e
unset CLAUDECODE

SLEEP_PID=""
USR1_FIRED=0
PENDING_ANALYSIS=0
ANALYZING=0
LAST_ANALYSIS_EPOCH=0
ANALYSIS_COOLDOWN="${KNC_ANALYSIS_COOLDOWN:-60}"
IDLE_TIMEOUT_SECONDS="${KNC_OBSERVER_IDLE_TIMEOUT:-1800}"
ACTIVITY_FILE="${PROJECT_DIR}/.observer-last-activity"

cleanup() {
  [ -n "$SLEEP_PID" ] && kill "$SLEEP_PID" 2>/dev/null
  [ -f "$PID_FILE" ] && [ "$(cat "$PID_FILE" 2>/dev/null)" = "$$" ] && rm -f "$PID_FILE"
  exit 0
}
trap cleanup TERM INT

on_usr1() {
  [ -n "$SLEEP_PID" ] && kill "$SLEEP_PID" 2>/dev/null && SLEEP_PID=""
  if [ "$ANALYZING" -eq 1 ]; then
    PENDING_ANALYSIS=1; return
  fi
  USR1_FIRED=1
  local now_epoch elapsed
  now_epoch=$(date +%s)
  elapsed=$(( now_epoch - LAST_ANALYSIS_EPOCH ))
  [ "$elapsed" -lt "$ANALYSIS_COOLDOWN" ] && return
  ANALYZING=1
  analyze_observations
  LAST_ANALYSIS_EPOCH=$(date +%s)
  ANALYZING=0
}
trap on_usr1 USR1

analyze_observations() {
  [ ! -f "$OBSERVATIONS_FILE" ] && return
  local obs_count
  obs_count=$(wc -l < "$OBSERVATIONS_FILE" 2>/dev/null || echo 0)
  [ "$obs_count" -lt "${MIN_OBSERVATIONS:-20}" ] && return

  echo "[$(date)] Analyzing $obs_count observations..." >> "$LOG_FILE"

  if ! command -v claude >/dev/null 2>&1; then
    echo "[$(date)] claude CLI not found" >> "$LOG_FILE"
    return
  fi

  # session-guardian
  bash "$(dirname "$0")/session-guardian.sh" || return

  # Tail recent observations
  observer_tmp="${PROJECT_DIR}/.observer-tmp"
  mkdir -p "$observer_tmp"
  analysis_file="$(mktemp "${observer_tmp}/knc-analysis.XXXXXX.jsonl")"
  tail -n 500 "$OBSERVATIONS_FILE" > "$analysis_file"
  analysis_relpath=".observer-tmp/$(basename "$analysis_file")"
  cd "$PROJECT_DIR" || return

  prompt=$(cat <<PROMPT
Read ${analysis_relpath} and identify SDD+TDD workflow patterns.
Look for:
1. HARD-GATE triggers and their resolutions
2. User corrections to workflow choices
3. Repeated skill sequences
4. Consistency preferences (mode/type choices)

If you find 3+ occurrences of the same pattern, write an instinct file to:
${INSTINCTS_DIR}/<id>.yaml

Instinct format:
---
id: kebab-case-name
trigger: when <specific condition>
confidence: <0.3-0.85: 3-5=0.5, 6-10=0.7, 11+=0.85>
domain: <workflow | code-quality | testing | design | process>
source: session-observation
scope: project
project_id: ${PROJECT_ID}
project_name: ${PROJECT_NAME}
---

# Title

## Action
<what to do, one clear sentence>

## Evidence
- Observed N times
- Pattern: <description>
- Last observed: <date>

Be conservative. Only create instincts for clear patterns.
Never include code snippets, only patterns.
PROMPT
  )

  OBSERVER_SKIP=1 claude --model haiku --max-turns 10 --print \
    --allowedTools "Read,Write" \
    -p "$prompt" >> "$LOG_FILE" 2>&1 &

  local claude_pid=$!
  ( sleep 120; kill "$claude_pid" 2>/dev/null || true ) &
  wait "$claude_pid" 2>/dev/null || true

  # Archive processed observations
  local archive_dir="${PROJECT_DIR}/observations.archive"
  mkdir -p "$archive_dir"
  mv "$OBSERVATIONS_FILE" "$archive_dir/processed-$(date +%Y%m%d-%H%M%S)-$$.jsonl" 2>/dev/null || true
  rm -f "$analysis_file"
}

echo "$$" > "$PID_FILE"
echo "[$(date)] KNC Observer started for ${PROJECT_NAME} (PID: $$)" >> "$LOG_FILE"

while true; do
  # Idle check
  local last_activity now_epoch idle_for
  last_activity=$(stat -c %Y "$OBSERVATIONS_FILE" 2>/dev/null || echo 0)
  now_epoch=$(date +%s)
  idle_for=$(( now_epoch - last_activity ))
  if [ "$last_activity" -gt 0 ] && [ "$idle_for" -ge "$IDLE_TIMEOUT_SECONDS" ]; then
    echo "[$(date)] Idle ${idle_for}s, exiting" >> "$LOG_FILE"
    cleanup
  fi

  if [ "$PENDING_ANALYSIS" -eq 1 ]; then
    PENDING_ANALYSIS=0; USR1_FIRED=0; ANALYZING=1
    analyze_observations
    LAST_ANALYSIS_EPOCH=$(date +%s); ANALYZING=0
    continue
  fi

  sleep "${OBSERVER_INTERVAL_SECONDS:-300}" &
  SLEEP_PID=$!
  wait "$SLEEP_PID" 2>/dev/null
  SLEEP_PID=""

  if [ "$USR1_FIRED" -eq 1 ]; then
    USR1_FIRED=0
  else
    ANALYZING=1
    analyze_observations
    LAST_ANALYSIS_EPOCH=$(date +%s)
    ANALYZING=0
  fi
done
