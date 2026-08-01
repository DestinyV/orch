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
        # 跳过共享模板（如 _prompt-defense.md，非 agent）
        if f.startswith("_"): continue
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
print(f"  OK  workflow: {hg} HARD-GATEs") if hg >= 3 else warnings.append(f"workflow: {hg} HARD-GATEs")
old = wfc.count("../scripts/") + wfc.count("bash ../")
print(f"  OK  no old paths") if old == 0 else errors.append(f"workflow: {old} old paths")
print(f"  OK  cross-ref") if "start-dev.md" in wfc else warnings.append("no cross-ref")

print("\n=== 7. PLATFORMS ===")
for plat, flist in {".cursor":[".cursor/hooks.json",".cursor/rules/common-development-workflow.mdc"],".gemini":[".gemini/GEMINI.md"],".opencode":[".opencode/opencode.json"],".codex":[".codex/AGENTS.md",".codex/config.toml"],".codebuddy":[".codebuddy/README.md",".codebuddy/install.js"]}.items():
    miss = [f for f in flist if not os.path.isfile(os.path.join(ROOT,f))]
    if miss: errors.append(f"{plat}: missing {miss}")
    else: print(f"  OK  {plat}: {len(flist)} files")

print("\n=== 8. CAPABILITY CHECKS (T6.3) ===")
# GATE 覆盖：22 个 skill 中 ≥21 含 <GATE>（cost 现已含）
no_gate = []
for skill in sorted(os.listdir(os.path.join(ROOT,"skills"))):
    sp = os.path.join(ROOT,"skills",skill)
    if not os.path.isdir(sp): continue
    sm = os.path.join(sp,"SKILL.md")
    if os.path.isfile(sm):
        c = open(sm, encoding="utf-8").read()
        if "<GATE>" not in c: no_gate.append(skill)
print(f"  {'OK' if len(no_gate) <= 1 else 'FAIL'}  GATE 覆盖 22 skills（无 GATE: {no_gate if no_gate else '无'}）")
if len(no_gate) > 1: errors.append(f"skills without GATE: {no_gate}")

# 无 project-map.md 残留
pm = 0
for root_dir, _, files in os.walk(os.path.join(ROOT,"agents")):
    for f in files:
        if f.endswith(".md") and "project-map.md" in open(os.path.join(root_dir,f), encoding="utf-8").read(): pm += 1
print(f"  {'OK' if pm == 0 else 'FAIL'}  no project-map.md residue ({pm})")
if pm > 0: errors.append(f"{pm} project-map.md references")

# 无 /hookify
hk = 0
for f in os.listdir(os.path.join(ROOT,"agents")):
    if f.endswith(".md") and "hookify" in open(os.path.join(ROOT,"agents",f), encoding="utf-8").read(): hk += 1
print(f"  {'OK' if hk == 0 else 'FAIL'}  no /hookify residue ({hk})")
if hk > 0: errors.append(f"{hk} /hookify references")

# hooks.json 含 suggest-compact + observe
try:
    hooks = json.load(open(os.path.join(ROOT,"hooks","hooks.json"), encoding="utf-8"))
    ids = [e.get("id","") for ev in hooks.get("hooks",{}).values() for e in ev]
    ok_sc = "pre:compact" in ids
    ok_ob = "pre:observe" in ids and "post:observe" in ids
    print(f"  {'OK' if ok_sc else 'FAIL'}  hooks.json suggest-compact ({'pre:compact' in ids})")
    print(f"  {'OK' if ok_ob else 'FAIL'}  hooks.json observe ({'pre:observe' in ids}/{ 'post:observe' in ids})")
    if not ok_sc: errors.append("hooks.json missing suggest-compact")
    if not ok_ob: errors.append("hooks.json missing observe")
except Exception as ex:
    errors.append(f"hooks.json: {ex}")

# observer.enabled = true
try:
    cfg = json.load(open(os.path.join(ROOT,"skills","continuous-learning","config.json"), encoding="utf-8"))
    ok_ob_enabled = cfg.get("observer",{}).get("enabled") is True
    print(f"  {'OK' if ok_ob_enabled else 'FAIL'}  observer.enabled=true")
    if not ok_ob_enabled: errors.append("observer.enabled != true")
except Exception as ex:
    errors.append(f"config.json: {ex}")

# git 无 pyc
try:
    import subprocess
    out = subprocess.run(["git","ls-files"], capture_output=True, text=True, cwd=ROOT).stdout
    pyc = [l for l in out.split("\n") if ".pyc" in l or "__pycache__" in l]
    print(f"  {'OK' if not pyc else 'FAIL'}  git no .pyc ({len(pyc)})")
    if pyc: errors.append(f"pyc in git: {pyc}")
except Exception as ex:
    warnings.append(f"git check skipped: {ex}")

print(f"\n--- SUMMARY: {len(errors)} errors, {len(warnings)} warnings ---")
for e in errors: print(f"  ERR: {e}")
for w in warnings: print(f"  WARN: {w}")
if not errors: print("ALL PASSED")
sys.exit(1 if errors else 0)
