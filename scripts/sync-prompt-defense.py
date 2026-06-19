#!/usr/bin/env python3
"""Sync Prompt Defense Baseline from _prompt-defense.md into all agent files."""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

defense_path = os.path.join(ROOT, 'agents', '_prompt-defense.md')
with open(defense_path, encoding='utf-8') as f:
    content = f.read()

m = re.search(r'```\s*\n(.*?)```', content, re.DOTALL)
if not m:
    print('ERROR: could not extract defense text from _prompt-defense.md')
    exit(1)
canonical = m.group(1).strip()

for fp in sorted(glob.glob(os.path.join(ROOT, 'agents', '*.md'))):
    fname = os.path.basename(fp)
    if fname == '_prompt-defense.md':
        continue
    with open(fp, encoding='utf-8') as f:
        orig = f.read()
    if '## Prompt Defense Baseline' not in orig:
        print(f'SKIP {fname}: no section')
        continue
    new_text = re.sub(
        r'## Prompt Defense Baseline\n.*?(?=\n## |\Z)',
        '## Prompt Defense Baseline\n\n' + canonical + '\n',
        orig, count=1, flags=re.DOTALL
    )
    if new_text == orig:
        print(f'SAME {fname}')
        continue
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print(f'OK   {fname}')

print('\nDone')
