---
name: scripts
description: |
  工具优先策略——文件操作优先使用脚本完成，根据场景复杂度选择语言：
  简单查询→Grep/Bash，批量处理/大规模检索/有逻辑判断→Python脚本。
  仅当脚本无法处理时兜底使用大模型直接读取。减少Token消耗，提升效率。

  触发条件：任何Skill需要进行文件搜索、批量处理、内容提取、格式校验时
---

# scripts

## When to Use

- 需要进行文件搜索、批量处理、内容提取、格式校验时
- 优先用脚本批量处理而非逐个 Read 文件
- 简单查询用 Grep/Bash，复杂逻辑用 Python3

## Output

脚本输出结果（不加载整个文件到上下文）。

## 职责

为其他 Skill 提供脚本化的文件操作能力。核心原则：**能用脚本批量处理的不逐个 Read，能一次输出结果的不将文件内容加载到上下文。**

## 语言选择策略

```
操作复杂度
    │
    ├── 简单查询/单步操作 → Grep / Bash one-liner
    ├── 遍历+简单过滤 → Bash for+if
    ├── 遍历+复杂逻辑/多条件判断 → Python3 -c 内联脚本
    ├── 大规模检索+数据结构操作 → Python3 脚本（set/dict/正则）
    ├── 批量处理+文件读写+格式转换 → Python3 脚本（os/glob/json/re）
    └── 以上无法满足 → 兜底专用工具（Read/Write/Edit）
```

## 场景 → 语言映射

### 简单查询（Bash/Grep）

| 场景 | 示例 |
|------|------|
| 关键字搜索+文件列表 | `Grep(pattern, output_mode="files_with_matches")` |
| 搜索+显示匹配行+行号 | `Grep(pattern, output_mode="content", -n=true)` |
| 跨文件计数 | `Grep(pattern, output_mode="count")` |
| 多行模式搜索 | `Grep(pattern, multiline=true)` |
| 文件头/尾提取 | `Bash("head -N file")` / `Bash("tail -N file")` |
| 简单行范围提取 | `Bash("sed -n '10,20p' file")` |
| 文件查找 | `Glob(pattern)` |

### 批量处理 / 大规模检索（Python3 内联脚本）

当操作涉及**遍历+条件判断+数据聚合**时，编写 Python3 内联脚本：

**典型场景**：

```bash
# 遍历目录+读取文件+逻辑判断+格式化输出
python3 -c "
import os
base = 'path/to/dir'
for f in sorted(os.listdir(base)):
    if not f.endswith('.md'): continue
    with open(os.path.join(base, f), encoding='utf-8') as fh:
        content = fh.read()
    # 自定义逻辑
    has_target = 'keyword' in content
    print(f'{'[X]' if has_target else '[ ]'} {f}')
"

# 跨文件交叉引用检查
python3 -c "
import os, re
refs_dir = 'path/to/references'
skill_md = 'path/to/SKILL.md'
with open(skill_md, encoding='utf-8') as f: skill_content = f.read()
for fn in os.listdir(refs_dir):
    if fn not in skill_content:
        print(f'MISS: {fn}')
"

# JSON 批量处理
python3 -c "
import os, json
for fn in os.listdir('dir'):
    if fn.endswith('.json'):
        with open(os.path.join('dir', fn), encoding='utf-8') as f:
            data = json.load(f)
        # 处理逻辑
        print(f'{fn}: {len(data.get(\"items\", []))} items')
"

# 统计+排序+Top N
python3 -c "
import os
counts = {}
for fn in os.listdir('dir'):
    counts[fn] = os.path.getsize(os.path.join('dir', fn))
for k, v in sorted(counts.items(), key=lambda x: -x[1])[:10]:
    print(f'{k}: {v} bytes')
"
```

### 精确编辑（Edit 工具）

| 场景 | 方法 |
|------|------|
| 精确替换唯一字符串 | `Edit(old_string, new_string)` |
| 全局替换（所有出现） | `Edit(old_string, new_string, replace_all=true)` |
| 多文件同模式替换 | Python3 脚本读取→str.replace→写回 |

### 格式校验（Bash 单行）

| 场景 | 示例 |
|------|------|
| JSON 语法校验 | `Bash("python3 -c 'import json; json.load(open(\"f\"))'")` |
| JSON 字段检查 | `Bash("python3 -c 'import json; d=json.load(open(\"f\")); print(d[\"key\"])'")` |
| 文件编码检测 | `Bash("file -bi filename")` |

## 决策流程

1. 收到文件操作需求
2. 评估复杂度：
   - 单步查询/搜索 → Grep / Bash one-liner
   - 遍历+条件+聚合 → Python3 内联脚本
   - 精确字符替换 → Edit 工具
3. 脚本输出结果（不加载整个文件到上下文）
4. 脚本无法满足（逻辑过于复杂 / 需要语义理解）→ 兜底 Read/Write/Edit

## 环境检测与备选切换

脚本编写前先探测可用工具，按优先级选择，不可用时自动降级。

### 探测方法

```bash
# 探测可用命令（退出码 0=可用）
which python3 2>/dev/null || which python 2>/dev/null
which jq 2>/dev/null
which bash 2>/dev/null || which sh 2>/dev/null
```

探测结果确定后续脚本使用 `python3` 还是 `python`，`bash` 还是 `sh`。

### Python 备选链

```
python3 -c "..." → python -c "..." → 兜底 Read/Write
```

| 环境 | 可用命令 | 策略 |
|------|---------|------|
| Linux/macOS 标准 | `python3` | 首选 `python3 -c` |
| Windows（Python 3.x） | `python` 或 `python3` | 探测后选择可用者 |
| Windows（无 Python） | 无 | 降级 Bash / 兜底 Read |
| 容器/精简环境 | `python3` 或 `python` | 探测后选择，均无则 Bash |

### Shell 备选链

```
Bash(bash 语法) → Bash(sh 语法) → 拆分为多个简单命令 → 兜底 Read
```

| 环境 | 可用命令 | 策略 |
|------|---------|------|
| Linux/macOS | `bash` | 完整 bash 语法（`[[`、`for ((`、数组） |
| Windows Git Bash | `bash` | 可用但部分命令（sed/awk）可能缺失 |
| Alpine/精简容器 | `sh`（ash） | 降级 POSIX sh 语法（`[`、`for f in`、无数组） |
| Windows CMD | 无 bash | 仅 Python3 内联脚本 |

### jq 备选链

```
jq '.key' → python3 -c "json.load" → 兜底 Read
```

| 环境 | 策略 |
|------|------|
| jq 可用 | 首选 `jq`（简洁高效） |
| 有 Python 无 jq | Python3 `json.load()` + 字典操作替代 |
| 均无 | Read 后模型解析 |

### 平台适配速查

| 差异点 | Linux/macOS | Windows |
|--------|------------|---------|
| Python 路径 | `/usr/bin/python3` | `C:\Python3*\python.exe` 或 `python` |
| 路径分隔符 | `/` | Python 内用 `/` 或 `\\`，Bash 内用 `/` |
| sed 行内编辑 | `sed -i 's/...' file` | `sed -i 's/...' file`（Git Bash 支持） |
| 文件编码 | UTF-8（默认） | 可能为 GBK，Python 显式 `encoding='utf-8'` |
| /dev/null | ✅ | Git Bash 支持，CMD 用 `NUL` |

### 容错策略

1. **探测前置**：首个脚本操作前 `which` 探测一次，结果复用
2. **静默降级**：首选不可用时自动切换备选，不中断流程
3. **降级通知**：切换备选时在输出标注 `[info] using python (python3 not found)`
4. **终极兜底**：所有脚本方案不可用 → Read/Write/Edit 兜底（需注释原因）

## 关键约束

- **Grep 优先于 Bash grep**：文件搜索场景始终用 Grep 工具，不用 `Bash(grep/rg)`
- **Python3 优先于 Bash 循环**：涉及条件判断、数据聚合、多文件关联时，用 Python3 而非复杂 Bash 脚本
- **Edit 优先于 Read+Write**：精确编辑优先用 Edit 工具，避免读取全文
- **先探测再执行**：首个文件操作前探测 `python3/python/bash/sh/jq` 可用性，确定备选链
- **兜底有据**：所有脚本方案不可用时使用 Read 兜底，需在注释中说明降级路径

## 编写规范

- Python 内联脚本优先用双引号包裹（避免内部单引号转义问题）
- 路径使用正斜杠 `/`（Python 在 Windows 下也支持）
- 编码显式指定 `encoding='utf-8'`
- 输出简洁：每行一个结果，便于后续处理
- 容错：关键操作加 try/except，避免脚本因单个文件失败而整体崩溃

## 内置脚本

以下 6 个脚本已内置于 `${CLAUDE_PLUGIN_ROOT}/skills/scripts/scripts/` 目录，各 Skill 可直接调用，无需重新生成。

| 脚本 | 用途 | 调用 Skill |
|------|------|-----------|
| `${CLAUDE_PLUGIN_ROOT}/skills/scripts/scripts/extract-test-verify.py` | scenarios → TEST-VERIFY + Mock Data JSON | test-design |
| `${CLAUDE_PLUGIN_ROOT}/skills/scripts/scripts/validate-outputs.sh` | 批量验证产出文件非空 + 空目录清理 | workflow |
| `${CLAUDE_PLUGIN_ROOT}/skills/scripts/scripts/scan-exceptions.py` | 扫描异常类/错误码/RPC 模式 | exception |
| `${CLAUDE_PLUGIN_ROOT}/skills/scripts/scripts/extract-api-list.py` | design.md → 接口清单 JSON | contract |
| `${CLAUDE_PLUGIN_ROOT}/skills/scripts/scripts/extract-project-context.py` | 提取技术栈/分层/命名约定 | design, workflow |
| `${CLAUDE_PLUGIN_ROOT}/skills/scripts/scripts/extract-eval-metrics.py` | .workflow-eval.json → 指标摘要 | workflow |

**调用方式**：
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/scripts/scripts/extract-test-verify.py" orch-spec/{req}/spec/scenarios/
bash "${CLAUDE_PLUGIN_ROOT}/skills/scripts/scripts/validate-outputs.sh" file1 file2 --dir dir1 dir2
python3 "${CLAUDE_PLUGIN_ROOT}/skills/scripts/scripts/scan-exceptions.py" src/
```

## 使用方式

其他 Skill 在需要文件操作时调用本 Skill：

```bash
Skill("orch:scripts", args="cross-check:检查 references/ 下所有 .md 文件是否在 SKILL.md 中被引用")
Skill("orch:scripts", args="batch-extract:提取所有 spec-*/spec/requirement.md 中的 project-mode 字段")
Skill("orch:scripts", args="validate:批量校验 spec-*/spec/ 下所有 .json 文件")
```

## 参考文档速查

| 参考文档 | 使用场景 |
|---------|---------|
| `references/script-templates.md` | Python/Bash 脚本模板速查（遍历/过滤/聚合/交叉比对/格式化输出） |

<GATE>禁止 Bash(grep/rg) 替代 Grep 工具 | 禁止复杂 Bash 循环替代 Python3 脚本</GATE>