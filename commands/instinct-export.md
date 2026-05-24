---
name: instinct-export
description: 将 instincts（项目级/全局）导出为可分享的 JSON/YAML 文件。
---

# Instinct Export Command (SDD+TDD 适配版)

从 knowledge-continuum v2 导出 instincts 到可分享格式。适用于团队共享约定、迁移到新机器、贡献项目规范。

## 实现

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/knowledge-continuum/scripts/instinct-cli.py" export [--scope project|global|all] [--domain <name>] [--min-confidence <n>] [--output <file>]
```

## 用法

```
/instinct-export                                      # 导出全部（项目级 + 全局）
/instinct-export --scope project                       # 仅导出项目级 instincts
/instinct-export --scope global                        # 仅导出全局 instincts
/instinct-export --domain testing                      # 仅导出 testing 领域
/instinct-export --min-confidence 0.7                  # 仅导出置信度 ≥ 0.7 的
/instinct-export --output team-instincts.json           # 导出到指定文件
```

## 输出格式

JSON 格式：

```json
{
  "meta": {
    "exported_at": "2026-05-24T10:00:00+08:00",
    "source": "orch/knowledge-continuum",
    "count": 12
  },
  "instincts": [
    {
      "id": "prefer-functional-style",
      "trigger": "when writing new functions",
      "confidence": 0.8,
      "domain": "code-style",
      "source": "session-observation",
      "scope": "project",
      "project_id": "a1b2c3d4e5f6",
      "project_name": "my-project",
      "observations": 15
    }
  ]
}
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--scope` | 导出范围: project / global / all | all |
| `--domain` | 按领域过滤 | 全部 |
| `--min-confidence` | 置信度下限 (0-1) | 0 |
| `--output` | 输出文件路径 | stdout |
| `--format` | 输出格式: json / yaml | json |
