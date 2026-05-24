---
name: clarify
description: |
  苏格拉底式需求澄清。在 spec 之前，通过数学化模糊度评分的逐轮深度访谈澄清需求。
  在 spec 之前，通过数学化模糊度评分的逐轮深度访谈澄清需求。
  
  输入：需求描述（文本）
  输出：orch-spec/{req_id}/spec/clarification.md（澄清报告 + 模糊度分数）
---

# clarify — 苏格拉底需求澄清

## When to Use

- 需求描述模糊/开放/不确定时
- 用户说"我不太确定具体要什么"
- 需求不包含具体文件路径、函数名或验收标准

## Output

- `orch-spec/{req_id}/spec/clarification.md` — 苏格拉底澄清报告

## 职责

在 spec 之前，通过数学化模糊度评分的逐轮深度访谈，将模糊想法转化为清晰需求基线。每次只问一个问题，针对最薄弱的清晰度维度，直到模糊度降至阈值以下。

## 工作流程

```
[workflow] → 检测模糊度 > 0.2
  ↓
[clarify]
  Phase 0: 拓扑枚举 → 锁定范围形状
  Phase 1: 苏格拉底循环（每轮一问 + 评分）
  Phase 2: 挑战者模式（第4/6/8轮激活）
  Phase 3: 本体追踪（实体稳定性）
  Phase 4: 规范结晶 → clarification.md
  Phase 5: 桥接 spec
  ↓
[spec] 读取澄清结果，生成标准规范
```

## 阈值的设置

<HARD-GATE>必须先加载 config/socratic-config.json 确认阈值，不能使用硬编码默认值。</HARD-GATE>

1. 读取 `config/socratic-config.json` 中的 `ambiguityThreshold`（默认 0.2）
2. 阈值可被 `.claude/settings.json` 中的 `socratic.ambiguityThreshold` 覆盖
3. 显示当前阈值：`模糊度阈值: {threshold*100}% (来源: {source})`

## Phase 0: 拓扑枚举

在评分之前，先锁定需求的范围形状：

1. 从需求描述中提取顶层组件（1-6 个独立交付物）
2. 用 AskUserQuestion 确认拓扑结构：

```
拓扑确认 | 模糊度: 未评分

我理解这是 {N} 个顶层组件：
1. {组件名}: {一句话描述}
2. ...

是否正确？需要增/删/合并/拆分吗？
```

3. 锁定拓扑到状态，后续评分针对每个活动组件独立进行

## Phase 1: 苏格拉底循环

重复直到 `模糊度 ≤ 阈值` 或用户主动退出（第3轮后可提前退出）。

### 每轮步骤：

**Step 1: 确定最弱维度**
分析当前评分，找出模糊度最高的维度作为本轮目标。

**Step 2: 生成问题**
根据最弱维度生成针对性追问，每次只问一个：

| 维度 | 问题风格 | 示例 |
|------|---------|------|
| Goal | "具体会发生什么？" | "你说的'管理任务'，用户第一步具体做什么？" |
| Constraints | "边界在哪？" | "需要离线工作吗，还是必须联网？" |
| Criteria | "怎么算完成？" | "如果看到成品，什么会让你说'对，就是它'？" |
| Context | "如何适配现有系统？" | "src/auth/ 使用 JWT + passport，应扩展还是新建？" |

**Step 3: AskUserQuestion**
以清晰格式呈现问题：

```
第{n}轮 | 目标组件: {component} | 针对: {dimension} | 模糊度: {score}%

{question}
```

**Step 4: 评分模糊度**
接收答案后，派遣 socratic-clarifier agent 执行数学化评分：

```bash
Agent(subagent_type="orch:clarifier",
      prompt="
        对第{n}轮访谈结果进行模糊度评分：
        - 原始需求: {initial_idea}
        - 本轮回答: {answer}
        - 前轮记录: {prior_rounds_summary}
        返回 JSON: { goal_score, constraint_score, criteria_score, context_score,
                     weakest_dimension, weakest_rationale, ontology }
      ")
```

```python
# 评分模型
goal_score = 0.0-1.0  # 目标清晰度
constraint_score = 0.0-1.0  # 约束清晰度
criteria_score = 0.0-1.0  # 验收标准清晰度
context_score = 0.0-1.0  # [棕地]上下文清晰度

if 绿场:
    ambiguity = 1 - (goal*0.40 + constraints*0.30 + criteria*0.30)
else:
    ambiguity = 1 - (goal*0.35 + constraints*0.25 + criteria*0.25 + context*0.15)
```

**Step 5: 显示进度**

```
第{n}轮完成。

| 维度 | 分数 | 差距 |
|------|------|------|
| Goal | 0.85 | 清晰 |
| Constraints | 0.60 | 性能要求未定义 |
| Criteria | 0.70 | 验收标准不具体 |
| **模糊度** | **28%** | |

下一目标: Constraints — 需要确定并发量级
```

### 软限制

- **第10轮**: 软警告"已10轮，继续还是以当前清晰度推进？"
- **第20轮**: 硬上限"已达最大轮数，以当前清晰度推进"
- **第3轮+**: 允许用户选择提前退出（显示警告）

## Phase 2: 挑战者模式

在特定轮次激活不同的提问视角（各使用一次后恢复常规模式）：

### 第4轮+: Contrarian Mode
注入到问题生成提示：
> 现在处于 CONTRARIAN 模式。下一问应挑战用户的核心假设。问"如果反过来呢？"

### 第6轮+: Simplifier Mode
> 现在处于 SIMPLIFIER 模式。问"最简单的可用版本是什么？哪些约束其实不是必需的？"

### 第8轮+: Ontologist Mode（模糊度仍 > 0.3 时）
> 现在处于 ONTOLOGIST 模式。已追踪实体：{实体列表}。问"这里的核心概念到底是什么？"

## Phase 3: 本体追踪

每轮提取关键实体（名词），跨轮次追踪稳定性：

- `stable_entities`: 两轮中都出现且名称相同
- `changed_entities`: 名称不同但类型相同且字段重叠 > 50%
- `new_entities`: 本轮新增
- `removed_entities`: 本轮消失
- `stability_ratio`: (stable + changed) / total

当稳定性比率连续 2 轮达 100% 时，本体已收敛，可作为需求明确的证据。

## Phase 4: 规范结晶

当模糊度 ≤ 阈值（或硬上限/提前退出）时，生成澄清报告：

```markdown
# 苏格拉底澄清报告

## 元数据
- 轮次: {count}
- 最终模糊度: {score}%
- 类型: 绿场 | 棕地
- 阈值: {threshold}

## 清晰度分解
| 维度 | 分数 | 权重 |
|------|------|------|
| Goal | {s} | {w} |
| Constraints | {s} | {w} |
| Criteria | {s} | {w} |
| **模糊度** | | **{score}%** |

## 目标
{清晰的目标陈述}

## 约束
- {约束1}

## 验收标准
- [ ] {可测试标准1}

## 假设暴露与解决
| 假设 | 质疑 | 结论 |
|------|------|------|
| ... | ... | ... |

## 本体（关键实体）
| 实体 | 类型 | 字段 |
|------|------|------|
| ... | ... | ... |

## 本体收敛轨迹
| 轮次 | 实体数 | 稳定比率 |
|------|--------|---------|
| 1 | {n} | - |
```

输出到 `orch-spec/{req_id}/spec/clarification.md`。

## Phase 5: 桥接 spec

澄清完成后，自动级联到 spec：

```bash
Skill("orch:spec", args="{requirement_desc} (clarification: orch-spec/{req_id}/spec/clarification.md)")
```

spec 读取澄清报告，直接进入场景拆解阶段，跳过需求理解问卷。

## 快速模式

用户明确要求快速模式时：
- 跳过 Phase 0（拓扑枚举）
- 跳过 Phase 2（挑战者模式）
- 轮次上限降至 5
- 模糊度阈值放宽至 0.4

## 关键约束

| ✅ 必须 | ❌ 禁止 |
|---------|--------|
| 每轮只问一个问题 | 批量提问 |
| 显示每轮模糊度分数 | 评分不透明的推进 |
| 第3轮后支持提前退出 | 低于3轮退出 |
| 澄清输出到 orch-spec/{id}/spec/ | 写入其他目录 |
| 完成后桥接 spec | 跳过 spec 直接编码 |
| Opus 模型用于评分（temperature 0.1） | Haiku/Sonnet 评分 |
| 棕地模式先 explore 再问用户 | 让用户复述代码已有信息 |

## 参考文档

| 文档 | 场景 |
|------|------|
| `../../config/socratic-config.json` | 模糊度阈值 + 权重配置 |
| `../../agents/socratic-clarifier.md` | Scoring Agent 定义 |
| `../../commands/start-dev.md` | 步骤0.5 编排 |
