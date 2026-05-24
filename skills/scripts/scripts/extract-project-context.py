#!/usr/bin/env python3
"""extract-project-context.py — 从项目提取技术栈/分层/命名约定"""
import sys, json, re, os, glob

def extract_context(project_root):
    """提取项目上下文"""
    ctx = {'tech_stack': [], 'layers': [], 'naming': [], 'imports': [], 'config_files': []}

    # 检测技术栈
    pkg = os.path.join(project_root, 'package.json')
    if os.path.isfile(pkg):
        ctx['tech_stack'].append('Node.js/TypeScript')
    if os.path.isfile(os.path.join(project_root, 'pom.xml')):
        ctx['tech_stack'].append('Java/Maven')
    if os.path.isfile(os.path.join(project_root, 'go.mod')):
        ctx['tech_stack'].append('Go')
    if os.path.isfile(os.path.join(project_root, 'Cargo.toml')):
        ctx['tech_stack'].append('Rust')
    if os.path.isfile(os.path.join(project_root, 'pyproject.toml')):
        ctx['tech_stack'].append('Python')
    if os.path.isfile(os.path.join(project_root, 'requirements.txt')):
        ctx['tech_stack'].append('Python')

    # 检测分层结构
    for pattern in ['src/controllers', 'src/services', 'src/repository', 'src/domain',
                    'src/components', 'src/pages', 'src/api', 'src/store']:
        if os.path.isdir(os.path.join(project_root, pattern)):
            ctx['layers'].append(pattern)

    # 检测命名约定
    for ext, pattern in [('*.vue', r'(?:export\s+default\s+|function\s+|class\s+)(\w+)'),
                          ('*.ts', r'(?:export\s+(?:default\s+)?(?:const|function|class)\s+)(\w+)')]:
        for f in glob.glob(os.path.join(project_root, 'src', '**', ext), recursive=True)[:20]:
            try:
                with open(f) as fh:
                    for line in fh:
                        m = re.search(pattern, line)
                        if m:
                            ctx['naming'].append(m.group(1))
                            break
            except: pass
        if ctx['naming']: break

    # 配置文件
    for cf in ['package.json', 'tsconfig.json', '.eslintrc*', 'pom.xml', 'go.mod', 'pyproject.toml']:
        for f in glob.glob(os.path.join(project_root, cf)):
            ctx['config_files'].append(os.path.relpath(f, project_root))

    # 去重
    ctx['naming'] = list(set(ctx['naming']))[:20]
    return ctx

if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    print(json.dumps(extract_context(root), ensure_ascii=False, indent=2))
