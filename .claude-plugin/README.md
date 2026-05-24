# orch Plugin Manifest

`.claude-plugin/` 目录包含插件元数据：

| File | Purpose |
|------|---------|
| `plugin.json` | Claude Code plugin manifest |
| `marketplace.json` | Marketplace listing (DestinyV-marketplace) |
| `PLUGIN_SCHEMA_NOTES.md` | Manifest schema constraints and gotchas |

## Key Facts

- **Agents**: Auto-discovered from `agents/` — not declared in manifest
- **Hooks**: Auto-loaded from `hooks/hooks.json` — not declared in manifest
- **Skills**: 18 skills in `skills/`
- **Commands**: 12 commands in `commands/`

## Validation

```bash
claude plugin validate .claude-plugin/plugin.json
```
