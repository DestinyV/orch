#!/bin/bash
# continuous-learning — Observation Hook
#
# Captures PreToolUse/PostToolUse events for instinct-based pattern analysis.
# Integration layer between orch workflow and instinct learning.
#
# Registered via plugin hooks/hooks.json (auto-loaded).
# Can also be registered manually in ~/.claude/settings.json.
#
# Observation hook for continuous-learning instinct learning.
# scoped to capture orch workflow decisions (HARD-GATE triggers,
# pattern matches, user corrections) as instinct observations.

set -e

HOOK_PHASE="${1:-}"
if [ -z "$HOOK_PHASE" ]; then
  case "${CLAUDE_HOOK_EVENT_NAME:-}" in
    PreToolUse|pretooluse|pre_tool_use|pre) HOOK_PHASE="pre" ;;
    PostToolUse|posttooluse|post_tool_use|post) HOOK_PHASE="post" ;;
    *) HOOK_PHASE="post" ;;
  esac
fi

INPUT_JSON=$(cat)
[ -z "$INPUT_JSON" ] && exit 0

# ── Python resolution ──────────────────────────────
_is_windows_app_installer_stub() {
  local _candidate="$1"
  [ -z "$_candidate" ] && return 1
  local _resolved
  _resolved="$(command -v "$_candidate" 2>/dev/null || true)"
  [ -z "$_resolved" ] && return 1
  case "$_resolved" in
    *AppInstallerPythonRedirector.exe|*AppInstallerPythonRedirector.EXE) return 0 ;;
  esac
  if command -v readlink >/dev/null 2>&1; then
    local _target
    _target="$(readlink -f "$_resolved" 2>/dev/null || readlink "$_resolved" 2>/dev/null || true)"
    case "$_target" in
      *AppInstallerPythonRedirector.exe|*AppInstallerPythonRedirector.EXE) return 0 ;;
    esac
  fi
  return 1
}

resolve_python_cmd() {
  if [ -n "${KNC_PYTHON_CMD:-}" ] && command -v "$KNC_PYTHON_CMD" >/dev/null 2>&1; then
    printf '%s\n' "$KNC_PYTHON_CMD"; return 0
  fi
  if command -v python3 >/dev/null 2>&1 && ! _is_windows_app_installer_stub python3; then
    printf '%s\n' python3; return 0
  fi
  if command -v python >/dev/null 2>&1 && ! _is_windows_app_installer_stub python; then
    printf '%s\n' python; return 0
  fi
  return 1
}

PYTHON_CMD="$(resolve_python_cmd 2>/dev/null || true)"
[ -z "$PYTHON_CMD" ] && exit 0

# ── Config ──────────────────────────────────────────
KNC_HOMUNCULUS_DIR="${KNC_HOMUNCULUS_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/knc-homunculus}"
OBSERVATIONS_FILE="${KNC_HOMUNCULUS_DIR}/observations.jsonl"
mkdir -p "$(dirname "$OBSERVATIONS_FILE")"
touch "$OBSERVATIONS_FILE"

# ── Parse + write observation ──────────────────────
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "$INPUT_JSON" | HOOK_PHASE="$HOOK_PHASE" TS="$timestamp" "$PYTHON_CMD" -c '
import json, sys, os, re

data = json.load(sys.stdin)
hook_phase = os.environ.get("HOOK_PHASE", "post")
event = "tool_start" if hook_phase == "pre" else "tool_complete"

tool_name = data.get("tool_name", data.get("tool", "unknown"))
tool_input = data.get("tool_input", data.get("input", {}))
tool_output = data.get("tool_response", data.get("tool_output", data.get("output", "")))
session_id = data.get("session_id", "unknown")
tool_use_id = data.get("tool_use_id", "")

# Truncate large payloads
def truncate(v, limit=2000):
    if v is None: return None
    s = json.dumps(v) if isinstance(v, dict) else str(v)
    return s[:limit]

# Scrub secrets
_SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|token|secret|password|authorization|credentials?|auth)"
    r"""(["'"'"'\s:=]+)"""
    r"([A-Za-z]+\s+)?" r"([A-Za-z0-9_\-/.+=]{8,})"
)
def scrub(val):
    if val is None: return None
    return _SECRET_RE.sub(lambda m: m.group(1)+m.group(2)+(m.group(3) or "")+"[REDACTED]", str(val))

obs = {
    "timestamp": os.environ["TS"],
    "event": event,
    "tool": tool_name,
    "session": session_id,
    "tool_use_id": tool_use_id,
}
if event == "tool_start":
    obs["input_summary"] = truncate(scrub(tool_input))
else:
    obs["output_summary"] = truncate(scrub(tool_output))

print(json.dumps(obs))
' >> "$OBSERVATIONS_FILE" 2>/dev/null || true

exit 0
