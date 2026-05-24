---
name: spec-import
description: 规范迁移导入 — 将项目中其他目录的规范文档迁移整合到 orch-spec/spec/ 主规范库
argument-hint: <source_dir>
---

# 规范迁移导入

将散落的规范文档统一导入 `orch-spec/spec/` 主规范库。

## 入口

```
/spec-import "source_dir"
```

## 示例

```bash
# 导入 docs/ 下所有规范文件
/spec-import "docs/"

# 导入指定文件
/spec-import "docs/api-design.md"

# 导入项目根目录旧规范
/spec-import "old-specs/"
```

## 流程

调用 `Skill("orch:spec-import", args="source_dir")`，执行扫描 → 归类 → 冲突检测 → 确认 → 合并 → 报告。

详见 `skills/spec-import/SKILL.md`。
