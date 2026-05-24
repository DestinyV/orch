#!/usr/bin/env bash
# 知识提炼脚本 v2 — 去重提炼 + instinct 感知 + 频次统计 + 抽象压缩
# Usage: ./knowledge-distill.sh [homunculus-dir]

set -euo pipefail

KNC_DIR="${1:-${KNC_HOMUNCULUS_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/knc-homunculus}}"
INDEX="$KNC_DIR/../patterns/pattern-index.json"
PATTERNS_DIR="$KNC_DIR/../patterns"

# Also scan instincts
INSTINCT_GLOBAL="$KNC_DIR/instincts/personal"
INSTINCT_INHERITED="$KNC_DIR/instincts/inherited"

log() { echo "[knowledge-distill] $*"; }

if [ ! -f "$INDEX" ] && [ ! -d "$INSTINCT_GLOBAL" ]; then
  log "No pattern index or instincts found."
  exit 0
fi

log "=== 知识提炼 v2 (Instinct-Aware) ==="

# 1. Count instinct confidence distribution
total_instincts=0
high_confidence=0
if [ -d "$INSTINCT_GLOBAL" ]; then
  for f in "$INSTINCT_GLOBAL"/*.yaml; do
    [ -f "$f" ] || continue
    total_instincts=$((total_instincts + 1))
    if grep -q "^confidence: [0-9]\.[7-9]" "$f" 2>/dev/null; then
      high_confidence=$((high_confidence + 1))
    fi
  done
  log "Global instincts: $total_instincts (high-confidence: $high_confidence)"
fi

# 2. Project-scoped instinct count
if [ -d "$KNC_DIR/projects" ]; then
  for pdir in "$KNC_DIR/projects"/*/; do
    [ -d "$pdir" ] || continue
    pname=$(basename "$pdir")
    pcount=$(find "$pdir/instincts" -name "*.yaml" 2>/dev/null | wc -l)
    log "  Project $pname: $pcount instincts"
    # Promote candidates: instinct appears in 2+ projects
    for inst in "$pdir/instincts/personal"/*.yaml; do
      [ -f "$inst" ] || continue
      iid=$(grep "^id:" "$inst" 2>/dev/null | head -1 | sed 's/^id: *//')
      [ -n "$iid" ] || continue
      matches=$(find "$KNC_DIR/projects" -path "*/instincts/personal/${iid}.yaml" 2>/dev/null | wc -l)
      if [ "$matches" -ge 2 ]; then
        log "  → Promote candidate: $iid (appears in $matches projects)"
      fi
    done
  done
fi

# 3. Update pattern-index frequency (original logic)
if [ -f "$INDEX" ] && command -v python3 &>/dev/null; then
  python3 -c "
import json, sys
idx = json.load(open('$INDEX'))
patterns = sorted(idx.get('patterns', []), key=lambda p: p.get('frequency', 0), reverse=True)
for p in patterns:
    freq = p.get('frequency', 0)
    status = '核心' if freq >= 5 else '常用' if freq >= 2 else '低频'
    print(f'  [{status}] {p[\"id\"]} {p[\"name\"]} - 使用{freq}次')
"
fi

# 4. File size check (patterns)
for f in "$PATTERNS_DIR"/*.md 2>/dev/null; do
  [ -f "$f" ] || continue
  lines=$(wc -l < "$f" 2>/dev/null || echo 0)
  [ "$lines" -gt 200 ] && log "  ⚠️  $(basename "$f"): ${lines}行 - 建议拆分为核心+详情"
done

log "知识提炼 v2 完成。运行 instinct-cli.py evolve 以集群近似 instincts"
