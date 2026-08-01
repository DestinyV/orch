# 归档日志 — orch-spec/spec/

| 项 | 值 |
|----|-----|
| 需求 ID | plugin-capability-optimization |
| 需求描述 | 插件本体全方位能力优化（元任务） |
| 需求类型 | meta-task（优化 orch 插件自身） |
| 归档日期 | 2026-08-01 |
| 归档 Agent | archiver |
| 主规范版本 | v1.0 |
| 归档类型 | **首次归档**（主规范库初始化，无既有规范可比对） |
| 测试门控 | 29 条 TEST-VERIFY：**28 VERIFIED / 1 PARTIAL / 0 MISSING**，命令 exit 全 0 |

---

## 1. 归档内容

从 `orch-spec/plugin-capability-optimization/spec/` 归档到主规范库：

| 维度 | 文件 | 数量 |
|------|------|------|
| 场景 | scenarios/S1-S6（6 文件，30 个 Case） | 6 |
| 数据模型 | data-models.md（6 个实体） | 6 |
| 业务规则 | business-rules.md（5 规则 + 4 约束 + 北极星审查结论） | 9 |
| 术语 | glossary.md（22 个术语） | 22 |

- 场景保留 S1-S6 完整内容（含 WHEN-THEN、TEST-VERIFY、Mock Data）。
- 北极星原则（约束 = 护栏非牢笼）标记为主规范**最高优先级规则**（business-rules.md 规则1）。
- 测试门控说明：TV-S6-02（自动流转率原值 83%）为 PARTIAL —— 属工作流活体测量值，无法在静态复核重测，但其判定机制 judgeRate 已独立机器验证无缺陷；非代码/规范缺陷，不阻断归档。

---

## 2. 合并结果

主规范库不存在，本次为**初始化创建**，全部维度按"完全新增"策略直接添加，无去重/修改/删除。

| 维度 | 对标结果 | 操作 | 新增数 |
|------|---------|------|--------|
| 场景对标 | 全部完全新增（库为空） | 复制 scenarios/*.md | 6 |
| 数据模型对标 | 全部字段增加（库为空） | 追加 6 实体 | 6 |
| 规则对标 | 全部新增规则 | 追加 5 规则 + 4 约束 + NSP 审查 | 9 |
| 术语对标 | 全部新增术语 | 追加 22 术语 | 22 |

**自动合并率**：100%（44/44 项自动合并）
**DECISION_NEEDED**：0（无既有规范可比对，无冲突）

---

## 3. 一致性检查

| 检查项 | 结果 |
|--------|------|
| WHEN-THEN 格式统一 | PASS — S1-S6 全部 30 个 Case 均为 WHEN-THEN 结构 |
| 引用的模型均已定义 | PASS — scenarios 引用 6 实体（optimization.rules[]/hook 注册表/agent 注册表/STAGE_OUTPUTS/自检报告/北极星审查）均在 data-models.md 定义 |
| 使用的术语均已定义 | PASS — glossary.md 覆盖 22 术语（含 GATE/北极星原则/meta-task 等） |
| 无循环依赖 | PASS — 场景依赖为 DAG：S1→S2→S4→S6、S3→S4、S5→S6，无环 |
| 版本号递增 | PASS — 主规范 v1.0（首次初始化） |
| 向后兼容 | PASS — 新建库，无既有内容受影响 |
| 冲突零容忍 | PASS — 0 冲突，无静默跳过 |

---

## 4. 规范库当前状态

| 维度 | 总数 | 详情 |
|------|------|------|
| 已归档需求 | 1 | plugin-capability-optimization |
| 场景 | 6 | S1-S6（30 个 Case） |
| 数据模型 | 6 | 优化规则 / Hook 注册表 / Agent 注册表 / STAGE_OUTPUTS / 自检报告 / 北极星审查记录 |
| 业务规则 | 9 | 5 规则 + 4 约束（北极星原则 = 最高） |
| 术语 | 22 | 含北极星原则/规则自决/白名单人工/验证闭环等 |
| 目录 | 5 文件 + 1 场景目录 | README / data-models / business-rules / glossary / archive-log + scenarios/ |

**主规范库文件**：
- `orch-spec/spec/README.md`
- `orch-spec/spec/scenarios/S1-S6`
- `orch-spec/spec/data-models.md`
- `orch-spec/spec/business-rules.md`
- `orch-spec/spec/glossary.md`
- `orch-spec/spec/archive-log.md`

---

## 5. 上下文注册中心同步

| 文件 | 更新内容 |
|------|---------|
| orch-spec/context/requirements.yaml | 追加 plugin-capability-optimization 条目（keywords / modules_touched / files_touched[36 文件] / api_routes=[] / exploration_mode=full） |
| orch-spec/context/.exploration-state.json | last_explored_sha = f07a553（当前 HEAD）；last_full_exploration = 2026-08-01；total_requirements = 1 |
| orch-spec/context/logic-chains/api-calls.yaml | 标注"无 API 变更"（后端插件元任务，无 REST 路由） |

---

## 6. 源需求标记

`orch-spec/plugin-capability-optimization/spec/requirement.md` 已追加：

```
## 归档状态
- **archived**: true
- **归档日期**: 2026-08-01
- **归档去向**: orch-spec/spec/（主规范库 v1.0）
```

---

*本日志由 archiver 生成，遵循"冲突零容忍 / 变更可追溯 / 先合并后记录"原则。*
