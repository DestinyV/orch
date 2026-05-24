---
name: instinct-import
description: 从 JSON/YAML 文件或 URL 导入 instincts 到项目级或全局作用域。
---

# Instinct Import Command (SDD+TDD 适配版)

从本地文件或 HTTP(S) URL 导入 instincts 到 knowledge-continuum v2。支持冲突检测、置信度比较和干运行预览。

## 实现

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/instinct-cli.py" import <file-or-url> [--dry-run] [--force] [--min-confidence <n>] [--scope project|global]
```

## 用法

```
/instinct-import team-instincts.json                        # 导入本地文件
/instinct-import https://org/repo/instincts.json             # 从 URL 导入
/instinct-import team-instincts.json --dry-run               # 预览（不实际导入）
/instinct-import team-instincts.json --scope global --force  # 导入到全局，跳过确认
/instinct-import team-instincts.json --min-confidence 0.7   # 仅导入置信度 ≥ 0.7 的
```

## 导入过程

```
 Importing instincts from: team-instincts.json
================================================

Found 12 instincts to import.

Analyzing conflicts...

## New Instincts (8)
These will be added:
  ✓ use-zod-validation (confidence: 0.7)
  ✓ prefer-named-exports (confidence: 0.65)
  ✓ test-async-functions (confidence: 0.8)

## Duplicate Instincts (3)
Already have similar instincts:
  WARNING: prefer-functional-style
     Local: 0.8 confidence, 12 observations
     Import: 0.7 confidence
     → Keep local (higher confidence)

  WARNING: test-first-workflow
     Local: 0.75 confidence
     Import: 0.9 confidence
     → Update to import (higher confidence)

Import 8 new, update 1?
```

## 合并策略

导入时带有冲突处理：
- 传入的 instinct 置信度更高 → 更新候选
- 传入的 instinct 置信度更低或相等 → 跳过
- 差异在 ±0.05 内视为同等 → 保留本地
- 用户确认后才执行（除非 `--force`）

## 来源追踪

导入的 instincts 标记为：

```
source: inherited
scope: {project|global}
imported_from: "team-instincts.json"
imported_at: "2026-05-24T10:00:00+08:00"
```

## 输出

```
PASS: Import complete!

Added: 8 instincts
Updated: 1 instinct
Skipped: 3 instincts (equal/higher confidence already exists)

New instincts saved to:
  ~/.local/share/knc-homunculus/instincts/inherited/

Run /instinct-status to see all instincts.
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<file-or-url>` | 本地文件路径或 HTTP(S) URL | 必填 |
| `--dry-run` | 预览不实际导入 | false |
| `--force` | 跳过确认提示 | false |
| `--min-confidence` | 置信度下限 (0-1) | 0 |
| `--scope` | 目标范围: project / global | project |
