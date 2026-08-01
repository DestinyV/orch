#!/usr/bin/env python3
"""T1.4 测试 — 北极星原则 GATE 审查 (TC-S1-07)。

断言：skills/workflow/SKILL.md + stage-gate.js 的每条 GATE 仅约束
「流程顺序/阶段产出存在/派遣完整性」，无能力限制型措辞（限制思考深度/探索方式/创造性）。
"""
import os
import re
import sys

PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

errors = 0
warnings = 0

# cage 类关键词（限制思考/探索/创造）
CAGE_PATTERNS = [
    r'禁止\s*(探索|思考|分析|阅读)',
    r'必须\s*(采用|使用)\s*[^。，]{0,10}(方式|方法|模板)',
    r'不(允许|得)\s*(探索|发挥|创造)',
    r'禁止\s*(读取|查看).{0,8}(原文|文件|源码)',
    r'只能\s*(按|根据|使用)\s*(注入|给定|预设)',
]


def check(cond, msg):
    global errors, warnings
    if cond:
        print(f'  [OK]   {msg}')
    else:
        errors += 1
        print(f'  [FAIL] {msg}')


def main():
    print('=== T1.4 北极星 GATE 审查 (TC-S1-07) ===')

    targets = [
        os.path.join(PLUGIN_ROOT, 'skills', 'workflow', 'SKILL.md'),
        os.path.join(PLUGIN_ROOT, 'scripts', 'hooks', 'stage-gate.js'),
    ]

    for target in targets:
        if not os.path.exists(target):
            check(False, f'文件存在: {os.path.relpath(target, PLUGIN_ROOT)}')
            continue
        src = open(target, encoding='utf-8').read()
        # 提取 GATE 文本
        gates = re.findall(r'<GATE>(.*?)</GATE>', src, re.DOTALL)
        # 提取 HARD-GATE 文本
        gates += re.findall(r'<HARD-GATE>(.*?)</HARD-GATE>', src, re.DOTALL)
        print(f'\n-- {os.path.relpath(target, PLUGIN_ROOT)}: {len(gates)} 条 GATE --')
        if not gates:
            check(True, '无 GATE（无需审查）')
            continue
        violations = []
        for g in gates:
            for pat in CAGE_PATTERNS:
                if re.search(pat, g):
                    violations.append((pat, g[:60]))
        if violations:
            for pat, g in violations:
                check(False, f'能力限制型措辞 "{pat}": {g}...')
        else:
            check(True, f'{len(gates)} 条 GATE 全部为流程/产出/派遣约束（guardrail）')

    # 检查 start-dev.md 的探索禁令是否已降级
    print('\n-- start-dev.md 探索禁令降级 --')
    sd = open(os.path.join(PLUGIN_ROOT, 'commands', 'start-dev.md'), encoding='utf-8').read()
    still_gate = re.search(r'<GATE>[^<]*(禁止[^<]*探索|禁止[^<]*文件读取|禁止[^<]*目录扫描)[^<]*</GATE>', sd)
    check(still_gate is None, 'start-dev.md 无「禁止探索/文件读取/目录扫描」GATE（已降级为建议）')

    # 检查 tasker.md 的 Read 限制是否已降级
    print('\n-- tasker.md Read 限制降级 --')
    tk = open(os.path.join(PLUGIN_ROOT, 'agents', 'tasker.md'), encoding='utf-8').read()
    still_limited = re.search(r'<GATE>[^<]*(仅当|只允许)[^<]*(Read 原文|读取原文)[^<]*</GATE>', tk)
    check(still_limited is None, 'tasker.md 无「仅当…才 Read 原文」GATE（已降级为建议）')

    # business-rules 审查结论落盘
    print('\n-- business-rules.md 北极星审查结论 --')
    br = open(os.path.join(PLUGIN_ROOT, 'orch-spec', 'plugin-capability-optimization', 'spec', 'business-rules.md'), encoding='utf-8').read()
    check('北极星原则审查结论' in br, 'business-rules.md 含「北极星原则审查结论」章节')
    for cid in ['NSP-001', 'NSP-002', 'NSP-003', 'NSP-004', 'NSP-005', 'NSP-006', 'NSP-007']:
        check(cid in br, f'含判定 {cid}')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
