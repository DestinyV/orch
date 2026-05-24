#!/usr/bin/env node
/**
 * PreCompact hook.
 * Saves workflow state before context compaction to prevent progress loss.
 */
const fs = require('fs');
const path = require('path');
const { isHookEnabled } = require('../lib/hook-flags');

const HOOK_ID = 'precompact:state';

function saveStateBeforeCompact(rootDir) {
  const specDev = path.join(rootDir, 'orch-spec');
  if (!fs.existsSync(specDev)) return;

  const entries = fs.readdirSync(specDev);
  for (const entry of entries) {
    const stateFile = path.join(specDev, entry, '.workflow-state.json');
    if (!fs.existsSync(stateFile)) continue;

    try {
      const state = JSON.parse(fs.readFileSync(stateFile, 'utf-8'));
      if (state.status === 'in_progress') {
        // Save a compact checkpoint
        const checkpoint = Object.assign({}, state, {
          _compact_checkpoint: new Date().toISOString(),
        });
        fs.writeFileSync(stateFile + '.compact', JSON.stringify(checkpoint, null, 2));
      }
    } catch (_) { /* ignore */ }
  }
}

function main() {
  if (!isHookEnabled(HOOK_ID)) return;
  const root = process.env.CLAUDE_PLUGIN_ROOT || process.cwd();
  saveStateBeforeCompact(root);
}

try { main(); } catch (_) { /* fail-open */ }
