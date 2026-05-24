#!/usr/bin/env bash
# 知识刷新脚本 v3 — 5-outcome 刷新模型 + solution 感知
# Usage: ./knowledge-refresh.sh [knc-dir]

set -euo pipefail

KNC_DIR="${1:-${KNC_HOMUNCULUS_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/knc-homunculus}}"
PATTERNS_DIR="$(dirname "$KNC_DIR")/patterns"
SOLUTIONS_DIR="$(dirname "$KNC_DIR")/solutions"
EXPIRE_DAYS=30

log() { echo "[knowledge-refresh] $*"; }

log "=== 知识刷新 v3 (5-Outcome) ==="

# Phase 1: Scan pattern-index expiry
log "--- 扫描过期知识（>${EXPIRE_DAYS}天未更新） ---"
if command -v python3 &>/dev/null; then
  python3 -c "
import json, datetime, os
pf = os.path.join('$PATTERNS_DIR', 'pattern-index.json')
if os.path.isfile(pf):
    idx = json.load(open(pf))
    now = datetime.datetime.now()
    for p in idx.get('patterns', []):
        last = p.get('last_used', '')
        if last:
            try:
                dt = datetime.datetime.fromisoformat(last)
                days = (now - dt).days
                if days > $EXPIRE_DAYS:
                    print(f'  [Keep?] {p[\"id\"]} {p[\"name\"]} - {days}天未更新')
            except: pass
"
fi

# Phase 2: 5-Outcome classification for solutions
log "--- 5-Outcome 分类 ---"
if [ -d "$SOLUTIONS_DIR" ]; then
  for f in "$SOLUTIONS_DIR"/*.md; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    mod_days=$(( ($(date +%s) - $(stat -c %Y "$f")) / 86400 ))
    if [ "$mod_days" -gt 90 ]; then
      log "  [Stale] $name — 超过90天，建议审查 (Replace/Delete?)"
    elif [ "$mod_days" -gt "$EXPIRE_DAYS" ]; then
      log "  [Review] $name — 超过${EXPIRE_DAYS}天，建议审查 (Keep/Update?)"
    else
      log "  [Keep]  $name — 在有效期内"
    fi
  done
fi

# Phase 3: Conflict detection
log "--- 冲突检测 ---"
if command -v python3 &>/dev/null && [ -d "$SOLUTIONS_DIR" ]; then
  python3 -c "
import os, re
from collections import defaultdict
sd = '$SOLUTIONS_DIR'
triggers = defaultdict(list)
for root, _, files in os.walk(sd):
    for f in files:
        if not f.endswith('.md'): continue
        try:
            text = open(os.path.join(root, f), encoding='utf-8').read()
        except: continue
        m = re.search(r'^## (?:Problem|Context)\s+(.+)$', text, re.MULTILINE)
        if m:
            desc = m.group(1).strip()[:60]
            triggers[desc].append(f)
for desc, files in triggers.items():
    if len(files) > 1:
        print(f'  [Consolidate?] \"{desc}\" 出现在 {len(files)} 个文件中')
"
fi

# Phase 4: Inspect instincts staleness
log "--- Instinct 过期检测 ---"
if [ -d "$KNC_DIR/instincts/personal" ]; then
  for f in "$KNC_DIR/instincts/personal"/*.yaml; do
    [ -f "$f" ] || continue
    age=$(( ($(date +%s) - $(stat -c %Y "$f")) / 86400 ))
    [ "$age" -gt 60 ] && log "  [Review] $(basename "$f") — ${age}天未更新"
  done
fi

log "知识刷新 v3 完成。5-Outcome: Keep / Update / Consolidate / Replace / Delete"
