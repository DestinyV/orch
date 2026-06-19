# 上下文继承协议（Context Inheritance Protocol）

## 概述

跨需求上下文复用的核心机制。每个新需求从 project-context + 历史相似需求的 req-context 继承基线，只探索增量，避免重复全量扫描。

## 协议流程

```
需求描述
  ↓ Step 0 (workflow)
1. 关键词提取 → keyword 权重列表
2. project-context 匹配 → 继承基线 section 列表
3. 历史需求匹配 → 继承相似需求的 req-context 文件
4. 生成 Inheritance Baseline → baseline-context.json
  ↓ Step 1 (spec / code-explorer)
5. 增量探索（只扫描 baseline 未覆盖的部分）
6. 产出 project-map.json（完整结构化项目地图）
  ↓ Step 3/5/6
7. 各阶段从 project-map 读取所需子图
8. 每阶段标记实际使用的 context 条目
  ↓ Step 7 (archive)
9. 知识沉淀：新发现 → context/ 文件合并
10. 更新 requirements.yaml + .exploration-state.json
```

---

## 1. 关键词提取

### 规则

从需求描述中提取技术关键词，按类型分类：

| 类型 | 提取来源 | 权重 |
|------|---------|------|
| **模块名** | `src/auth/`, `src/payment/`, `services/billing/` 等目录路径 | 1.0 |
| **API 名** | `/api/login`, `POST /checkout`, `GraphQL` | 1.0 |
| **数据实体** | `User`, `Order`, `Payment` 等大写名词 | 0.8 |
| **框架/库** | `React`, `Express`, `Prisma`, `Stripe` | 0.7 |
| **功能动词** | `登陆`、`支付`、`搜索`、`通知` | 0.5 |
| **非技术词** | `修改`、`优化`、`修复`（无领域指向） | 0.2 |

### 输出

```json
{
  "keyphrases": [
    {"text": "auth", "weight": 1.0, "type": "module"},
    {"text": "JWT", "weight": 1.0, "type": "api"},
    {"text": "User", "weight": 0.8, "type": "entity"},
    {"text": "login", "weight": 0.5, "type": "verb"}
  ],
  "inferred_files": ["src/auth/login.ts"],
  "inferred_modules": ["src/auth/"]
}
```

---

## 2. Project-Context 匹配

### 匹配算法

对 `orch-spec/context/index.json` 的每个 section，计算 keyword 与 tags 的交集覆盖率：

```
match_score = |keywords ∩ tags| / |tags|

match_score > 0.5  → INHERIT（全量继承该 section）
match_score 0.2-0.5 → TAG_ONLY（只继承该 section 的 tags，不继承内容）
match_score < 0.2 → SKIP（不继承）
```

### 输出

```json
{
  "inherited_sections": {
    "architecture": {"source": "project-context", "match_score": 0.8},
    "conventions": {"source": "project-context", "match_score": 0.6},
    "file-map": {"source": "project-context", "match_score": 0.3, "mode": "tag_only"}
  },
  "inherited_requirements": [
    {"req_id": "user-auth", "similarity": 0.72, "inherited_files": ["key-files.md", "decisions.md"]}
  ]
}
```

---

## 3. 历史需求匹配

### 相似度计算

读取 `orch-spec/context/requirements.yaml`，对新需求与每条历史需求计算 Jaccard 相似度：

```
similarity = |keywords_A ∩ keywords_B| / |keywords_A ∪ keywords_B|
```

| similarity | 继承策略 |
|-----------|---------|
| > 0.6 | 全量继承（req-context 全部文件 + decisions） |
| 0.3-0.6 | 部分继承（key-files.md + decisions.md） |
| < 0.3 | 不继承 |

---

## 4. Inheritance Baseline

### 格式

合并步骤 2+3 的结果，标记每个条目的来源和 stale 风险：

```json
{
  "baseline_id": "bsl-2026-06-19-001",
  "created_at": "2026-06-19T10:00:00Z",
  "sections": {
    "project-context/architecture": {
      "path": "orch-spec/context/architecture.md",
      "stale_risk": "stable",
      "last_refreshed": "2026-06-07",
      "match_score": 0.8
    },
    "req-user-auth/decisions": {
      "path": "orch-spec/user-auth/req-context/decisions.md",
      "stale_risk": "evolving",
      "last_refreshed": "2026-06-15",
      "similarity": 0.72
    }
  }
}
```

---

## 5. 增量探索协议

code-explorer 接收到 `baseline_context` 参数后的行为：

1. 读取 baseline_context.sections，加载所有已继承的 section
2. 对每个 section，检查其 `last_refreshed` SHA 是否与当前 HEAD 一致：
   - 一致 → section 内容视为最新，跳过扫描
   - 不一致 → 只扫描 `git diff` 中与该 section 相关的文件
3. 对 baseline 未覆盖的维度（absence in sections），执行全量扫描
4. 新发现追加到 req-context/，不覆盖 baseline 的已有内容

---

## 6. project-map.json 格式

Step 1 的最终产出（同时也是 P0.2 的核心数据结构）：

```json
{
  "_meta": {
    "created_by": "code-explorer",
    "requirement": "{req_id}",
    "mode": "full | incremental",
    "inherited_from": ["project-context", "req-user-auth"]
  },
  "modules": [
    {
      "path": "src/auth",
      "files": [
        {"path": "src/auth/login.ts", "exports": ["loginHandler", "validateCredentials"], "test": "tests/auth/login.test.ts"},
        {"path": "src/auth/jwt.ts", "exports": ["sign", "verify", "decode"], "test": "tests/auth/jwt.test.ts"}
      ],
      "dependencies": ["src/db", "src/config"],
      "api_routes": ["POST /api/login", "POST /api/refresh"]
    }
  ],
  "api_routes": [
    {"method": "POST", "path": "/api/login", "handler_module": "src/auth", "handler_file": "login.ts"},
    {"method": "GET", "path": "/api/users", "handler_module": "src/users"}
  ],
  "data_models": [
    {"name": "User", "fields": ["id", "email", "passwordHash", "createdAt"], "file": "src/models/user.ts"}
  ],
  "test_targets": [
    {"module": "src/auth", "test_files": ["tests/auth/login.test.ts", "tests/auth/jwt.test.ts"]}
  ]
}
```

### 子图提取规则（各阶段使用）

| 阶段 | 提取内容 |
|------|---------|
| Step 3 (design) | 全量 modules + dependencies + api_routes + data_models |
| Step 5 (execute) | 只保留当前 Task provides/consumes 相关的 modules 子集 |
| Step 6 (test) | 只保留 test_targets 中涉及变更模块的条目 |

---

## 7. 上下文使用率追踪

每阶段完成后，标记本阶段实际读取了 baseline 中的哪些 section。

```json
{
  "stage": "design_creation",
  "used_sections": ["project-context/architecture", "req-user-auth/decisions"],
  "unused_sections": ["project-context/code-patterns"],
  "accessed_files": ["src/auth/login.ts", "src/auth/jwt.ts"]
}
```

archive 步骤根据使用率决策：
- 连续 3 个需求都未使用某 section → 降权（`index.json` 中 `inheritance_weight` 降低 0.1）
- 从未使用的 section → 标记为 `archive_only`（只保留不参与继承匹配）

---

## 8. 约束

| ✅ 必须 | ❌ 禁止 |
|---------|--------|
| 继承基线必须标注来源 | 不标注来源直接覆盖 req-context |
| 每次 git diff 检测到文件变更时必须更新 section SHA | 继承 stale 内容超过 2 个需求周期 |
| 每阶段标记 context 使用率 | 未使用的 context section 持续参与继承匹配 |
| archive 步骤必须同步 requirements.yaml | 跳过 archive 导致下次继承丢失 |
