#!/usr/bin/env node
/**
 * SessionStart hook.
 * Checks for incomplete workflows and restores state.
 */
const fs = require('fs');
const path = require('path');
const { isHookEnabled } = require('../lib/hook-flags');

const HOOK_ID = 'session:init';

function checkWorkflowState(rootDir) {
  const specDev = path.join(rootDir, 'spec-dev');
  if (!fs.existsSync(specDev)) return;

  const entries = fs.readdirSync(specDev);
  for (const entry of entries) {
    const stateFile = path.join(specDev, entry, '.workflow-state.json');
    if (!fs.existsSync(stateFile)) continue;

    try {
      const state = JSON.parse(fs.readFileSync(stateFile, 'utf-8'));
      if (state.status === 'in_progress') {
        console.log(`[orch] 工作流进行中: ${entry} (阶段: ${state.current_stage})`);
        console.log(`[orch] 继续请运行: /start-dev`);
      }
    } catch (_) { /* ignore */ }
  }
}

function main() {
  if (!isHookEnabled(HOOK_ID)) return;

  const root = process.env.CLAUDE_PLUGIN_ROOT
    || process.env.INIT_CWD
    || process.cwd();

  checkWorkflowState(root);
}

try { main(); } catch (_) { /* fail-open */ }
