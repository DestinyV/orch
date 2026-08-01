#!/usr/bin/env python3
"""T3.2-T3.5 综合测试 — cost GATE + using-orch 索引 + observer + TRIGGER。

断言 (TC-S3-04/05/06/07/08/09):
  - cost/SKILL.md 含 ≥1 <GATE>
  - using-orch 表格覆盖全部 22 个 skill；无遗漏
  - continuous-learning/config.json observer.enabled === true
  - 16 个核心 skill 的 description 含 TRIGGER when；全部 22 个 description 非空
"""
import json
import os
import re
import sys

PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

errors = 0
warnings = 0

# 22 个 skill（磁盘）
ALL_SKILLS = sorted(os.listdir(os.path.join(PLUGIN_ROOT, 'skills')))

# 16 个核心 skill（需 TRIGGER）
CORE_SKILLS = [
    'archive', 'clarify', 'continuous-learning', 'contract', 'debug',
    'design', 'exception', 'execute', 'req-change', 'scripts', 'spec',
    'spec-migrate', 'task', 'test', 'test-design', 'workflow',
]


def check(cond, msg):
    global errors, warnings
    if cond:
        print(f'  [OK]   {msg}')
    else:
        errors += 1
        print(f'  [FAIL] {msg}')


def main():
    print('=== T3.2-T3.5 skills 综合验证 ===')

    # TC-S3-04: cost GATE
    print('\n-- TC-S3-04: cost 含 GATE --')
    cost = open(os.path.join(PLUGIN_ROOT, 'skills', 'cost', 'SKILL.md'), encoding='utf-8').read()
    check(cost.count('<GATE>') >= 1, f'cost/SKILL.md 含 ≥1 <GATE>（实际 {cost.count("<GATE>")}）')

    # TC-S3-05/06: using-orch 索引覆盖 22
    print('\n-- TC-S3-05/06: using-orch 索引 --')
    uo = open(os.path.join(PLUGIN_ROOT, 'skills', 'using-orch', 'SKILL.md'), encoding='utf-8').read()
    table_skills = re.findall(r'\|\s*\*\*(\w[\w-]*)\*\*\s*\|', uo)
    missing = [s for s in ALL_SKILLS if s not in table_skills]
    check(len(table_skills) >= 22, f'using-orch 表格列出 {len(table_skills)} 个 skill（期望 ≥22）')
    check(len(missing) == 0, f'无 skill 目录从索引遗漏（遗漏: {missing if missing else "无"}）')

    # TC-S3-07: observer enabled
    print('\n-- TC-S3-07: observer 激活 --')
    cfg = json.load(open(os.path.join(PLUGIN_ROOT, 'skills', 'continuous-learning', 'config.json'), encoding='utf-8'))
    check(cfg['observer']['enabled'] is True, f'config.json observer.enabled === true（实际 {cfg["observer"]["enabled"]}）')

    # TC-S3-08: 核心 skill description 含 TRIGGER
    print('\n-- TC-S3-08: 核心 skill 含 TRIGGER when --')
    no_trigger = []
    for s in CORE_SKILLS:
        fp = os.path.join(PLUGIN_ROOT, 'skills', s, 'SKILL.md')
        if not os.path.exists(fp):
            no_trigger.append(f'{s}(缺失)')
            continue
        src = open(fp, encoding='utf-8').read()
        fm = src.split('---')[1] if src.startswith('---') else ''
        if 'TRIGGER when' not in fm:
            no_trigger.append(s)
    check(len(no_trigger) == 0, f'16 个核心 skill description 含 TRIGGER when（缺失: {no_trigger if no_trigger else "无"}）')

    # TC-S3-09: 全部 22 description 非空
    print('\n-- TC-S3-09: 全部 skill description 非空 --')
    empty_desc = []
    for s in ALL_SKILLS:
        fp = os.path.join(PLUGIN_ROOT, 'skills', s, 'SKILL.md')
        src = open(fp, encoding='utf-8').read()
        m = re.search(r'description:\s*\|?\s*(.*?)\n---', src, re.DOTALL)
        if not m or not m.group(1).strip():
            empty_desc.append(s)
    check(len(empty_desc) == 0, f'全部 {len(ALL_SKILLS)} 个 skill description 非空（空: {empty_desc if empty_desc else "无"}）')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
