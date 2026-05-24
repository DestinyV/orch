# Plugin Manifest Schema Notes

## Critical Constraints

### `agents` Field: DO NOT ADD

Agent `.md` files under `agents/` are **auto-discovered by convention**. Adding an `"agents"` field to `plugin.json` will cause:

```
agents: Invalid input
```

### `hooks` Field: DO NOT ADD

Claude Code v2.1+ **auto-loads** `hooks/hooks.json` by convention. Declaring it also in `plugin.json` causes:

```
Duplicate hooks file detected
```

### `mcpServers`: Keep Empty Object

```json
"mcpServers": {}
```

Prevents root `.mcp.json` auto-discovery during Claude plugin installs.

### Field Shape

- `skills` and `commands` must be arrays (even for single entries)
- `version` is required
- Strings are not accepted in place of arrays

## Known-Good Structure

```json
{
  "version": "2.21.0",
  "skills": ["./skills/"],
  "commands": ["./commands/"],
  "mcpServers": {}
}
```

## Validation

```bash
claude plugin validate .claude-plugin/plugin.json
```
