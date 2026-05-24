---
description: 运行 SDD+TDD HARD-GATE 质量管道：规范合规 + 测试覆盖率 + 代码质量。输出修复措施。
argument-hint: "[path|.] [--fix] [--strict]"
---

# Quality Gate Command (SDD+TDD 适配版)

运行 SDD+TDD 的 HARD-GATE 质量管道。结合规范合规检查、测试覆盖率门控和代码质量审查，确保交付物达标。

## 用法

```
/quality-gate [path|.] [--fix] [--strict]
```

- 默认目标：当前目录 (`.`)
- `--fix`：允许自动格式化/修复
- `--strict`：启用严格模式（覆盖率要求更高）

## HARD-GATE 质量管道

### Phase 1: 规范合规 (Spec Compliance)

检查 `spec-dev/` 下当前需求的规范完整性：

```bash
# 核心文件检查
test -f spec-dev/*/spec/requirement.md || echo "[HARD-GATE] requirement.md 缺失"
test -f spec-dev/*/spec/data-models.md || echo "[HARD-GATE] data-models.md 缺失"
ls spec-dev/*/spec/scenarios/*.md >/dev/null 2>&1 || echo "[HARD-GATE] scenarios/ 缺失"
test -f spec-dev/*/spec/business-rules.md || echo "[WARN] business-rules.md 缺失"
test -f spec-dev/*/design/design.md || echo "[WARN] design.md 缺失（阶段3未完成）"
```

**阻断条件**：requirement.md + data-models.md + scenarios 任一缺失 → HARD-GATE BLOCKED

### Phase 2: 测试覆盖率门控 (Coverage Gates)

根据 project-mode 检查覆盖门：

| 模式 | 单元覆盖率 | 集成/E2E | 说明 |
|------|-----------|----------|------|
| standard | ≥85% | 必须 | 常规开发 |
| quick | ≥60% | 可选 | 快速模式 |
| strict | ≥90% | 必须全覆盖 | `--strict` 模式 |

```bash
# 检测语言并运行覆盖率
if [ -f package.json ]; then
  npm test -- --coverage 2>/dev/null
elif [ -f Cargo.toml ]; then
  cargo tarpaulin 2>/dev/null
elif [ -f pyproject.toml ]; then
  pytest --cov 2>/dev/null
fi
```

**阻断条件**：覆盖率未达门控值 → HARD-GATE BLOCKED

### Phase 3: 代码质量管道 (Quality Pipeline)

检测语言/工具并运行：

| 语言 | 检查 | 命令 |
|------|------|------|
| TypeScript | Type check | `npx tsc --noEmit` |
| TypeScript | Lint | `npm run lint` |
| TypeScript | Format | `npx prettier --check` |
| Python | Lint | `ruff check` |
| Python | Format | `ruff format --check` |
| Rust | Lint | `cargo clippy -- -D warnings` |
| Go | Vet | `go vet ./...` |

`--fix` 时自动修复可格式化的问题。

### Phase 4: HARD-GATE 决策

```
╔══════════════════════════════════════╗
║        HARD-GATE 质量报告            ║
╚══════════════════════════════════════╝

Phase 1 — 规范合规:     [PASS/FAIL]
Phase 2 — 覆盖率:        [PASS/FAIL] ({actual}%, threshold {threshold}%)
Phase 3 — Type check:   [PASS/FAIL]
Phase 3 — Lint:         [PASS/FAIL]
Phase 3 — Format:       [PASS/FAIL]
Phase 3 — Tests:        [PASS/FAIL]

==> RESULT: PASS | BLOCKED
```

**阻断**：任一 Phase 1/2 失败，或 Phase 3 中 security 级别问题 → BLOCKED

## 输出

报告包含：
1. 各 Phase 状态 (PASS/FAIL/BLOCKED)
2. 失败项的具体修复措施
3. 自动修复的变更摘要（`--fix` 时）

## 与工作流集成

HARD-GATE 在工作流的以下时机自动触发：
- `design` → 设计完成时
- `execute` → 每 Task 规范审查 + 质量审查
- `test` → 闭环验证时
- `archive` → 归档前终检

`/quality-gate` 允许在任意时刻手动触发完整管道。
