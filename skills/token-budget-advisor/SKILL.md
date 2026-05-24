---
name: token-budget-advisor
description: |
  在响应前向用户提供深度选择（25%/50%/75%/100%），帮助控制 Token 消耗和响应长度。
  TRIGGER when: 用户提及 "token budget"、"简短回答"、"50%深度"、"控制长度"、"节省token"、"详细回答"、"exhaustive"。
  DO NOT TRIGGER when: 用户已在本会话中设定深度级别、答案显然为一行、"token" 指认证/会话 token。
origin: community
---

# Token Budget Advisor (TBA)

在 Claude 回答之前拦截响应流，提供响应深度选择。

## 何时使用

- 用户想控制响应长度或详细程度
- 用户提到 token、budget、depth、response length
- 用户说 "short version"、"tldr"、"brief"、"详细回答"、"exhaustive"
- 任何用户想预先选择深度/细节级别的场景

**不触发**: 用户已在本会话设置过级别（静默维持），或答案显然为一行。

## 工作原理

### Step 1 — 估算输入 Token

用启发式估算输入 Token 数：
- 散文: `words × 1.3`
- 代码/混合: `chars / 4`
- 混合内容取主导类型

### Step 2 — 按复杂度估算响应范围

| Complexity | Multiplier | Example |
|------------|-----------|---------|
| Simple | 3× - 8× | "What is X?" |
| Medium | 8× - 20× | "How does X work?" |
| Medium-High | 10× - 25× | 代码请求 + 上下文 |
| Complex | 15× - 40× | 多部分分析、架构 |
| Creative | 10× - 30× | 故事、文章 |

Response window = `input_tokens × mult_min` to `input_tokens × mult_max`

### Step 3 — 呈现深度选项

在回答前呈现：

```
Input: ~[N] tokens  |  Type: [type]  |  Complexity: [level]  |  Language: [lang]

Choose response depth:

[1] Essential   (25%)  ->  ~[tokens]   Direct answer only
[2] Moderate    (50%)  ->  ~[tokens]   Answer + context + 1 example
[3] Detailed    (75%)  ->  ~[tokens]   Full answer with alternatives
[4] Exhaustive (100%)  ->  ~[tokens]   Everything, no limits

Which level? (1-4 or "25% depth" etc.)
```

### Step 4 — 按深度级别响应

| Level | Target | Include | Omit |
|-------|--------|---------|------|
| 25% Essential | 2-4 sentences | Direct answer | Context, examples |
| 50% Moderate | 1-3 paragraphs | Answer + context + 1 example | Deep analysis |
| 75% Detailed | Structured | Multiple examples, pros/cons | Edge cases |
| 100% Exhaustive | No limit | Everything | Nothing |

## 快捷键 — 跳过提问

| User says | Level |
|-----------|-------|
| "1" / "25% depth" / "short version" / "tldr" | 25% |
| "2" / "50% depth" / "moderate" / "balanced" | 50% |
| "3" / "75% depth" / "detailed" / "thorough" | 75% |
| "4" / "100% depth" / "exhaustive" / "full deep dive" | 100% |

用户在本会话中设定过级别 → 静默维持，除非主动更改。

## 精度

启发式估算 ~85-90% 准确度（±15%）。始终显示精度声明。

## 集成

与 `context-budget` 配合：先审计当前上下文占用量，再用 TBA 控制单次响应开销。
与 `strategic-compact` 配合：深度响应后建议 compaction 释放上下文。

## 关键约束

- ✅ 用户指定深度后立即响应，不再提问
- ✅ 会话内保持同一级别
- ❌ 不估算实际模型定价（由 cost-tracking 负责）
- ❌ 不读取文件内容（只基于启发式估算）


## Output

按用户选择的深度级别提供的回答（25% Essential / 50% Moderate / 75% Detailed / 100% Exhaustive）。

## Constraints

- 用户指定深度后立即响应，不再提问
- 会话内保持同一级别
- 不估算实际模型定价（由 cost-tracking 负责）
- 不读取文件内容（只基于启发式估算）

<HARD-GATE>不估算模型定价（由 cost-tracking 负责） | 不读取文件内容（仅启发式估算）</HARD-GATE>