#!/usr/bin/env python3
"""T6.1 + T7.2 综合测试 — self-check + verdict 判定 (TC-S4-01..05 + TC-S6-02..07)。

断言：
  - self-check exit=0 且 5 块全 PASS
  - verdict.js judgeRate 边界/特殊值
  - judgeAutoResolve 规则自决 vs 白名单人工
"""
import json
import os
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
    print('=== T6.1 + T7.2 自检 + 量化判定 ===')

    # TC-S4-01 + TC-S6-01: self-check exit=0 + 5 block PASS
    print('\n-- TC-S6-01: self-check 5 block PASS --')
    proc = subprocess.run(
        ['node', os.path.join(PLUGIN_ROOT, 'scripts', 'self-check.js'), '--json'],
        capture_output=True, text=True, cwd=PLUGIN_ROOT,
    )
    check(proc.returncode == 0, f'self-check exit 0（实际 {proc.returncode}）')
    try:
        report = json.loads(proc.stdout)
        blocks = report.get('blocks', {})
        check(all(blocks.get(b) for b in ['orchestration','agents','skills','tdd_loop','commands_hooks']),
              f'5 块全部 PASS（实际: {blocks}）')
    except json.JSONDecodeError:
        check(False, 'self-check 输出可解析 JSON')

    # TC-S6-02/03: judgeRate 流转率
    print('\n-- TC-S6-02/03: 流转率判定 --')
    vj = os.path.join(PLUGIN_ROOT, 'scripts', 'lib', 'verdict.js')
    r = subprocess.run(['node', '-e', f"""
        const v = require('{vj.replace(chr(92), '/')}');
        console.log(JSON.stringify({{a: v.judgeRate(83, 80), b: v.judgeRate(75, 80)}}));
    """], capture_output=True, text=True)
    try:
        res = json.loads(r.stdout)
        check(res['a']['pass'] is True, f'flow_rate 83 ≥ 80 → pass（实际 {res["a"]}）')
        check(res['b']['pass'] is False, f'flow_rate 75 < 80 → fail（实际 {res["b"]}）')
    except (json.JSONDecodeError, KeyError):
        check(False, 'judgeRate 输出可解析')

    # TC-S6-04/05: judgeRate 达标率
    print('\n-- TC-S6-04/05: 达标率判定 --')
    r = subprocess.run(['node', '-e', f"""
        const v = require('{vj.replace(chr(92), '/')}');
        console.log(JSON.stringify({{a: v.judgeRate(90, 90), b: v.judgeRate(85, 90)}}));
    """], capture_output=True, text=True)
    try:
        res = json.loads(r.stdout)
        check(res['a']['pass'] is True, f'pass_rate 90 ≥ 90 → pass（实际 {res["a"]}）')
        check(res['b']['pass'] is False, f'pass_rate 85 < 90 → fail（实际 {res["b"]}）')
    except (json.JSONDecodeError, KeyError):
        check(False, 'judgeRate 输出可解析')

    # TC-S6-06/07: judgeAutoResolve
    print('\n-- TC-S6-06/07: 规则自决 vs 白名单人工 --')
    r = subprocess.run(['node', '-e', f"""
        const v = require('{vj.replace(chr(92), '/')}');
        const auto = ['compile failure','test failure','missing file','step retry'];
        const manual = ['requirement conflict','acceptance uncertain','HARD-GATE block','cross-repo change'];
        console.log(JSON.stringify({{
            auto: auto.map(v.judgeAutoResolve),
            manual: manual.map(v.judgeAutoResolve)
        }}));
    """], capture_output=True, text=True)
    try:
        res = json.loads(r.stdout)
        check(all(x == 'auto-resolve' for x in res['auto']), f'auto 集 4 项 → auto-resolve（实际 {res["auto"]}）')
        check(all(x == 'pause-for-human' for x in res['manual']), f'manual 集 4 项 → pause-for-human（实际 {res["manual"]}）')
    except (json.JSONDecodeError, KeyError):
        check(False, 'judgeAutoResolve 输出可解析')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
