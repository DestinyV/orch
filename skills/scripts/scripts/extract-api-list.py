#!/usr/bin/env python3
"""extract-api-list.py — 从 design.md 提取接口清单为 JSON"""
import sys, json, re, os

def extract_api_list(design_md):
    """从 design.md 提取接口清单"""
    result = {'apis': [], 'conventions': {}}
    with open(design_md) as f:
        content = f.read()

    # 提取接口（markdown 表格格式）
    api_sections = re.findall(r'\|\s*(GET|POST|PUT|DELETE|PATCH)\s*\|\s*(\S+)\s*\|\s*(.+?)\s*\|', content)
    for method, path, desc in api_sections:
        result['apis'].append({'method': method, 'path': path, 'description': desc.strip()})

    # 提取项目约定
    for section in ['URL风格', '响应格式', '认证方式', '分页格式', '错误码']:
        m = re.search(rf'{section}[:\s]*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if m:
            result['conventions'][section] = m.group(1).strip()[:200]

    return result

if __name__ == '__main__':
    design_file = sys.argv[1] if len(sys.argv) > 1 else 'orch-spec/default/design/design.md'
    if not os.path.isfile(design_file):
        print(json.dumps({'error': f'File not found: {design_file}'}))
        sys.exit(1)
    print(json.dumps(extract_api_list(design_file), ensure_ascii=False, indent=2))
