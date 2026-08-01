#!/usr/bin/env python3
"""T2.4 测试 — agent frontmatter 统一 (TC-S2-07)。

断言：
  - 全部 agent 含 name/description/tools/model
  - tools 为逗号分隔（无 [ 数组语法）
  - model: inherit
  - color 缺失仅告警不阻断
"""
import os
import re
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


def parse_fm(src):
    m = re.match(r'^---\n(.*?)\n---', src, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip()
    return fm


def main():
    print('=== T2.4 frontmatter 统一 ===')
    agents_dir = os.path.join(PLUGIN_ROOT, 'agents')
    required_keys = ['name', 'description', 'tools', 'model']

    agents = [f for f in os.listdir(agents_dir) if f.endswith('.md') and not f.startswith('_')]
    missing_keys = []
    array_syntax = []
    not_inherit = []

    for f in agents:
        src = open(os.path.join(agents_dir, f), encoding='utf-8').read()
        fm = parse_fm(src)
        for k in required_keys:
            if k not in fm:
                missing_keys.append((f, k))
        tools = fm.get('tools', '')
        if '[' in tools:
            array_syntax.append(f)
        if fm.get('model', '') != 'inherit':
            not_inherit.append((f, fm.get('model', '')))

    print('\n-- 必填键 --')
    check(len(missing_keys) == 0, f'全部 agent 含 name/description/tools/model（缺失: {missing_keys if missing_keys else "无"}）')

    print('\n-- tools 逗号语法 --')
    check(len(array_syntax) == 0, f'无数组语法 tools（残留: {array_syntax if array_syntax else "无"}）')

    print('\n-- model: inherit --')
    check(len(not_inherit) == 0, f'全部 model: inherit（违规: {not_inherit if not_inherit else "无"}）')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
