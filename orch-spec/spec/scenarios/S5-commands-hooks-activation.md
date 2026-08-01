# 场景: S5 Commands + Hooks 激活

**优先级**：中
**相关场景**：S1（编排）、S3（Skills）
**场景间依赖**：
- depends-on: S1（门控修正）
- provides-to: S6（激活的 hook 参与验证）

---

## 场景描述

激活已实现但未注册的自动化能力，修复文档漂移，统一命令/Skill 命名空间。确保 CLAUDE.md 声明与 hooks.json 实际一致。

---

## 前置条件

- 探索审计已定位 F3/F4/F6/F9/F11
- scripts/hooks/suggest-compact.js 存在
- hooks.json 6 项注册

---

## Case 1: suggest-compact.js 注册激活

**目标**：修复 F3 —— 有脚本未注册，compact 建议功能未激活

**WHEN**
```
- scripts/hooks/suggest-compact.js 已实现（阈值 40 次 Edit/Write）
- hooks.json 无对应注册项
- CLAUDE.md 宣称存在 compact 建议
```

**THEN**
```
- hooks.json 补注册 PreToolUse(Edit/Write) → suggest-compact.js
- 激活逻辑边界 compact 建议功能
```

---

## Case 2: instinct 观察 hook 激活或清理

**目标**：修复 F4 —— observe.sh 缺失，instinct 观察层死配置

**WHEN**
```
- CLAUDE.md 宣称 PreToolUse/PostToolUse observe.sh
- hook-flags.js PROFILES 含 pre:observe/post:observe
- observe.sh 文件不存在，hooks.json 未注册
```

**THEN**
```
- 处置方案 A：实现 observe.sh 并注册（激活 instinct 学习层）
- 处置方案 B：清理死配置（hook-flags + CLAUDE.md）
- 与 S3 Case5 的 observer 状态确认联动
```

---

## Case 3: CLAUDE.md 钩子表同步

**目标**：修复 F6 —— CLAUDE.md 钩子表与 hooks.json 脱节

**WHEN**
```
- CLAUDE.md 钩子表仍写 observe.sh / suggest-compact.js
- hooks.json 实际注册不同
```

**THEN**
```
- 同步 CLAUDE.md 钩子表与 hooks.json 实际一致
- 消除文档漂移
```

---

## Case 4: 文档漂移全面修复

**目标**：修复 README.md / AGENTS.md / .claude-plugin/README.md / file-map.yaml / index.json

**WHEN**
```
- README 宣称 11 skills/9 agents//orch:sdd-dev
- AGENTS.md 宣称 25 agents
- .claude-plugin/README 宣称 18 skills/12 commands
- file-map.yaml 结构过时
- index.json 未注册新 section
```

**THEN**
```
- README 同步为 22 skills/26 agents//start-dev
- AGENTS.md 注册 tdd-guide（或标注 deprecated）
- .claude-plugin/README 同步为 22 skills/14 commands
- file-map.yaml 更新
- index.json 注册 tech-stack/architecture/conventions/project-context
```

---

## Case 5: __pycache__ 清理

**目标**：修复 F11 —— scripts/__pycache__/*.pyc 已提交 git

**WHEN**
```
- git ls-files 检查到 scripts/__pycache__/*.pyc
- 构建产物入库
```

**THEN**
```
- 从 git 移除 pyc 文件
- .gitignore 添加 __pycache__/ *.pyc
```

---

## 验证清单

- [ ] suggest-compact.js 已注册激活
- [ ] observe.sh 激活或死配置清理
- [ ] CLAUDE.md 钩子表与 hooks.json 一致
- [ ] 全部文档数量口径一致
- [ ] 无 pyc 入库

---

## TEST-VERIFY（可测试的验收标准）

- [ ] 应校验 hooks.json 含 suggest-compact 注册项
- [ ] 应校验 observe 相关配置非死引用
- [ ] 应比对 CLAUDE.md 钩子表与 hooks.json
- [ ] 应 grep 确认文档数量口径一致（22/26/14）
- [ ] 应 git ls-files 确认无 *.pyc

### Mock Data

**有效输入**：
```json
{ "hook": "suggest-compact", "registered": true }
```

**边界值**：
```json
{ "observe": "observe.sh", "state": "activated" }
```

**特殊值**：
```json
{ "doc": "README.md", "skills": 22, "agents": 26 }
```
