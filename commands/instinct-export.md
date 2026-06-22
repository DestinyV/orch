---
description: 导出进化规则到 JSON/Markdown 文件。将 optimization.rules[] 序列化为可移植格式。
argument-hint: "[format] [path]"
---

# Instinct Export — 规则导出

将 `orch-spec/user-preferences/preferences.json → optimization.rules[]` 导出为可移植文件，用于备份、跨项目共享或人工审查。

## 执行流程

1. 读取 preferences.json → optimization.rules[]
2. 按参数过滤（active only / all / 指定 injection_point）
3. 输出为 JSON 或 Markdown 格式
4. 写入指定路径或 stdout

## 参数

- 无参数：stdout 输出 JSON（全部规则）
- `md`：输出 Markdown 格式
- `md <path>`：输出 Markdown 到文件
- `json <path>`：输出 JSON 到文件
- `--active-only`：仅导出 active 规则（置信度 ≥ 30）
- `--injection <point>`：仅导出指定 injection_point 的规则

## 输出格式

### JSON 导出

```json
{
  "exported_at": "ISO",
  "source": "orch-spec/user-preferences/preferences.json",
  "rules": [...]
}
```

### Markdown 导出

按 injection_point 分组，每条规则包含 observation / hypothesis / action / evolution。

## 数据来源

`orch-spec/user-preferences/preferences.json → optimization.rules[]`

## 关键约束

- 不修改源文件
- 导出文件不含项目敏感信息（仅规则结构）
