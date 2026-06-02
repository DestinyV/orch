---
name: spec-migrate
description: 规范迁移导入 — 将项目中其他目录的规范文档迁移整合到 orch-spec/spec/ 主规范库
argument-hint: <source_dir>
---

# 规范迁移导入

将散落的规范文档导入 `orch-spec/spec/` 主规范库。不创建临时目录，直接按字段级/行级/文件级合并策略写入。

## 入口

```
/spec-migrate "source_dir"
```

## 示例

```bash
# 导入 docs/ 下所有规范文件
/spec-migrate "docs/"

# 导入指定文件
/spec-migrate "docs/api-design.md"

# 导入项目根目录旧规范
/spec-migrate "old-specs/"
```

## 流程

调用 `Skill("orch:spec-migrate", args="source_dir")`，执行扫描 → 去重 → 冲突确认 → 按类型合并写入 → 报告生成。

详见 `skills/spec-migrate/SKILL.md`。
