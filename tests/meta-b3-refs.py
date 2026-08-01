#!/usr/bin/env python3
"""T3.1 测试 — skills 悬空引用修复 (TC-S3-01/02/03)。

断言：
  - execute/SKILL.md 引用 context-inheritance-protocol.md 且文件存在；不含 context-injection-protocol.md
  - spec/SKILL.md 引用 ../design/references/diagram-trigger-rules.md 且文件存在
  - skills/ 全部 .md 链接交叉校验无悬空
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


def resolve_path(base_file, rel_path):
    """解析 markdown 相对链接路径。"""
    # 去掉锚点
    rel = rel_path.split('#')[0]
    # 去掉行号片段
    rel = re.sub(r':\d+$', '', rel)
    target = os.path.normpath(os.path.join(os.path.dirname(base_file), rel))
    return target


def main():
    print('=== T3.1 skills 悬空引用修复 ===')

    # TC-S3-01: execute 引用
    print('\n-- TC-S3-01: execute 引用 --')
    exe = open(os.path.join(PLUGIN_ROOT, 'skills', 'execute', 'SKILL.md'), encoding='utf-8').read()
    check('context-inheritance-protocol.md' in exe, 'execute/SKILL.md 含 context-inheritance-protocol.md')
    check('context-injection-protocol.md' not in exe, 'execute/SKILL.md 不含 context-injection-protocol.md')
    inh_path = os.path.join(PLUGIN_ROOT, 'skills', 'workflow', 'references', 'context-inheritance-protocol.md')
    check(os.path.exists(inh_path), f'目标文件存在: {os.path.relpath(inh_path, PLUGIN_ROOT)}')

    # TC-S3-02: spec 引用
    print('\n-- TC-S3-02: spec 引用 --')
    spec = open(os.path.join(PLUGIN_ROOT, 'skills', 'spec', 'SKILL.md'), encoding='utf-8').read()
    check('../design/references/diagram-trigger-rules.md' in spec, 'spec/SKILL.md 含 ../design/references/diagram-trigger-rules.md')
    dtg = os.path.join(PLUGIN_ROOT, 'skills', 'design', 'references', 'diagram-trigger-rules.md')
    check(os.path.exists(dtg), f'目标文件存在: {os.path.relpath(dtg, PLUGIN_ROOT)}')

    # TC-S3-03: skills/ 全部引用交叉校验
    # 注意：templates/ 目录中的模板引用是"输出占位"（渲染后才产生文件，如 ./scenarios/、./data-models.md），
    # 以及跨目录相对约定（如 ../design/design.md 是模板运行时在 req-context 下的相对路径）。
    # 真实悬空 = 非 templates 的 SKILL.md 引用不存在的文件。
    print('\n-- TC-S3-03: skills/ 引用交叉校验（SKILL.md 非模板）--')
    dangling = []
    total_refs = 0
    for root, dirs, files in os.walk(os.path.join(PLUGIN_ROOT, 'skills')):
        for f in files:
            if not f.endswith('.md'):
                continue
            fp = os.path.join(root, f)
            # 跳过 templates/ 中的模板文件（输出占位引用）
            if 'templates' in fp.replace('\\', '/'):
                continue
            src = open(fp, encoding='utf-8').read()
            refs = re.findall(r'\]\(([^)]+)\)', src)
            for ref in refs:
                if ref.startswith(('http://', 'https://', '#', 'mailto:')):
                    continue
                total_refs += 1
                target = resolve_path(fp, ref)
                if not os.path.exists(target):
                    dangling.append(f'{os.path.relpath(fp, PLUGIN_ROOT)} -> {ref}')
    check(len(dangling) == 0, f'skills/ SKILL.md 全部 {total_refs} 个相对引用无悬空（悬空: {dangling[:5] if dangling else "无"}）')

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
