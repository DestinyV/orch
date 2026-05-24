#!/usr/bin/env python3
"""scan-exceptions.py — 扫描项目异常类名、错误码格式、RPC 调用模式"""
import sys, json, re, os, subprocess, glob

def scan_exceptions(src_dir):
    """扫描项目中的异常处理约定"""
    result = {'exception_classes': [], 'error_codes': [], 'rpc_patterns': [], 'module_errors': {}}

    # 扫描异常类名
    for ext, pattern in [('*.java', r'(?:class\s+)(\w*(?:Exception|Error)\w*)'),
                          ('*.ts', r'(?:class\s+|type\s+|interface\s+)(\w*(?:Error)\w*)'),
                          ('*.py', r'class\s+(\w*(?:Exception)\w*)')]:
        for f in glob.glob(os.path.join(src_dir, '**', ext), recursive=True):
            try:
                with open(f) as fh:
                    for line in fh:
                        m = re.search(pattern, line)
                        if m:
                            result['exception_classes'].append({'class': m.group(1), 'file': os.path.relpath(f, src_dir)})
            except: pass

    # 扫描错误码文件
    for pattern in ['**/error*.properties', '**/errors*.ts', '**/error*.json', '**/*error*.java']:
        for f in glob.glob(os.path.join(src_dir, pattern), recursive=True):
            rel = os.path.relpath(f, src_dir)
            result['error_codes'].append({'file': rel})

    # 扫描 RPC 调用
    for ext, pattern in [('*.java', r'(\w+)\s*\.\s*(\w+)\s*\('),
                          ('*.ts', r'(?:fetch|axios|request)\s*\(')]:
        for f in glob.glob(os.path.join(src_dir, '**', ext), recursive=True):
            try:
                with open(f) as fh:
                    for i, line in enumerate(fh, 1):
                        if re.search(pattern, line):
                            result['rpc_patterns'].append({'file': os.path.relpath(f, src_dir), 'line': i})
            except: pass

    # 去重异常类
    seen = set()
    unique = []
    for item in result['exception_classes']:
        if item['class'] not in seen:
            seen.add(item['class'])
            unique.append(item)
    result['exception_classes'] = unique[:50]  # 限制数量

    return result

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'src'
    if not os.path.isdir(src):
        print(json.dumps({'error': f'Source directory not found: {src}'}))
        sys.exit(1)
    print(json.dumps(scan_exceptions(src), ensure_ascii=False, indent=2))
