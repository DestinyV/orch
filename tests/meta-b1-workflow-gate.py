#!/usr/bin/env python3
"""T1.1 测试 — workflow-gate STAGE_OUTPUTS 覆盖 + stage-contracts 集中化。

断言 (TC-S1-01/02/03):
  - STAGE_OUTPUTS 覆盖全部 8 个阶段 key
  - 3.5/5/6/9 各含预期产出文件
  - 未知 stage fail-open（不崩溃）
"""
import json
import os
import re
import subprocess
import sys
import tempfile

PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FIXTURES = os.path.join(PLUGIN_ROOT, 'orch-spec', 'plugin-capability-optimization', 'tests', 'fixtures.json')

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
    print('=== T1.1 workflow-gate STAGE_OUTPUTS 覆盖 ===')
    fixtures = json.load(open(FIXTURES, encoding='utf-8'))
    s1 = fixtures['S1']
    all_stages = s1['stages_expected']['all_stages']
    stage_map = s1['stages_expected']['stage_outputs_map']

    # 定位 stage-contracts.js 或 workflow-gate.js
    contracts_path = os.path.join(PLUGIN_ROOT, 'scripts', 'lib', 'stage-contracts.js')
    gate_path = os.path.join(PLUGIN_ROOT, 'scripts', 'hooks', 'workflow-gate.js')
    source = ''
    if os.path.exists(contracts_path):
        source = open(contracts_path, encoding='utf-8').read()
        print(f'  [INFO] 读取 stage-contracts.js')
    elif os.path.exists(gate_path):
        source = open(gate_path, encoding='utf-8').read()
        print(f'  [INFO] 读取 workflow-gate.js（stage-contracts 尚不存在，RED 态）')
    else:
        check(False, 'stage-contracts.js 或 workflow-gate.js 存在')
        sys.exit(1)

    # TC-S1-01: 全部 8 阶段 key
    print('\n-- TC-S1-01: STAGE_OUTPUTS 覆盖 8 阶段 --')
    missing_keys = [k for k in all_stages if f"'{k}'" not in source]
    check(len(missing_keys) == 0, f'STAGE_OUTPUTS 含全部 8 key（缺失: {missing_keys if missing_keys else "无"}）')

    # TC-S1-02: 3.5/5/6/9 各含预期产出
    print('\n-- TC-S1-02: 3.5/5/6/9 各含预期产出 --')
    for stage, outs in stage_map.items():
        for out in outs:
            check(out in source, f'STAGE_OUTPUTS[{stage}] 含 "{out}"')

    # TC-S1-03: 未知 stage fail-open（行为测试）
    print('\n-- TC-S1-03: 未知 stage fail-open --')
    if os.path.exists(gate_path):
        with tempfile.TemporaryDirectory() as tmp:
            # 造一个 unknown stage 的 in_progress 工作流
            spec_dir = os.path.join(tmp, 'orch-spec')
            os.makedirs(spec_dir)
            req_dir = os.path.join(spec_dir, 'mock-req')
            os.makedirs(req_dir)
            state = {
                'workflow': 'orch',
                'requirement_id': 'mock-req',
                'status': 'in_progress',
                'current_stage': 'unknown_stage',
                'stages': [],
            }
            json.dump(state, open(os.path.join(req_dir, '.workflow-state.json'), 'w'))
            env = dict(os.environ)
            env['CLAUDE_PLUGIN_ROOT'] = tmp
            hook_json = json.dumps({'tool': 'Skill', 'tool_name': 'Skill', 'name': 'orch:spec'})
            try:
                proc = subprocess.run(
                    ['node', gate_path], input=hook_json, capture_output=True,
                    timeout=6, env=env, text=True,
                )
                check(proc.returncode == 0, f'workflow-gate exit 0（实际 {proc.returncode}）')
                check('stack' not in (proc.stderr or '').lower(), 'stderr 无 stack trace')
            except subprocess.TimeoutExpired:
                check(False, 'workflow-gate 超时（>6s）')
    else:
        check(False, 'workflow-gate.js 存在')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
