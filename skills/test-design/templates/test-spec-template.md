# test-spec-creation.md 模板

## 基础结构

```markdown
# 测试规范 - {功能名称}

**来源**：spec-dev/{req}/spec/
**TEST-VERIFY 总数**：{N}
**Test Case 总数**：{M}

## Test Case 清单

| TC-ID | TEST-VERIFY | 场景 | 测试类型 | 预期结果 |
|-------|------------|------|---------|---------|
| TC-1.1 | TV-1 | 正常路径 | 单元 | 返回成功 |
| TC-1.2 | TV-1 | 边界值 | 单元 | 抛出错误 |

## Mock 策略

| 依赖 | Mock 方式 | Fixture |
|------|----------|---------|
| API 调用 | mockResolvedValue | fixtures/api-success.json |
| 数据库 | 内存DB | fixtures/db-seed.sql |

## 覆盖率分析

- 单元测试：{N} 个 TC
- 集成测试：{N} 个场景
- E2E 测试：{N} 个流程

## TEST-VERIFY 覆盖矩阵

| TEST-VERIFY | 对应 TC | 覆盖状态 |
|------------|---------|---------|
| TV-1 | TC-1.1, TC-1.2 | ✅ 100% |
```

## 命名规范

- TC-ID：`TC-{TV序号}-{场景序号}-{变体序号}`
- 测试文件：`[feature].test.ts` / `[feature].e2e.test.ts`
- Fixture：`fixtures/[feature]-[scenario].json`
