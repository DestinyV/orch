#!/usr/bin/env python3
"""T2.5 测试 — code-architect 编号 + /hookify 清理 (TC-S2-08/09)。

断言：
  - code-architect.md 的 `### 0.` 仅一次；标题编号升序连续无重复
  - agents/ 内 grep /hookify = 0
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
    print('=== T2.5 code-architect 编号 + /hookify ===')

    # TC-S2-08: 编号连续
    print('\n-- TC-S2-08: code-architect 编号连续 --')
    ca = open(os.path.join(PLUGIN_ROOT, 'agents', 'code-architect.md'), encoding='utf-8').read()
    nums = [int(m) for m in re.findall(r'^### (\d+)\.', ca, re.MULTILINE)]
    check(nums.count(0) == 1, f'`### 0.` 仅出现一次（实际 {nums.count(0)}）')
    # 编号升序连续（允许从 0 开始，无重复无跳号）
    expected = list(range(len(nums)))
    check(nums == expected, f'编号升序连续（实际 {nums}，期望 {expected}）')

    # TC-S2-09: 无 /hookify
    print('\n-- TC-S2-09: 无 /hookify 引用 --')
    hits = []
    for f in os.listdir(os.path.join(PLUGIN_ROOT, 'agents')):
        if f.endswith('.md') and not f.startswith('_'):
            src = open(os.path.join(PLUGIN_ROOT, 'agents', f), encoding='utf-8').read()
            if 'hookify' in src:
                hits.append(f)
    check(len(hits) == 0, f'agents/ 无 /hookify 引用（命中: {hits if hits else "无"}）')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
