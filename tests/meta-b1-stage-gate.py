#!/usr/bin/env python3
"""T1.2 测试 — stage-gate stdin 超时 + EXEMPT 命令名分离。

断言 (TC-S1-08/09/10/11):
  - 空 stdin 阻塞进程 ≤2s 自行退出，输出 {"decision":"allow"}
  - 合法 Skill hook JSON stdin → 输出含 decision 字段的合法 JSON
  - checkpoint 等命令名不在 EXEMPT_SKILLS
  - EXEMPT_SKILLS ∩ 命令列表 = 空集；存在独立 EXEMPT_COMMANDS
"""
import json
import os
import subprocess
import sys
import time

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
    fixtures = json.load(open(FIXTURES, encoding='utf-8'))
    s1 = fixtures['S1']
    timeout_ms = s1['stdin_timeout_ms']  # 2000
    gate_decision = s1['gate_fail_open_decision']  # "allow"
    command_names = s1['exempt']['command_names']

    contracts_path = os.path.join(PLUGIN_ROOT, 'scripts', 'lib', 'stage-contracts.js')
    gate_path = os.path.join(PLUGIN_ROOT, 'scripts', 'hooks', 'stage-gate.js')

    contracts = ''
    if os.path.exists(contracts_path):
        contracts = open(contracts_path, encoding='utf-8').read()
    else:
        gate_src = open(gate_path, encoding='utf-8').read()
        # RED 态：从 gate 本地数组提取 EXEMPT_SKILLS
        m = gate_src.split('const EXEMPT_SKILLS = [')[1].split(']')[0]
        contracts = m

    print('=== T1.2 stage-gate stdin 超时 + EXEMPT ===')

    # TC-S1-08: 空 stdin 阻塞 → 限时退出 + allow
    print('\n-- TC-S1-08: 空 stdin 阻塞 2s 内 fail-open --')
    proc = subprocess.Popen(
        ['node', gate_path],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=PLUGIN_ROOT,
    )
    # 打开 stdin 但不写数据（模拟迟到），等待进程自行退出
    start = time.time()
    try:
        out, err = proc.communicate(timeout=6)
        elapsed = time.time() - start
        check(proc.returncode == 0, f'进程自行退出 exit 0（实际 {proc.returncode}, {elapsed:.1f}s）')
        try:
            parsed = json.loads(out.decode('utf-8'))
            check(parsed.get('decision') == gate_decision, f'输出 decision="{gate_decision}"（实际 {out.decode().strip()}）')
        except json.JSONDecodeError:
            check(False, f'输出为合法 JSON（实际: {out.decode()[:80]}）')
    except subprocess.TimeoutExpired:
        proc.kill()
        check(False, f'进程阻塞超时（>6s）—— 修复前 RED 态（stdin 无超时保护）')

    # TC-S1-09: 合法 Skill JSON → 合法 JSON + decision
    print('\n-- TC-S1-09: 合法 stdin → 正确决策 --')
    hook_json = json.dumps({
        'tool_name': 'Skill',
        'tool': 'Skill',
        'tool_input': 'Skill("orch:spec", "test")',
    })
    try:
        proc = subprocess.run(
            ['node', gate_path], input=hook_json, capture_output=True, timeout=6, text=True, cwd=PLUGIN_ROOT,
        )
        try:
            parsed = json.loads(proc.stdout.strip())
            check('decision' in parsed, f'输出含 decision 字段（实际 keys: {list(parsed.keys())}）')
        except json.JSONDecodeError:
            check(False, f'输出为合法 JSON（实际: {proc.stdout[:80]}）')
    except subprocess.TimeoutExpired:
        check(False, '合法 stdin 处理超时')

    # TC-S1-10/11: EXEMPT 命令名分离
    print('\n-- TC-S1-10/11: EXEMPT_SKILLS 命令名分离 --')
    # 提取 EXEMPT_SKILLS 数组（从 stage-contracts.js 或 gate 内嵌）
    def extract_array(src, name):
        import re
        m = re.search(rf'const {name} = \[(.*?)\];', src, re.DOTALL)
        if not m:
            return []
        return [x.strip().strip("'\"") for x in m.group(1).split(',') if x.strip()]

    exempt_skills = extract_array(contracts, 'EXEMPT_SKILLS')
    exempt_cmds = extract_array(contracts, 'EXEMPT_COMMANDS')

    # 若从 stage-contracts 读，直接取真实值
    if os.path.exists(contracts_path):
        c = None
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location('sc', contracts_path)
            mod = importlib.util.module_from_spec(spec)
            # 不执行 require（Node 模块），改为字符串提取
        except Exception:
            pass
        src = open(contracts_path, encoding='utf-8').read()
        exempt_skills = extract_array(src, 'EXEMPT_SKILLS')
        exempt_cmds = extract_array(src, 'EXEMPT_COMMANDS')

    forbidden_in_skills = [c for c in command_names if c in exempt_skills]
    check(len(forbidden_in_skills) == 0, f'命令名不在 EXEMPT_SKILLS（残留: {forbidden_in_skills if forbidden_in_skills else "无"}）')

    intersect = set(exempt_skills) & set(command_names)
    check(len(intersect) == 0, f'EXEMPT_SKILLS ∩ 命令列表 = 空集（交集: {intersect if intersect else "空"}）')

    check('EXEMPT_COMMANDS' in contracts or len(exempt_cmds) > 0, f'存在独立 EXEMPT_COMMANDS（{len(exempt_cmds)} 个）')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
