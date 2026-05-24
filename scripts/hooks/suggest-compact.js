#!/usr/bin/env node
/**
 * PreToolUse(Edit|Write) hook — suggest /compact at logical boundaries.
 * Triggers after N Edit/Write operations to prevent context pressure.
 */
const fs = require('fs');
const path = require('path');

const THRESHOLD = 40; // operations before suggesting
const COUNTER_FILE = path.join(process.cwd(), '.claude', '.compact-counter');

function main() {
  const raw = fs.readFileSync(0, 'utf-8');

  let count = 0;
  try {
    count = parseInt(fs.readFileSync(COUNTER_FILE, 'utf-8')) || 0;
  } catch (_) { /* first run */ }

  count++;
  try {
    fs.mkdirSync(path.dirname(COUNTER_FILE), { recursive: true });
    fs.writeFileSync(COUNTER_FILE, String(count));
  } catch (_) { /* ignore write failures */ }

  if (count >= THRESHOLD) {
    console.error('[orch] Context pressure detected:');
    console.error(`  ${count} Edit/Write operations since last /compact.`);
    console.error('  Consider running /compact to free context memory.');
    // Reset counter after suggesting
    try { fs.unlinkSync(COUNTER_FILE); } catch (_) { /* ok */ }
  }
}

try { main(); } catch (_) { /* fail-open */ }
