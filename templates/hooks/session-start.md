# SessionStart Hook Template

```javascript
#!/usr/bin/env node
/**
 * SessionStart hook template.
 * Fires when a new session starts (including /compact).
 */
const fs = require('fs');
const path = require('path');

const HOOK_ID = 'session:custom-init';

function main() {
  // Read session context from stdin
  const raw = fs.readFileSync(0, 'utf-8');

  // Your initialization logic here
  // Example: restore project context from saved state
  const stateDir = path.join(process.cwd(), '.claude', 'state');
  if (fs.existsSync(stateDir)) {
    for (const f of fs.readdirSync(stateDir)) {
      if (f.endsWith('.json')) {
        console.log(`[hook] Restored state: ${f}`);
      }
    }
  }
}

try { main(); } catch (_) { /* fail-open */ }
```
