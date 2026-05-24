#!/usr/bin/env python3
"""
Instinct CLI — Manage instincts for continuous-learning v2

Commands:
  status   - Show all instincts (project + global) with confidence
  import   - Import instincts from file
  export   - Export instincts to file
  evolve   - Cluster related instincts into skills/commands
  promote  - Promote project instincts to global scope
  projects - List all known projects and instinct counts
  prune    - Delete pending instincts older than TTL
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def resolve_knc_dir() -> Path:
    override = os.environ.get("KNC_HOMUNCULUS_DIR")
    if override and Path(override).is_absolute():
        return Path(override)
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg and Path(xdg).is_absolute():
        return Path(xdg) / "knc-homunculus"
    return Path.home() / ".local" / "share" / "knc-homunculus"


def detect_project() -> dict:
    """Detect current project context."""
    if os.environ.get("KNC_PROJECT_ID") and os.environ.get("KNC_PROJECT_NAME"):
        return {
            "id": os.environ["KNC_PROJECT_ID"],
            "name": os.environ["KNC_PROJECT_NAME"],
        }

    try:
        toplevel = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()
        if toplevel:
            name = Path(toplevel).name
            remote = subprocess.run(
                ["git", "-C", toplevel, "remote", "get-url", "origin"],
                capture_output=True, text=True, timeout=5
            ).stdout.strip()
            pid = hashlib.md5((remote or toplevel).encode()).hexdigest()[:12]
            return {"id": pid, "name": name}
    except Exception:
        pass

    return {"id": "global", "name": "global"}


KNC_DIR = resolve_knc_dir()


def project_obs_dir(project_id: str) -> Path:
    if project_id in ("global", "unknown"):
        return KNC_DIR
    return KNC_DIR / "projects" / project_id


def glob_instincts(base_dir: Path) -> list[Path]:
    """Find all instinct yaml files under a directory."""
    if not base_dir.exists():
        return []
    return sorted(base_dir.rglob("*.yaml")) + sorted(base_dir.rglob("*.md"))


def parse_instinct(filepath: Path) -> Optional[dict]:
    """Parse a YAML-frontmatter instinct file into a dict."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return None

    if not text.startswith("---"):
        return None

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None

    front = parts[1].strip()
    body = parts[2].strip()

    instinct = {"file": str(filepath), "body": body, "source": "session-observation"}
    for line in front.split("\n"):
        m = re.match(r"^(\w+)\s*:\s*(.+)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            instinct[key] = val

    # Parse confidence as float
    if "confidence" in instinct:
        try:
            instinct["confidence"] = float(instinct["confidence"])
        except ValueError:
            instinct["confidence"] = 0.0

    return instinct


def cmd_status(args):
    """Show all instincts (project + global)."""
    project = detect_project()
    pid = project["id"]

    project_dir = project_obs_dir(pid)
    global_dir = KNC_DIR

    instincts = []

    # Project-scoped instincts
    for d in [project_dir / "instincts" / "personal",
              project_dir / "instincts" / "inherited"]:
        for f in glob_instincts(d):
            inst = parse_instinct(f)
            if inst:
                inst["scope"] = "project"
                instincts.append(inst)

    # Global instincts
    for d in [global_dir / "instincts" / "personal",
              global_dir / "instincts" / "inherited"]:
        for f in glob_instincts(d):
            inst = parse_instinct(f)
            if inst:
                inst["scope"] = "global"
                instincts.append(inst)

    if not instincts:
        print(f"[knc] No instincts found for project '{project['name']}' ({pid})")
        return

    # Group by scope
    scoped = [i for i in instincts if i.get("scope") == "project"]
    global_inst = [i for i in instincts if i.get("scope") == "global"]

    print(f"\n{'='*60}")
    print(f"  Project: {project['name']} ({pid})")
    print(f"{'='*60}")

    if scoped:
        print(f"\n  ── Project-Scoped Instincts ({len(scoped)}) ──")
        for i in sorted(scoped, key=lambda x: -x.get("confidence", 0)):
            c = i.get("confidence", 0)
            badge = "★" if c >= 0.7 else "∙"
            print(f"  {badge} {i.get('id','?')} [{c:.1f}] {i.get('trigger','')[:60]}")

    if global_inst:
        print(f"\n  ── Global Instincts ({len(global_inst)}) ──")
        for i in sorted(global_inst, key=lambda x: -x.get("confidence", 0)):
            c = i.get("confidence", 0)
            badge = "★" if c >= 0.7 else "∙"
            print(f"  {badge} {i.get('id','?')} [{c:.1f}] {i.get('trigger','')[:60]}")

    print()


def cmd_export(args):
    """Export instincts to file."""
    out_file = Path(args.output)
    project = detect_project()
    pid = project["id"] if not args.global_only else "global"

    base = project_obs_dir(pid)
    instincts = []
    for d in [base / "instincts" / "personal", base / "instincts" / "inherited"]:
        for f in glob_instincts(d):
            inst = parse_instinct(f)
            if inst:
                if args.domain and inst.get("domain") != args.domain:
                    continue
                instincts.append({
                    "id": inst.get("id", ""),
                    "trigger": inst.get("trigger", ""),
                    "confidence": inst.get("confidence", 0),
                    "domain": inst.get("domain", ""),
                    "scope": inst.get("scope", "project" if pid != "global" else "global"),
                    "action": inst.get("body", "")[:200],
                })

    out_file.write_text(json.dumps(instincts, indent=2, ensure_ascii=False))
    print(f"[knc] Exported {len(instincts)} instincts to {out_file}")


def cmd_import(args):
    """Import instincts from file."""
    in_file = Path(args.file)
    if not in_file.exists():
        print(f"[knc] ERROR: File not found: {in_file}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(in_file.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        print(f"[knc] ERROR: Expected list or dict", file=sys.stderr)
        sys.exit(1)

    project = detect_project()
    pid = project["id"]
    target_dir = project_obs_dir(pid) / "instincts" / ("inherited" if not args.personal else "personal")
    target_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for inst in data:
        iid = inst.get("id", f"imported-{count}")
        if args.scope:
            inst["scope"] = args.scope
        filepath = target_dir / f"{iid}.yaml"
        front = [f"{k}: {v}" for k, v in inst.items()
                 if k in ("id", "trigger", "confidence", "domain", "source", "scope", "project_id", "project_name")]
        body = f"---\n" + "\n".join(front) + "\n---\n\n# {iid}\n\n## Action\n{inst.get('action', inst.get('trigger', ''))}\n"
        filepath.write_text(body, encoding="utf-8")
        count += 1

    print(f"[knc] Imported {count} instincts to {target_dir}")


def cmd_evolve(args):
    """Cluster related instincts into skills/commands."""
    project = detect_project()
    pid = project["id"]
    project_dir = project_obs_dir(pid)
    instincts = []

    for d in [project_dir / "instincts" / "personal",
              project_dir / "instincts" / "inherited"]:
        for f in glob_instincts(d):
            inst = parse_instinct(f)
            if inst:
                instincts.append(inst)

    if not instincts:
        print(f"[knc] No instincts to evolve for '{project['name']}'")
        return

    # Group by domain
    by_domain = defaultdict(list)
    for i in instincts:
        domain = i.get("domain", "uncategorized")
        by_domain[domain].append(i)

    evolved_dir = project_dir / "evolved"
    evolved_skills = evolved_dir / "skills"
    evolved_commands = evolved_dir / "commands"
    evolved_agents = evolved_dir / "agents"
    evolved_skills.mkdir(parents=True, exist_ok=True)
    evolved_commands.mkdir(parents=True, exist_ok=True)
    evolved_agents.mkdir(parents=True, exist_ok=True)

    for domain, group in by_domain.items():
        high_conf = [i for i in group if i.get("confidence", 0) >= 0.7]
        if len(high_conf) >= 3:
            # Generate a skill from the cluster
            triggers = "\n".join(f"  - {i.get('trigger','?')}" for i in high_conf[:5])
            skill_content = f"""---
name: evolved-{domain}
description: Auto-evolved skill from {len(high_conf)} {domain} instincts
---

# {domain.title()} Practices

## Triggers
{triggers}

## Instincts
{chr(10).join(f'- {i.get("id","?")} [{i.get("confidence",0):.1f}]' for i in high_conf)}
"""
            fname = f"{domain}-practices.md"
            (evolved_skills / fname).write_text(skill_content, encoding="utf-8")
            print(f"  [skill] evolved/{domain}-practices.md ({len(high_conf)} instincts)")

    print(f"[knc] Evolution complete. Check {evolved_dir}")


def cmd_promote(args):
    """Promote project instincts to global scope."""
    project = detect_project()
    pid = project["id"]
    project_dir = project_obs_dir(pid)
    global_dir = KNC_DIR
    global_instincts_dir = global_dir / "instincts" / "personal"
    global_instincts_dir.mkdir(parents=True, exist_ok=True)

    instincts = []
    for f in glob_instincts(project_dir / "instincts" / "personal"):
        inst = parse_instinct(f)
        if inst:
            instincts.append(inst)

    if not instincts:
        print(f"[knc] No project instincts to promote")
        return

    target_id = args.id
    promoted = 0
    for i in instincts:
        if target_id and i.get("id") != target_id:
            continue
        if i.get("confidence", 0) >= 0.8:
            # Copy to global
            src = Path(i["file"])
            dst = global_instincts_dir / src.name
            shutil.copy2(src, dst)
            promoted += 1
            print(f"  Promoted {i.get('id')} [{i.get('confidence',0):.1f}] → global")

    if not target_id and not promoted:
        print("[knc] No instincts met promotion criteria (confidence >= 0.8)")
    elif target_id and not promoted:
        print(f"[knc] Instinct '{target_id}' not found or confidence < 0.8")


def cmd_projects(args):
    """List all known projects and their instinct counts."""
    projects_dir = KNC_DIR / "projects"
    if not projects_dir.exists():
        print("[knc] No projects found")
        return

    print(f"\n{'='*50}")
    print("  Known Projects")
    print(f"{'='*50}")

    total_global = 0
    for d in [KNC_DIR / "instincts" / "personal", KNC_DIR / "instincts" / "inherited"]:
        total_global += len(glob_instincts(d))
    print(f"\n  Global instincts: {total_global}")

    for pdir in sorted(projects_dir.iterdir()):
        if not pdir.is_dir():
            continue
        personal = len(glob_instincts(pdir / "instincts" / "personal"))
        inherited = len(glob_instincts(pdir / "instincts" / "inherited"))
        total = personal + inherited

        meta = pdir / "project.json"
        name = "?"
        if meta.exists():
            try:
                name = json.loads(meta.read_text()).get("name", "?")
            except Exception:
                pass
        print(f"  {pdir.name}  {name:20s}  instincts: {total} (personal={personal}, inherited={inherited})")

    print()


def cmd_prune(args):
    """Delete pending instincts older than TTL."""
    ttl_days = args.days
    project = detect_project()
    pid = project["id"]
    base = project_obs_dir(pid) if not args.global_only else KNC_DIR
    cut = datetime.now(timezone.utc) - timedelta(days=ttl_days)
    pruned = 0

    for f in glob_instincts(base):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        if mtime < cut:
            f.unlink()
            pruned += 1

    print(f"[knc] Pruned {pruned} instincts older than {ttl_days} days")


def main():
    parser = argparse.ArgumentParser(description="continuous-learning Instinct CLI")
    sub = parser.add_subparsers(dest="command")

    p_status = sub.add_parser("status", help="Show instincts")
    p_status.set_defaults(func=cmd_status)

    p_export = sub.add_parser("export", help="Export instincts")
    p_export.add_argument("-o", "--output", default="knc-instincts.json")
    p_export.add_argument("--domain", help="Filter by domain")
    p_export.add_argument("--global-only", action="store_true")
    p_export.set_defaults(func=cmd_export)

    p_import = sub.add_parser("import", help="Import instincts")
    p_import.add_argument("file")
    p_import.add_argument("--personal", action="store_true")
    p_import.add_argument("--scope", choices=["project", "global"])
    p_import.set_defaults(func=cmd_import)

    p_evolve = sub.add_parser("evolve", help="Cluster instincts into skills")
    p_evolve.set_defaults(func=cmd_evolve)

    p_promote = sub.add_parser("promote", help="Promote instincts to global")
    p_promote.add_argument("id", nargs="?", default="")
    p_promote.add_argument("--dry-run", action="store_true")
    p_promote.set_defaults(func=cmd_promote)

    p_projects = sub.add_parser("projects", help="List projects")
    p_projects.set_defaults(func=cmd_projects)

    p_prune = sub.add_parser("prune", help="Prune old instincts")
    p_prune.add_argument("--days", type=int, default=30)
    p_prune.add_argument("--global-only", action="store_true")
    p_prune.set_defaults(func=cmd_prune)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
