#!/usr/bin/env bash
# continuous-learning — Project detection helper
#
# Detects current project context for project-scoped instincts.
# Sets: PROJECT_ID, PROJECT_NAME, PROJECT_ROOT, PROJECT_DIR
#
# Sourced by observe.sh, start-observer.sh, and hook wrappers.

set -e

# Use env var override if set
if [ -n "${KNC_PROJECT_ID:-}" ] && [ -n "${KNC_PROJECT_NAME:-}" ]; then
  PROJECT_ID="$KNC_PROJECT_ID"
  PROJECT_NAME="$KNC_PROJECT_NAME"
  PROJECT_ROOT="${KNC_PROJECT_ROOT:-$PWD}"
  PROJECT_DIR="${KNC_HOMUNCULUS_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/knc-homunculus}/projects/${PROJECT_ID}"
  mkdir -p "$PROJECT_DIR"
  return 0
fi

# Detect from git
GIT_TOPLEVEL="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "$GIT_TOPLEVEL" ]; then
  PROJECT_ROOT="$GIT_TOPLEVEL"
  PROJECT_NAME="$(basename "$GIT_TOPLEVEL")"

  # Use git remote for stable project ID
  GIT_REMOTE="$(git -C "$GIT_TOPLEVEL" remote get-url origin 2>/dev/null || echo "")"
  if [ -n "$GIT_REMOTE" ]; then
    PROJECT_ID="$(echo "$GIT_REMOTE" | md5sum 2>/dev/null | cut -c1-12 || echo "$PROJECT_NAME" | md5sum 2>/dev/null | cut -c1-12 || echo "$PROJECT_NAME" | python3 -c "import sys,hashlib; print(hashlib.md5(sys.stdin.read().encode()).hexdigest()[:12])" 2>/dev/null || echo "unknown")"
  else
    PROJECT_ID="$(echo "$GIT_TOPLEVEL" | md5sum 2>/dev/null | cut -c1-12 || python3 -c "import sys,hashlib; print(hashlib.md5(sys.stdin.read().encode()).hexdigest()[:12])" 2>/dev/null <<< "$GIT_TOPLEVEL" || echo "unknown")"
  fi
  PROJECT_ID="${PROJECT_ID:-local}"
  PROJECT_DIR="${KNC_HOMUNCULUS_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/knc-homunculus}/projects/${PROJECT_ID}"
  mkdir -p "$PROJECT_DIR"
  return 0
fi

# Fallback: global
PROJECT_ID="global"
PROJECT_NAME="global"
PROJECT_ROOT="$PWD"
PROJECT_DIR="${KNC_HOMUNCULUS_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/knc-homunculus}"
