#!/usr/bin/env bash
# Instinct observation hook — POSIX 薄包装（满足 observe.sh 文件契约 + 非 Windows 平台）
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec node "$DIR/observe.js" "$@"
