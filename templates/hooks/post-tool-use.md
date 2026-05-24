# PostToolUse Hook Template

```javascript
#!/usr/bin/env node
/**
 * PostToolUse hook template.
 * Fires after each tool call completes.
 */
const fs = require('fs');
const path = require('path');

const HOOK_ID = 'post:custom-hook';

function main() {
  const raw = fs.readFileSync(0, 'utf-8');
  const data = JSON.parse(raw);

  const toolName = data.tool_name || data.tool || 'unknown';
  const output = data.tool_response || data.output || '';

  // Your hook logic here
  if (toolName === 'Bash') {
    // Example: capture command output for analysis
    const summary = output.substring(0, 200);
    console.log(`[hook] Bash completed: ${summary.length} chars`);
  }
}

try { main(); } catch (_) { /* fail-open */ }
```
