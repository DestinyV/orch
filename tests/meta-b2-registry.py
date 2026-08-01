#!/usr/bin/env python3
"""T2.2 测试 — tdd-guide 注册 + deprecated (TC-S2-03/04)。

断言：
  - 磁盘 agent 数（去 _prompt-defense.md）= AGENTS.md 注册表链接数 = 26
  - AGENTS.md 每个链接文件存在；磁盘 agent 全部在注册表（tdd-guide deprecated 允许）
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
    print('=== T2.2 tdd-guide 注册 + deprecated ===')

    agents_dir = os.path.join(PLUGIN_ROOT, 'agents')
    # 磁盘 agent 数（去 _prompt-defense.md 和模板）
    disk_agents = []
    for f in os.listdir(agents_dir):
        if f.endswith('.md') and not f.startswith('_'):
            disk_agents.append(f)
    disk_count = len(disk_agents)

    # AGENTS.md 注册表链接数
    ag = open(os.path.join(PLUGIN_ROOT, 'AGENTS.md'), encoding='utf-8').read()
    reg_links = re.findall(r'\(agents/([\w-]+\.md)\)', ag)
    reg_names = sorted(set(reg_links))

    print('\n-- TC-S2-03: 磁盘数 = 注册表数 --')
    check(disk_count == 26, f'磁盘 agent 数 = 26（实际 {disk_count}: {sorted(disk_agents)}）')
    check(len(reg_names) == 26, f'AGENTS.md 注册数 = 26（实际 {len(reg_names)}）')
    check(disk_count == len(reg_names), f'磁盘数 == 注册数（{disk_count} vs {len(reg_names)}）')

    print('\n-- TC-S2-04: 注册表链接有效 + 磁盘全覆盖 --')
    # 每个注册链接文件存在
    broken = [r for r in reg_links if not os.path.exists(os.path.join(agents_dir, r))]
    check(len(broken) == 0, f'注册表链接全部存在（断链: {broken if broken else "无"}）')

    # 磁盘 agent 全部在注册表
    unregistered = [f for f in disk_agents if f not in reg_links]
    check(len(unregistered) == 0, f'磁盘 agent 全部在注册表（未登记: {unregistered if unregistered else "无"}）')

    # tdd-guide 已注册且 deprecated 标注
    print('\n-- tdd-guide deprecated 标注 --')
    check('tdd-guide.md' in reg_links, 'tdd-guide 已注册进 AGENTS.md')
    tdg = open(os.path.join(agents_dir, 'tdd-guide.md'), encoding='utf-8').read()
    check('DEPRECATED' in tdg, 'tdd-guide.md 含 DEPRECATED 标注')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
