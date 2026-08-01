#!/usr/bin/env python3
"""Sync Prompt Defense Baseline from _prompt-defense.md into all agent files."""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

defense_path = os.path.join(ROOT, 'agents', '_prompt-defense.md')
with open(defense_path, encoding='utf-8') as f:
    content = f.read()

m = re.search(r'```\s*\n(.*?)```', content, re.DOTALL)
if not m:
    print('ERROR: could not extract defense text from _prompt-defense.md')
    exit(1)
canonical = m.group(1).strip()

for fp in sorted(glob.glob(os.path.join(ROOT, 'agents', '*.md'))):
    fname = os.path.basename(fp)
    if fname == '_prompt-defense.md':
        continue
    with open(fp, encoding='utf-8') as f:
        orig = f.read()
    # 仅处理已含 Prompt Defense 节的文件（保持"部分 agent 同步"既有约定，不强制全量插入）
    if '## Prompt Defense Baseline' not in orig:
        print(f'SKIP {fname}: no section')
        continue
    # 幂等策略（ADR-007）：先全量清除所有已存在的 Prompt Defense 节（含孤儿头），再单次插入。
    # 原 re.sub count=1 只替换首个匹配，重复节清不净导致 F5 非幂等。
    # 段落切分方案：按 \n## 标题切分，丢弃所有 Prompt Defense 段落（无论重复多少次）。
    parts = re.split(r'(?m)^(?=## )', orig)
    kept = [p for p in parts if not re.match(r'##\s*Prompt Defense', p)]
    # 保护 frontmatter 后、Prompt Defense 前的横幅段（如 tdd-guide 的 > **DEPRECATED**）：
    # 若文件首个非 frontmatter 段以 ">" 开头且不含 Prompt Defense，则保留（不被后续清除误删）。
    # （注：横幅段属于 kept[1] 附近，本身不被过滤；此处仅保证不因插入逻辑丢失。）
    cleaned = ''.join(kept)
    # 清除孤儿标题行（无内容的 ## Prompt Defense Baseline 单行）
    cleaned = re.sub(
        r'^#{1,3}\s*Prompt Defense Baseline\s*$',
        '', cleaned, flags=re.MULTILINE
    )
    # 若清理后仍有节（正则异常兜底），跳过避免误写
    if '## Prompt Defense Baseline' in cleaned:
        print(f'WARN {fname}: residual section after cleanup, skipping')
        continue
    # 在 frontmatter 闭合 `---` 之后单点插入一次 canonical 节。
    # canonical 本身已含 "## Prompt Defense Baseline" 标题，此处不重复加标题。
    m_fm = re.search(r'^---\n.*?\n---\n', cleaned, re.DOTALL)
    block = canonical + '\n\n'
    if m_fm:
        insert_at = m_fm.end()
        new_text = cleaned[:insert_at] + block + cleaned[insert_at:]
    else:
        new_text = block + cleaned
    if new_text == orig:
        print(f'SAME {fname}')
        continue
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print(f'OK   {fname}')

print('\nDone')
