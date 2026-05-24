# PreToolUse Hook Template

```javascript
#!/usr/bin/env node
/**
 * PreToolUse hook template.
 * Fires before each tool call matching the specified matcher.
 */
const fs = require('fs');
const path = require('path');

const HOOK_ID = 'pre:custom-hook';

function main() {
  // Read stdin (hook JSON payload)
  const raw = fs.readFileSync(0, 'utf-8');
  const data = JSON.parse(raw);

  const toolName = data.tool_name || data.tool || 'unknown';

  // Your hook logic here
  if (toolName === 'Edit') {
    // Example: validate edit target
    const target = data.tool_input?.file_path || '';
    if (target.includes('node_modules')) {
      console.log('[hook] Skipping edit in node_modules');
    }
  }
}

try { main(); } catch (_) { /* fail-open */ }
```
