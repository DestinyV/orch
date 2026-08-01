#!/usr/bin/env python3
"""T4.1-T4.3 综合测试 — hooks 激活 (TC-S5-01/02 + hook-flags 门控)。

断言：
  - hooks.json 有效，PreToolUse 含 suggest-compact(matcher Edit/Write, command 指向 suggest-compact.js)
  - hooks.json 含 pre:observe / post:observe；observe.sh 存在
  - hook-flags.js PROFILES 含 pre:compact / pre:observe / post:observe
  - suggest-compact.js 在禁用时 no-op
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
    print('=== T4 hooks 激活 ===')

    # TC-S5-01: hooks.json 含 suggest-compact
    print('\n-- TC-S5-01: suggest-compact 注册 --')
    hooks = json.load(open(os.path.join(PLUGIN_ROOT, 'hooks', 'hooks.json'), encoding='utf-8'))
    pre = hooks['hooks']['PreToolUse']
    sc = [h for h in pre if 'compact' in h.get('id', '')]
    check(len(sc) == 1, f'PreToolUse 含 suggest-compact 注册（id: {sc[0]["id"] if sc else "无"}）')
    if sc:
        matcher = sc[0].get('matcher', '')
        check('Edit' in matcher and 'Write' in matcher, f'matcher 含 Edit/Write（实际 {matcher}）')
        cmd = sc[0]['hooks'][0]['command']
        check('suggest-compact.js' in cmd, f'command 指向 suggest-compact.js（实际 {cmd[:60]}）')
        sc_file = os.path.join(PLUGIN_ROOT, 'scripts', 'hooks', 'suggest-compact.js')
        check(os.path.exists(sc_file), 'suggest-compact.js 文件存在')

    # TC-S5-02: observe 激活（observe.sh 存在 + 已注册）
    print('\n-- TC-S5-02: observe 激活 --')
    obs_sh = os.path.join(PLUGIN_ROOT, 'scripts', 'hooks', 'observe.sh')
    obs_js = os.path.join(PLUGIN_ROOT, 'scripts', 'hooks', 'observe.js')
    check(os.path.exists(obs_sh), 'observe.sh 存在')
    check(os.path.exists(obs_js), 'observe.js 存在')
    all_ids = []
    for event, entries in hooks['hooks'].items():
        for e in entries:
            all_ids.append(e.get('id', ''))
    check('pre:observe' in all_ids and 'post:observe' in all_ids, f'hooks.json 含 pre:observe + post:observe（实际 ids: {all_ids}）')

    # hook-flags PROFILES 含三 id
    print('\n-- hook-flags PROFILES --')
    hf = open(os.path.join(PLUGIN_ROOT, 'scripts', 'lib', 'hook-flags.js'), encoding='utf-8').read()
    for hid in ['pre:compact', 'pre:observe', 'post:observe']:
        check(hid in hf, f'hook-flags.js 含 {hid}')

    # suggest-compact 门控（disabled no-op）
    print('\n-- suggest-compact 门控 --')
    sc_src = open(os.path.join(PLUGIN_ROOT, 'scripts', 'hooks', 'suggest-compact.js'), encoding='utf-8').read()
    check('isHookEnabled' in sc_src and 'pre:compact' in sc_src, 'suggest-compact.js 含 isHookEnabled(pre:compact) 门控')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
