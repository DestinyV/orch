#!/usr/bin/env python3
"""T2.1 测试 — project-map 引用统一 (TC-S2-01/02)。

断言：
  - agents/+skills/ 递归 grep project-map.md = 0
  - code-architect.md / tasker.md / design/SKILL.md 均含 project-map.json
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


def main():
    print('=== T2.1 project-map 引用统一 ===')

    # TC-S2-01: 无 project-map.md 残留
    print('\n-- TC-S2-01: project-map.md 残留检查 --')
    hits = []
    for root, dirs, files in os.walk(os.path.join(PLUGIN_ROOT, 'agents')):
        for f in files:
            if f.endswith('.md'):
                src = open(os.path.join(root, f), encoding='utf-8').read()
                if 'project-map.md' in src:
                    hits.append(os.path.join(root, f))
    for root, dirs, files in os.walk(os.path.join(PLUGIN_ROOT, 'skills')):
        for f in files:
            if f.endswith('.md'):
                src = open(os.path.join(root, f), encoding='utf-8').read()
                if 'project-map.md' in src:
                    hits.append(os.path.join(root, f))
    check(len(hits) == 0, f'agents/+skills/ 无 project-map.md 残留（命中: {hits if hits else "无"}）')

    # TC-S2-02: 3 指定文件含 project-map.json
    print('\n-- TC-S2-02: 指定文件含 project-map.json --')
    files_to_check = [
        os.path.join(PLUGIN_ROOT, 'agents', 'code-architect.md'),
        os.path.join(PLUGIN_ROOT, 'agents', 'tasker.md'),
        os.path.join(PLUGIN_ROOT, 'skills', 'design', 'SKILL.md'),
    ]
    for f in files_to_check:
        src = open(f, encoding='utf-8').read()
        check('project-map.json' in src, f'{os.path.relpath(f, PLUGIN_ROOT)} 含 project-map.json')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
