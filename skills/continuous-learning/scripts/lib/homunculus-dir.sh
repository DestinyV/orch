#!/usr/bin/env bash
# continuous-learning — Homunculus directory resolution
# Sourced by observe.sh, start-observer.sh, and instinct-cli.py wrappers.

_ecc_resolve_homunculus_dir() {
  local override="${KNC_HOMUNCULUS_DIR:-}"
  if [ -n "$override" ]; then
    printf '%s\n' "$override"
    return
  fi

  local xdg="${XDG_DATA_HOME:-}"
  if [ -n "$xdg" ]; then
    printf '%s\n' "${xdg}/knc-homunculus"
    return
  fi

  printf '%s\n' "${HOME}/.local/share/knc-homunculus"
}
