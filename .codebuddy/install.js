#!/usr/bin/env node

/**
 * CodeBuddy installer for orch plugin.
 * Symlinks key adaptation files into CodeBuddy's config directory.
 *
 * Usage: node .codebuddy/install.js [--codebuddy-path <path>]
 */

const fs = require('fs');
const path = require('path');

const PLUGIN_ROOT = path.resolve(__dirname, '..');

const LINKS = {
  // Platform adaptation references
  'skills/using-orch/references/copilot-tools.md': '.codebuddy/tools-mapping.md',
  'AGENTS.md': '.codebuddy/AGENTS.md',

  // Core skills (read-only symlinks or copies)
  'skills/workflow/SKILL.md': '.codebuddy/skills/workflow.md',
  'skills/spec/SKILL.md': '.codebuddy/skills/spec.md',
  'skills/design/SKILL.md': '.codebuddy/skills/design.md',
  'skills/task/SKILL.md': '.codebuddy/skills/task.md',
  'skills/execute/SKILL.md': '.codebuddy/skills/execute.md',
  'skills/test/SKILL.md': '.codebuddy/skills/test.md',
};

function install(cbPath) {
  const targetRoot = cbPath || path.join(PLUGIN_ROOT, '.codebuddy');

  for (const [src, dest] of Object.entries(LINKS)) {
    const srcPath = path.join(PLUGIN_ROOT, src);
    const destPath = path.join(targetRoot, dest);

    if (!fs.existsSync(srcPath)) {
      console.warn(`[orch] SKIP (not found): ${srcPath}`);
      continue;
    }

    fs.mkdirSync(path.dirname(destPath), { recursive: true });

    try {
      // Prefer symlink; fall back to copy on Windows without privilege
      const targetRel = path.relative(path.dirname(destPath), srcPath);
      fs.symlinkSync(targetRel, destPath, 'file');
      console.log(`[orch] LINK: ${dest}`);
    } catch {
      fs.copyFileSync(srcPath, destPath);
      console.log(`[orch] COPY: ${dest}`);
    }
  }

  console.log('[orch] Install complete.');
}

// Parse --codebuddy-path argument
const argIndex = process.argv.indexOf('--codebuddy-path');
const cbPath = argIndex !== -1 ? process.argv[argIndex + 1] : null;
install(cbPath);
