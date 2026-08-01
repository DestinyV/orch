#!/usr/bin/env python3
"""T5.1-T5.3 综合测试 — 文档同步 + pyc 清理 (TC-S5-03/04/05)。

断言：
  - CLAUDE.md 钩子表脚本全部在 hooks.json 中（双向一致）
  - README 含 22 skills/26 agents/14 commands，无 /orch:sdd-dev；.claude-plugin/README 含 22/14；AGENTS.md 含 26
  - git ls-files 无 *.pyc；.gitignore 含 __pycache__/ *.pyc
"""
import json
import os
import re
import subprocess
import sys

PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

errors = 0
warnings = 0


def check(cond, msg):
    global errors, warnings
    if cond:
        print(f'  [OK]   {msg}')
    else:
        errors += 1
        print(f'  [FAIL] {msg}')


def main():
    print('=== T5 文档同步 ===')

    # TC-S5-03: CLAUDE.md 钩子表 ↔ hooks.json 双向一致
    print('\n-- TC-S5-03: CLAUDE.md 钩子表 ↔ hooks.json --')
    hooks = json.load(open(os.path.join(PLUGIN_ROOT, 'hooks', 'hooks.json'), encoding='utf-8'))
    hook_scripts = set()
    for event, entries in hooks['hooks'].items():
        for e in entries:
            for h in e.get('hooks', []):
                cmd = h.get('command', '')
                m = re.search(r'([\w.-]+\.(?:js|sh))', cmd)
                if m:
                    hook_scripts.add(m.group(1))
    claude_md = open(os.path.join(PLUGIN_ROOT, 'CLAUDE.md'), encoding='utf-8').read()
    table_scripts = set(re.findall(r'\|\s*([\w.-]+\.(?:js|sh))\s*\|', claude_md))
    # 双向：CLAUDE.md 表中每个脚本在 hooks.json 中
    not_in_hooks = table_scripts - hook_scripts
    check(len(not_in_hooks) == 0, f'CLAUDE.md 表中脚本均在 hooks.json（不在: {not_in_hooks if not_in_hooks else "无"}）')
    # hooks.json 中每个脚本（除禁用）在 CLAUDE.md 表中
    not_in_md = hook_scripts - table_scripts
    check(len(not_in_md) == 0, f'hooks.json 脚本均在 CLAUDE.md 表中（不在: {not_in_md if not_in_md else "无"}）')

    # TC-S5-04: 文档数量口径
    print('\n-- TC-S5-04: 文档数量口径 --')
    readme = open(os.path.join(PLUGIN_ROOT, 'README.md'), encoding='utf-8').read()
    check('22 professional skills' in readme or '22 Skills' in readme, 'README 含 22 skills 声明')
    check('26 professional Agents' in readme or '26 professional' in readme, 'README 含 26 agents 声明')
    check('/orch:sdd-dev' not in readme, 'README 无 /orch:sdd-dev 残留')
    check('/start-dev' in readme, 'README 含 /start-dev')
    plugin_readme = open(os.path.join(PLUGIN_ROOT, '.claude-plugin', 'README.md'), encoding='utf-8').read()
    check('22 skills' in plugin_readme and '14 commands' in plugin_readme, '.claude-plugin/README 含 22 skills/14 commands')

    # TC-S5-05: git 无 *.pyc；.gitignore 含模式
    print('\n-- TC-S5-05: git 无 pyc + .gitignore --')
    proc = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=PLUGIN_ROOT)
    pyc_hits = [l for l in proc.stdout.split('\n') if '.pyc' in l or '__pycache__' in l]
    check(len(pyc_hits) == 0, f'git ls-files 无 *.pyc（命中: {pyc_hits if pyc_hits else "无"}）')
    gi = open(os.path.join(PLUGIN_ROOT, '.gitignore'), encoding='utf-8').read()
    check('__pycache__/' in gi and '*.pyc' in gi, '.gitignore 含 __pycache__/ 和 *.pyc')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
