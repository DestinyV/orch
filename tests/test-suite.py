#!/usr/bin/env python3
"""orch test suite"""

import os, sys, json, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
warnings = []

def parse_fm(path):
    c = open(path, encoding="utf-8").read()
    if not c.startswith("---"): return None, c
    p = c.split("---", 2)
    if len(p) < 3: return None, c
    fm = {}
    for l in p[1].strip().split("\n"):
        m = re.match(r"^(\w+)\s*:\s*(.+)$", l)
        if m: fm[m.group(1)] = m.group(2).strip()
    return fm, p[2]

print("=== 1. DIR STRUCTURE ===")
for d in ["skills","agents","commands","docs","hooks","references","config","schemas","rules","scripts/lib",".claude-plugin",".cursor/rules",".gemini",".opencode",".codex",".codebuddy"]:
    print(f"  {'OK' if os.path.isdir(os.path.join(ROOT,d)) else 'MISS'}  {d}")
    if not os.path.isdir(os.path.join(ROOT,d)): errors.append(f"Missing dir: {d}")

for f in ["AGENTS.md","COMMANDS.md","RULES.md","CLAUDE.md"]:
    print(f"  {'OK' if os.path.isfile(os.path.join(ROOT,f)) else 'MISS'}  {f}")
    if not os.path.isfile(os.path.join(ROOT,f)): errors.append(f"Missing: {f}")

print("\n=== 2. FRONTMATTER (agents+commands) ===")
for pf in ("agents","commands"):
    d = os.path.join(ROOT, pf)
    for f in sorted(os.listdir(d)):
        if not f.endswith(".md"): continue
        fm, _ = parse_fm(os.path.join(d, f))
        if fm is None: errors.append(f"{pf}/{f}: no frontmatter")
        elif "name" not in fm and "description" not in fm: errors.append(f"{pf}/{f}: missing name/description")
        else: print(f"  OK  {pf}/{f}")

print("\n=== 3. SKILL SKILL.md ===")
for skill in sorted(os.listdir(os.path.join(ROOT,"skills"))):
    sp = os.path.join(ROOT,"skills",skill)
    if not os.path.isdir(sp): continue
    sm = os.path.join(sp,"SKILL.md")
    if not os.path.isfile(sm): warnings.append(f"skills/{skill}: no SKILL.md")
    else:
        fm, _ = parse_fm(sm)
        print(f"  {'OK' if fm else 'WARN'}  skills/{skill}/SKILL.md")

print("\n=== 4. AGENTS.md XREF ===")
am = open(os.path.join(ROOT,"AGENTS.md"), encoding="utf-8").read()
for name, fp in re.findall(r'\[([^\]]+)\]\(agents/([^)]+)\)', am):
    if os.path.isfile(os.path.join(ROOT,"agents",fp)): print(f"  OK  agents/{fp}")
    else: errors.append(f"AGENTS.md -> agents/{fp} not found")

print("\n=== 5. JSON ===")
for jf in [".claude-plugin/plugin.json",".claude-plugin/marketplace.json","schemas/workflow-state.json","schemas/workflow-eval.json","config/stacks.json","config/platforms.json","skills/package.json"]:
    fp = os.path.join(ROOT,jf)
    if not os.path.isfile(fp): warnings.append(f"Missing: {jf}"); continue
    try:
        json.load(open(fp, encoding="utf-8"))
        print(f"  OK  {jf}")
    except Exception as ex: errors.append(f"Invalid JSON {jf}: {ex}")

print("\n=== 6. WORKFLOW ===")
sd = open(os.path.join(ROOT,"commands/start-dev.md"), encoding="utf-8").read()
wfc = open(os.path.join(ROOT,"skills/workflow/SKILL.md"), encoding="utf-8").read()
steps = re.findall(r"^\| *(\d+(?:\.\d+)?) *\| *(\S[^|]+)", sd, re.MULTILINE)
print(f"  OK  start-dev.md: {len(steps)} steps")
hg = wfc.count("<HARD-GATE>")
print(f"  OK  workflow-control: {hg} HARD-GATEs") if hg >= 3 else warnings.append(f"workflow-control: {hg} HARD-GATEs")
old = wfc.count("../scripts/") + wfc.count("bash ../")
print(f"  OK  no old paths") if old == 0 else errors.append(f"workflow-control: {old} old paths")
print(f"  OK  cross-ref") if "start-dev.md" in wfc else warnings.append("no cross-ref")

print("\n=== 7. PLATFORMS ===")
for plat, flist in {".cursor":[".cursor/hooks.json",".cursor/rules/common-development-workflow.mdc"],".gemini":[".gemini/GEMINI.md"],".opencode":[".opencode/opencode.json"],".codex":[".codex/AGENTS.md",".codex/config.toml"],".codebuddy":[".codebuddy/README.md",".codebuddy/install.js"]}.items():
    miss = [f for f in flist if not os.path.isfile(os.path.join(ROOT,f))]
    if miss: errors.append(f"{plat}: missing {miss}")
    else: print(f"  OK  {plat}: {len(flist)} files")

print(f"\n--- SUMMARY: {len(errors)} errors, {len(warnings)} warnings ---")
for e in errors: print(f"  ERR: {e}")
for w in warnings: print(f"  WARN: {w}")
if not errors: print("ALL PASSED")
sys.exit(1 if errors else 0)
