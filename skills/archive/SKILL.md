---
name: archive
description: |
  规范归档和优化（Archive阶段）

  输入：orch-spec/{requirement_desc_abstract}/spec/ + orch-spec/spec/（主规范目录）
  输出：orch-spec/spec/（已合并的主规范）

  功能：在测试通过后，将需求的规范文档合并集成到主规范中，建立企业级规范库。
---

# archive

## 职责

将测试通过的需求规范合并到企业级主规范库中。

**核心流程**：分析 → 对标 → 合并去重 → 一致性检查 → 归档报告。
**输出路径**：`orch-spec/spec/`（主规范目录）

## 何时使用

全部测试通过后执行归档。

## 工作流程

### 分析

读取新需求 spec（场景清单、数据模型、业务规则、术语）和主规范（若存在）。文件读取和比对使用 `Skill("orch:scripts")` 工具优先策略——Grep 定位场景文件、Python3 批量提取 TEST-VERIFY 和术语列表，减少 Read 调用。

### 步骤1.5: 归档前验证 — spec vs code 一致性

<GATE>归档前必须验证规范与最终实现的一致性。不一致时 spec 必须更新为匹配实现（spec 是实现的文档，实现是最终事实来源）。</GATE>

```bash
Agent(subagent_type="orch:code-explorer",
      prompt="扫描 orch-spec/{req}/src/ 提取实际实现的接口路由/数据模型/组件结构:
              1) API 路由和响应格式 vs contract.md
              2) 数据模型字段 vs data-models.md
              3) 组件目录结构 vs design.md 组件树
              输出差异报告到 orch-spec/{req}/testing/spec-code-diff.md")
```

**不匹配处理**：
| 类型 | 操作 |
|------|------|
| 实现有但 spec 无 | 追加到 spec（实现是最终事实来源） |
| spec 有但实现无 | 标记为 `FINAL_SPEC_DRIFT`，从 spec 移除或标注未实现 |
| 字段/接口结构不一致 | 更新 spec 匹配实现 |

### 步骤2-4: 派遣 archiver Agent 执行合并

<GATE>必须通过 Agent 派遣 archiver，不允许主上下文直接执行对标和合并。</GATE>

```bash
Agent(
  subagent_type="orch:archiver",
  prompt="
    对新需求规范进行归档合并：
    - 新需求 spec: orch-spec/{requirement_desc_abstract}/spec/
    - 主规范: orch-spec/spec/（若不存在则创建）
    
    执行以下任务：
    1. 场景对标：逐场景比对，分类为完全新增/部分重叠/完全覆盖/冲突
    2. 合并：场景/数据模型/业务规则/术语各维度统一（相同→去重 | 新增→添加 | 冲突→标记 DECISION_NEEDED）
    3. 一致性检查：输出各维度统计（已有/新增/冲突数）
    
    返回：对标矩阵、合并结果、冲突清单、一致性检查统计
  ",
  run_in_background=false
)
```

**容错**：Agent 失败则回退主 agent，但必须标注 ⚠️ 未完成自动化归档。

### 归档可视化（按需）

存在 DECISION_NEEDED 冲突时生成合并冲突关系图（冲突类型+严重度+影响范围）；主规范存在且本次有新增时生成规范演进时间线。

模板见 `templates/diagrams/`，输出到 `orch-spec/spec/diagrams/`。触发规则见 `../design/references/diagram-trigger-rules.md`。

### 生成归档报告

基于 archiver 返回结果，输出到 `orch-spec/spec/archive-log.md`，包含归档内容、合并结果、一致性检查、规范库当前状态。详见 `references/workflow-detail.md`（归档报告模板 + 合并示例）。

### 步骤6: 同步上下文注册中心（程序化执行）

归档完成后将本需求知识同步到 `orch-spec/context/`，供后续需求复用。

<GATE>归档完成时必须同步更新 orch-spec/context/。context/ 不存在时先创建目录并初始化 index.json。</GATE>

**执行顺序**（每一步使用脚本而非手工 LLM 编辑）：

```bash
# 步骤6.1: 提取 API 路由并追加到 api-calls.yaml
python3 -c "
import json, os, re
req = '{requirement_desc_abstract}'
design_path = f'orch-spec/{req}/design/design.md'
api_path = 'orch-spec/context/logic-chains/api-calls.yaml'
if os.path.exists(design_path):
    with open(design_path) as f: content = f.read()
    routes = re.findall(r'(GET|POST|PUT|DELETE|PATCH)\s+(/\S+)', content)
    if routes:
        existing = []
        if os.path.exists(api_path):
            with open(api_path) as f: existing = yaml.safe_load(f).get('chains', [])
        for method, path in routes:
            existing.append({'method': method, 'path': path, 'source_req': req})
        with open(api_path, 'w') as f: yaml.dump({'chains': existing}, f)
        print(f'[archive] Synced {len(routes)} API routes to api-calls.yaml')
"
```

```bash
# 步骤6.2: 提取 provides/consumes 并追加到 component-deps.yaml
python3 -c "
import yaml, os, re
req = '{requirement_desc_abstract}'
tasks_path = f'orch-spec/{req}/tasks/tasks.md'
deps_path = 'orch-spec/context/logic-chains/component-deps.yaml'
if os.path.exists(tasks_path):
    with open(tasks_path) as f: content = f.read()
    deps = re.findall(r'consumes:\s*(\S+)', content)
    if deps:
        existing = []
        if os.path.exists(deps_path):
            with open(deps_path) as f: existing = yaml.safe_load(f).get('dependencies', [])
        for dep in deps:
            existing.append({'provides': 'unknown', 'consumes': dep, 'source_req': req})
        with open(deps_path, 'w') as f: yaml.dump({'dependencies': existing}, f)
        print(f'[archive] Synced {len(deps)} dependencies to component-deps.yaml')
"
```

```bash
# 步骤6.3: 更新 requirements.yaml（需求相似度索引）
python3 -c "
import yaml, os
req = '{requirement_desc_abstract}'
reqs_path = 'orch-spec/context/requirements.yaml'
# 从 req-context/key-files.md 提取涉及的文件和模块
keyfiles_path = f'orch-spec/{req}/req-context/key-files.md'
files = []
if os.path.exists(keyfiles_path):
    with open(keyfiles_path) as f:
        for line in f:
            if line.startswith('- ') and '/' in line:
                files.append(line.strip('- ').strip())
existing = []
if os.path.exists(reqs_path):
    with open(reqs_path) as f: existing = yaml.safe_load(f).get('requirements', [])
existing.append({
    'id': req,
    'files_touched': files,
    'completed_at': '__DATE__'
})
with open(reqs_path, 'w') as f: yaml.dump({'requirements': existing}, f)
print(f'[archive] Updated requirements.yaml with {req}')
"
```

```bash
# 步骤6.4: 更新 .exploration-state.json
python3 -c "
import json, os, subprocess
state_path = 'orch-spec/context/.exploration-state.json'
# 获取当前 HEAD SHA
sha = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
state = json.load(open(state_path)) if os.path.exists(state_path) else {}
state['last_explored_sha'] = sha
section = '{requirement_desc_abstract}'
# 标记本需求涉及的 section 为 dirty=false（刚刷新）
for s in state.get('section_freshness', {}):
    state['section_freshness'][s]['sha'] = sha
    state['section_freshness'][s]['last_refreshed'] = '__DATE__'
state['inheritance_stats']['total_requirements'] = state['inheritance_stats'].get('total_requirements', 0) + 1
json.dump(state, open(state_path, 'w'), indent=2)
print(f'[archive] Updated exploration state (SHA: {sha[:8]})')
"
```

**验证**：同步后确认以下文件非空：
- `context/logic-chains/api-calls.yaml` — 有 `chains[]`（或为空数组且注明"无API变更"）
- `context/logic-chains/component-deps.yaml` — 有 `dependencies[]`
- `context/requirements.yaml` — 追加了本需求条目
- `.exploration-state.json` — `last_explored_sha` 更新

### 可选清理

用户多层确认后，备份并删除原需求目录。

## 归档合并协议

<GATE>归档不是只写 log，必须实际合并 spec 文件到主规范库。log 仅用于审计，不能替代合并。</GATE>

1. **场景合并** — 复制 `scenarios/*.md` 到主规范 `orch-spec/spec/scenarios/`。场景ID冲突时追加新Case到末尾（不覆盖），完全重复则跳过。
2. **数据模型合并** — 新增实体/字段追加到 `orch-spec/spec/data-models.md`。
3. **业务规则合并** — 新增规则追加到 `orch-spec/spec/business-rules.md`。规则冲突标注 `DECISION_NEEDED`。
4. **术语合并** — 新术语追加到 `orch-spec/spec/glossary.md`。重复跳过。
5. **标记已归档** — 在原需求 `requirement.md` 追加 `archived: true`。

## Output

- `orch-spec/spec/` — 已合并的主规范库（场景/模型/规则/术语）
- `orch-spec/spec/archive-log.md` — 归档日志（审计用）

## 关键约束

<GATE>任何冲突不得静默跳过，必须标记为 DECISION_NEEDED 等待人工确认</GATE>
<GATE>禁止只输出 archive-log.md 而不实际执行文件合并</GATE>

✅ 必须：对标比较找重复/新增 | 处理所有冲突 | 一致性检查通过 | 生成归档报告
❌ 禁止：随意删除已有规范 | 跳过重复检查 | 忽视冲突直接覆盖 | 不备份直接修改
