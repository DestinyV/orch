# 知识复利引擎

## 核心原则

**知识复利是辅助增强，不是流程省略。**

| ❌ 错误用法 | ✅ 正确用法 |
|-----------|-----------|
| "上次做过类似的，跳过追问" | "上次遗漏了异常处理，本次增加追问" |
| "用户偏好 A 方案，直接用" | "推荐 A 方案，但需确认是否仍然适用" |
| "历史没出过问题，不检查了" | "历史这个场景返工 3 次，本次重点检查" |

**第一要义：每次新需求都必须完整执行全部流程，不因历史经验而省略任何确认步骤。**

## 能力矩阵

```
识别 → 沉淀 → 提炼 → 刷新 → 自适应
  ↓      ↓      ↓      ↓      ↓
发现模式  写入库  去重抽象  更新过期  增强注入
```

### 1. 识别（Identify）

**触发时机**：每个 Skill 阶段完成后
**操作**：
- 记录关键决策（用户选择了什么方案）
- 记录卡点（哪个 HARD-GATE 被触发）
- 记录用户反馈（修改了哪些内容）

### 2. 沉淀（Accumulate）

**触发时机**：工作流完成时
**操作**：
- 匹配 `knowledge/patterns/` 中已有模式
- 新模式写入对应 pattern 文件
- 重复模式更新 `frequency` 和 `last_used`

### 3. 提炼（Distill）

**触发时机**：每完成 3 个需求或手动触发
**操作**：
- 去重：相似模式合并
- 优先级：按出现频次排序（高频→核心，低频→归档）
- 抽象：从具体案例提炼通用规则
- 压缩：超过 200 行的模式文件拆分为核心+详情

### 4. 刷新（Refresh）

**触发时机**：手动触发 `/knowledge-refresh` 或自动（30 天未更新）
**操作**：
- 扫描过期知识（>30 天未验证）
- 检测冲突知识（新旧矛盾）
- AskUserQuestion 确认保留/合并/删除策略

### 5. 自适应（Adapt）

**触发时机**：新需求启动时
**原则**：静默增强，不主动弹窗干扰核心流程。

**三层过滤机制**：
| 层 | 规则 | 示例 |
|---|------|------|
| **匹配过滤** | 新需求 vs 历史模式匹配度 ≥ 80% 才触发 | 历史遗漏"虚拟号段"，当前需求涉及手机号 → 触发 |
| **精简提炼** | 同类问题合并为 1 条，只提示"遗漏了什么" | 5 条具体问题 → "曾遗漏 5 项校验" |
| **静默注入** | 写入检查清单，不主动 AskUserQuestion | 追加到 spec 内部 checklist |

**注入时机**：
- spec 阶段1：加载历史相关风险摘要
- execute 阶段：追加历史遗漏项到质量检查清单
- 仅当当前需求确实遗漏时才提示用户

## 知识库结构

```
continuous-learning/
├── patterns/                    # 常见问题模式库（10个抽象模式）
│   ├── pattern-index.json       # 模式索引（关键词 + 频次）
│   ├── architecture-patterns.md # 架构设计模式
│   ├── data-governance.md       # 数据治理模式
│   ├── contracts.md         # 接口契约模式
│   ├── security-patterns.md     # 安全防护模式
│   ├── integration-patterns.md  # 系统集成模式
│   ├── performance-patterns.md  # 性能优化模式
│   ├── resilience-patterns.md   # 容错与韧性模式
│   ├── ui-interaction.md        # 交互与状态模式
│   ├── deployment-patterns.md   # 部署与发布模式
│   └── observability.md         # 可观测性模式
├── user-preferences/            # 用户偏好
│   └── preferences.json         # 偏好配置 + 历史记录
├── references/                  # 参考文档
│   └── continuous-learning.md   # 本文件
└── scripts/                     # 工具脚本
    ├── knowledge-refresh.sh     # 知识刷新
    └── knowledge-distill.sh     # 知识提炼
```

## 使用示例

### 场景1：数据库设计

**历史**：用户常遗漏 `updated_at` 字段和字符集定义
**本次增强**：
- spec 阶段1.7 数据库设计确认时，自动检查是否包含 `updated_at`
- 如果不包含，追加追问："是否需要添加 updated_at 审计字段？"

### 场景2：表单开发

**历史**：用户常遗漏防重复提交和 Loading 状态
**本次增强**：
- design 阶段测试性设计时，提示："历史表单需求常遗漏防重复提交，请确认是否已设计"

### 场景3：API 设计

**历史**：列表接口常遗漏排序和分页参数
**本次增强**：
- contract 阶段审查时，自动检查：`size`、`page`、`sort` 参数是否定义

## 知识刷新流程

```bash
# 手动触发
/knowledge-refresh

# 或执行脚本
bash "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/knowledge-refresh.sh"
```

刷新步骤：
1. 扫描所有 pattern 文件，标记超过 30 天未更新的知识
2. 检测新旧知识冲突（如矛盾的 API 规范）
3. AskUserQuestion 展示待处理项，用户确认保留/合并/删除
4. 更新 `pattern-index.json` 的 `updated_at`

## 知识提炼流程

```bash
# 自动触发（每 3 个需求）或手动
bash "${CLAUDE_PLUGIN_ROOT}/skills/continuous-learning/scripts/knowledge-distill.sh"
```

提炼步骤：
1. 统计各 pattern 的 `frequency`
2. 识别相似度高的模式（超过 70% 重叠）
3. 合并相似模式，保留最佳实践
4. 高频模式标记为"核心"，低频模式标记"归档"
5. 更新 `pattern-index.json`
