#!/usr/bin/env python3
"""T1.3 测试 — session-start 中断恢复自动补偿。

断言 (TC-S1-04/05/06):
  - in_progress → 输出 resume-from-6 恢复建议
  - 前置产出缺失 → 输出具体缺失文件清单
  - 无进行中工作流 → no-op（不误报）
"""
import json
import os
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


def run_session_start(tmp_root):
    """在临时根目录运行 session-start.js，返回 stdout。"""
    env = dict(os.environ)
    env['CLAUDE_PLUGIN_ROOT'] = tmp_root
    # 强制 Node 输出 UTF-8，避免 Windows GBK 控制台编码问题
    env['PYTHONIOENCODING'] = 'utf-8'
    env['LANG'] = 'en_US.UTF-8'
    env['LC_ALL'] = 'en_US.UTF-8'
    try:
        proc = subprocess.run(
            ['node', os.path.join(PLUGIN_ROOT, 'scripts', 'hooks', 'session-start.js')],
            capture_output=True, timeout=8, env=env, cwd=tmp_root,
        )
        return proc.stdout.decode('utf-8', errors='replace') or ''
    except subprocess.TimeoutExpired:
        return ''


def make_state(tmp_root, req_id, current_stage, stages):
    """在临时根目录构造 in_progress 工作流。"""
    spec_dir = os.path.join(tmp_root, 'orch-spec', req_id)
    os.makedirs(spec_dir, exist_ok=True)
    state = {
        'workflow': 'orch',
        'requirement_id': req_id,
        'status': 'in_progress',
        'current_stage': current_stage,
        'stages': stages,
        'completion_report_generated': False,
    }
    json.dump(state, open(os.path.join(spec_dir, '.workflow-state.json'), 'w'), indent=2)


def main():
    print('=== T1.3 session-start 自动补偿 ===')

    # TC-S1-04: in_progress（stage 5 done，stage 6 未做）→ resume-from-6
    print('\n-- TC-S1-04: in_progress → resume-from-6 建议 --')
    with tempfile.TemporaryDirectory() as tmp:
        stages = [
            {'stage': '0_workflow_control', 'status': 'done'},
            {'stage': '1_spec_creation', 'status': 'done'},
            {'stage': '2_test_design', 'status': 'done'},
            {'stage': '3_code_design', 'status': 'done'},
            {'stage': '4_code_task', 'status': 'done'},
            {'stage': '5_code_execute', 'status': 'done'},
            {'stage': '6_code_test', 'status': 'in_progress'},
        ]
        make_state(tmp, 'mock-req', '6_code_test', stages)
        out = run_session_start(tmp)
        check('mock-req' in out, f'输出含工作流标识 mock-req（实际: {out.strip()[:120]}）')
        check(('resume-from-6' in out) or ('继续' in out) or ('/start-dev' in out),
              f'输出续接建议（含 resume/继续/start-dev）')

    # TC-S1-05: 前置产出缺失 → 具体缺失文件清单
    print('\n-- TC-S1-05: 前置产出缺失 → 缺失文件清单 --')
    with tempfile.TemporaryDirectory() as tmp:
        stages = [
            {'stage': '0_workflow_control', 'status': 'done'},
            {'stage': '1_spec_creation', 'status': 'done'},
            {'stage': '2_test_design', 'status': 'done'},
            {'stage': '3_code_design', 'status': 'done'},
            {'stage': '4_code_task', 'status': 'done'},
            {'stage': '5_code_execute', 'status': 'done'},
        ]
        make_state(tmp, 'mock-req', '5_code_execute', stages)
        # stage 6 前置产出 testing-report.md 缺失（未创建 testing/testing-report.md）
        out = run_session_start(tmp)
        check(('testing-report.md' in out) or ('缺失' in out),
              f'提示具体缺失文件 testing-report.md（实际: {out.strip()[:160]}）')

    # TC-S1-06: 无 in_progress → no-op
    print('\n-- TC-S1-06: 无进行中工作流 → no-op --')
    with tempfile.TemporaryDirectory() as tmp:
        out = run_session_start(tmp)
        check('resume-from' not in out and '工作流进行中' not in out,
              f'无恢复建议输出（不误报，实际: {out.strip()[:100]}）')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
