# 代码质量审查者提示模板

调度代码质量审查子代理时使用此模板。

**目的：** 验证实现构建良好（干净、可测试、可维护）

**仅在规范一致性审查通过后才调度。**

```
Task tool (ai-code-reviewer):
  使用 ai-code-reviewer/code-reviewer.md 中的模板

  WHAT_WAS_IMPLEMENTED: [来自实现者的报告]
  PLAN_OR_REQUIREMENTS: 来自 [计划文件] 的任务 N
  BASE_SHA: [任务之前的提交]
  HEAD_SHA: [当前提交]
  DESCRIPTION: [任务摘要]
```

**代码审查者返回：** 优势、问题（严重/重要/次要）、评估
