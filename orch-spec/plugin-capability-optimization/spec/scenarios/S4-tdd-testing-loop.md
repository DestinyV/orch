# 场景: S4 TDD 执行与测试闭环

**优先级**：高
**相关场景**：S1（编排）、S2（Agent）、S6（验证闭环）
**场景间依赖**：
- depends-on: S1、S2、S3（前置优化完成）
- provides-to: S6（闭环支撑验证）

---

## 场景描述

优化 TDD 执行链路与插件自身测试闭环。确保 execute 阶段的 TDD 四阶段日志完整、覆盖率验证真实，并为插件自身建立可运行的自检能力。

---

## 前置条件

- S1-S3 优化完成
- tests/test-suite.py 存在
- 探索审计确认"无插件自检命令"（最大缺口）

---

## Case 1: 插件自身自检命令建立

**目标**：修复最大缺口 —— agents/commands/hooks/scripts 无自检命令或测试

**WHEN**
```
- 用户运行插件自检命令（如 /orch:self-check 或测试脚本）
- 检查 hooks.json 注册完整性
- 检查 agent 引用有效性
- 检查 skill 引用有效性
```

**THEN**
```
- 输出自检报告：注册表校验 + 引用交叉校验 + 文件存在性
- 无损坏项 → PASS
- 有损坏项 → 列出具体文件与修复建议
- 提供可重复运行的验证命令（CI 风格）
```

**备注**：这是"每块有验证闭环"验收标准的核心交付。

---

## Case 2: TDD 四阶段日志完整性校验

**目标**：确保 execute 阶段 TDD 日志含 RED/GREEN/REFACTOR/REVIEW 四阶段证据

**WHEN**
```
- execute 阶段执行 TDD
- tdd-guide 校验四阶段
- 任一阶段缺命令输出
```

**THEN**
```
- 标记 FAILED 驳回
- 不进入下一阶段（HARD-GATE）
- 提供缺失阶段的具体命令建议
```

---

## Case 3: 覆盖率验证真实性

**目标**：确保覆盖率≥85% 的验证基于真实测试输出，非编造

**WHEN**
```
- execute 完成，声明覆盖率 ≥85%
- test-verifier 独立运行验证命令
- 对比声明值与实测值
```

**THEN**
```
- 实测 ≥85% → VERIFIED
- 实测 <85% → PARTIAL/MISSING，打回补测试
- 不接受 executor 自我报告
```

---

## Case 4: 异常情况 — 无插件测试的回归风险

**目标**：修复"插件自身无测试"的长期风险

**WHEN**
```
- 修改 plugins 自身的 hooks/scripts/agents
- 无自动化测试覆盖
- 引入回归无法及时发现
```

**THEN**
```
- 建立 hooks/scripts 的冒烟测试（Node 脚本断言）
- 建立 agent frontmatter 校验测试
- 建立 skill 引用完整性测试
- 纳入 S6 验证闭环
```

---

## 验证清单

- [ ] 自检命令可运行并输出 PASS/FAIL
- [ ] TDD 四阶段日志完整
- [ ] 覆盖率验证真实（独立运行）
- [ ] 插件自身有冒烟测试

---

## TEST-VERIFY（可测试的验收标准）

- [ ] 应运行自检命令，输出有效报告
- [ ] 应校验 TDD 日志含四阶段命令输出
- [ ] 应独立运行覆盖率验证，结果真实
- [ ] 应运行插件冒烟测试，无失败

### Mock Data

**有效输入**：
```json
{ "command": "self-check", "exit": 0, "report": "PASS" }
```

**边界值**：
```json
{ "coverage_claimed": 85, "coverage_actual": 87, "verdict": "VERIFIED" }
```

**特殊值**：
```json
{ "coverage_claimed": 90, "coverage_actual": 72, "verdict": "PARTIAL" }
```
