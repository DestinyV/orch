#!/usr/bin/env python3
"""T2.3 测试 — Prompt Defense 幂等 (TC-S2-05/06)。

断言：
  - sync-prompt-defense.py 连跑两次，节数不增加（幂等）
  - 每个 agent 的 "## Prompt Defense Baseline" 节 ≤1
"""
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


def count_sections(agent_dir):
    """统计每个 agent 的 Prompt Defense 节数。"""
    counts = {}
    for f in os.listdir(agent_dir):
        if not f.endswith('.md') or f.startswith('_'):
            continue
        src = open(os.path.join(agent_dir, f), encoding='utf-8').read()
        counts[f] = src.count('## Prompt Defense Baseline')
    return counts


def main():
    print('=== T2.3 Prompt Defense 幂等 ===')
    agents_dir = os.path.join(PLUGIN_ROOT, 'agents')

    # TC-S2-06: 每 agent ≤1
    print('\n-- TC-S2-06: 每 agent ≤1 --')
    counts = count_sections(agents_dir)
    violators = {k: v for k, v in counts.items() if v > 1}
    check(len(violators) == 0, f'全部 agent Prompt Defense 节 ≤1（违规: {violators if violators else "无"}）')

    # TC-S2-05: 幂等（连跑两次，节数不增加）
    print('\n-- TC-S2-05: 幂等性 --')
    script = os.path.join(PLUGIN_ROOT, 'scripts', 'sync-prompt-defense.py')
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'utf-8'
    # 第一次运行（在当前已修复态，应为无变更或无新增）
    subprocess.run(['python', script], capture_output=True, env=env, cwd=PLUGIN_ROOT)
    after_first = count_sections(agents_dir)
    # 第二次运行
    subprocess.run(['python', script], capture_output=True, env=env, cwd=PLUGIN_ROOT)
    after_second = count_sections(agents_dir)
    increased = {k: (after_first[k], after_second[k]) for k in after_first if after_second[k] > after_first[k]}
    check(len(increased) == 0, f'连跑两次节数不增加（增加: {increased if increased else "无"}）')
    # 且全 ≤1
    all_ok = all(v <= 1 for v in after_second.values())
    check(all_ok, '第二次运行后全部 ≤1')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
