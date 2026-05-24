# 脚本模板速查

## Python3 内联模板

### 遍历+过滤+输出

```bash
python3 -c "
import os
for f in sorted(os.listdir('path')):
    if not f.endswith('.md'): continue
    # 逻辑
    print(f)
"
```

### 读取文件+条件判断

```bash
python3 -c "
import os
base = 'path'
for f in sorted(os.listdir(base)):
    fp = os.path.join(base, f)
    with open(fp, encoding='utf-8') as fh:
        content = fh.read()
    if 'keyword' in content:
        print(f)
"
```

### 交叉引用检查

```bash
python3 -c "
import os
with open('target.md', encoding='utf-8') as f:
    target = f.read()
for fn in sorted(os.listdir('refs/')):
    if fn not in target:
        print(f'MISS: refs/{fn}')
"
```

### JSON 批量读取

```bash
python3 -c "
import os, json
for fn in os.listdir('dir'):
    if not fn.endswith('.json'): continue
    with open(os.path.join('dir', fn), encoding='utf-8') as f:
        d = json.load(f)
    print(f'{fn}: {d.get(\"key\", \"N/A\")}')
"
```

### 统计+排序+Top N

```bash
python3 -c "
import os
sizes = {f: os.path.getsize(os.path.join('dir', f)) for f in os.listdir('dir') if os.path.isfile(os.path.join('dir', f))}
top = sorted(sizes.items(), key=lambda x: -x[1])[:10]
for f, s in top: print(f'{f}: {s} bytes')
"
```

### 批量字符串替换（跨文件）

```bash
python3 -c "
import os
d = 'dir'
for fn in os.listdir(d):
    if not fn.endswith('.md'): continue
    fp = os.path.join(d, fn)
    with open(fp, encoding='utf-8') as f: c = f.read()
    c = c.replace('old', 'new')
    with open(fp, 'w', encoding='utf-8') as f: f.write(c)
    print(f'Updated: {fn}')
"
```

## 环境探测

```bash
# 探测可用命令（脚本编写前执行一次，结果复用）
which python3 2>/dev/null && echo "PY=python3" || (which python 2>/dev/null && echo "PY=python" || echo "PY=none")
which jq 2>/dev/null && echo "JQ=yes" || echo "JQ=no"
which bash 2>/dev/null && echo "SH=bash" || (which sh 2>/dev/null && echo "SH=sh" || echo "SH=none")
```

## Python3 备选写法

```bash
# 自动适配 python3 或 python（探测后选择）
$(which python3 2>/dev/null || which python 2>/dev/null) -c "
import os
print('hello')
"
```

## jq 备选写法

```bash
# 方案1: jq（优先）
jq '.key' file.json 2>/dev/null || \

# 方案2: Python3 降级
$(which python3 || which python) -c "
import json
d = json.load(open('file.json'))
print(d['key'])
"
```

## Bash 简单操作

```bash
# 提取行范围
head -30 file.md | tail -20

# 提取两个标记间内容
sed -n '/## START/,/## END/p' file.md

# 统计行数/字数
wc -l file.md

# 查找空文件
find . -empty -name "*.md"

# 校验 JSON
python3 -c "import json; json.load(open('file.json'))"

# 文件编码
file -bi file.md
```
