#!/usr/bin/env python3
"""extract-test-verify.py — 从 scenarios/*.md 提取 TEST-VERIFY + Mock Data 为 JSON"""
import sys, json, re, glob, os

def extract_test_verify(scenarios_dir):
    """从 orch-spec/{req}/spec/scenarios/ 提取所有 TEST-VERIFY"""
    results = []
    files = sorted(glob.glob(os.path.join(scenarios_dir, '*.md')))
    for f in files:
        with open(f) as fh:
            content = fh.read()
        # 提取场景名
        scene_match = re.search(r'##\s*场景[:\s]+(.+)', content)
        scene_name = scene_match.group(1).strip() if scene_match else os.path.basename(f)
        # 提取 TEST-VERIFY
        tvs = re.findall(r'标识符:\s*TV-(\d+?):\s*(.+?)\n\*\*WHEN\*\*\s*(.+?)\s*\*\*THEN\*\*\s*(.+?)(?=\n标识符:|\n###\s|---|\Z)', content, re.DOTALL)
        for tv_id, tv_desc, when, then in tvs:
            # 提取 Mock Data
            mock_section = re.search(r'###\s*Mock\s*Data\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
            mock_data = {}
            if mock_section:
                mock_text = mock_section.group(1)
                for key in ['有效输入', '边界值', '特殊值', '依赖Mock']:
                    m = re.search(r'\*\*(' + key + r')\*\*\s*[：:]\s*(.+?)(?:\n\*\*|$)', mock_text, re.DOTALL)
                    if m:
                        mock_data[key] = m.group(2).strip()
            results.append({
                'file': os.path.basename(f),
                'scene': scene_name,
                'tv_id': f'TV-{tv_id}',
                'description': tv_desc.strip(),
                'when': when.strip(),
                'then': then.strip(),
                'mock_data': mock_data
            })
    return results

if __name__ == '__main__':
    scenarios_dir = sys.argv[1] if len(sys.argv) > 1 else 'orch-spec'
    if not os.path.isdir(scenarios_dir):
        print(json.dumps({'error': f'Directory not found: {scenarios_dir}'}))
        sys.exit(1)
    result = extract_test_verify(scenarios_dir)
    print(json.dumps({'count': len(result), 'test_verify': result}, ensure_ascii=False, indent=2))
