'use strict';
/**
 * Hook runner — safe hook execution with timeout and fail-open.
 * Usage: node scripts/lib/hook-runner.js <hook-script-path> [args...]
 *
 * Features:
 * - Resolves CLAUDE_PLUGIN_ROOT for skill script paths
 * - 30-second safety timeout
 * - fail-open: any error exits 0 with raw stdin passthrough
 * - Path traversal protection
 * - Windows compatibility
 */
const fs = require('fs');
const path = require('path');
const cp = require('child_process');

const TIMEOUT_MS = 30000;
const ROOT_VAR = process.env.CLAUDE_PLUGIN_ROOT || '';

function resolveRoot() {
  if (ROOT_VAR && ROOT_VAR.trim()) return ROOT_VAR.trim();

  const homeDir = process.env.HOME || process.env.USERPROFILE || '';
  const claudeDir = path.join(homeDir, '.claude');
  const probe = path.join('scripts', 'lib', 'hook-runner.js');

  // Standard install
  if (fs.existsSync(path.join(claudeDir, probe))) return claudeDir;

  // Plugin install
  const pluginDir = path.join(claudeDir, 'plugins', 'orch');
  if (fs.existsSync(path.join(pluginDir, probe))) return pluginDir;

  // Plugin cache fallback
  const cacheDir = path.join(claudeDir, 'plugins', 'cache', 'orch');
  if (fs.existsSync(cacheDir)) {
    for (const ver of fs.readdirSync(cacheDir)) {
      const candidate = path.join(cacheDir, ver, ver);
      if (fs.existsSync(path.join(candidate, probe))) return candidate;
    }
  }

  return claudeDir;
}

function isPathSafe(targetPath, rootDir) {
  const resolved = path.resolve(targetPath);
  return resolved.startsWith(rootDir + path.sep) || resolved === rootDir;
}

function runHook(hookPath, args) {
  const rootDir = resolveRoot();
  const target = path.resolve(rootDir, hookPath);

  if (!fs.existsSync(target)) {
    console.error('[hook-runner] Script not found:', target);
    return 0;
  }

  if (!isPathSafe(target, rootDir)) {
    console.error('[hook-runner] Path traversal blocked:', target);
    return 0;
  }

  try {
    const raw = fs.readFileSync(0, 'utf-8'); // stdin

    const result = cp.spawnSync(process.execPath, [target, ...args], {
      input: raw,
      timeout: TIMEOUT_MS,
      windowsHide: true,
      maxBuffer: 1024 * 1024,
    });

    if (result.status !== null && result.status !== 0) {
      console.error(`[hook-runner] Hook exited ${result.status}:`, hookPath);
    }
    if (result.stdout) process.stdout.write(result.stdout.toString());
    if (result.stderr) process.stderr.write(result.stderr.toString());
    return 0;
  } catch (err) {
    console.error('[hook-runner] Error:', err.message);
    return 0;
  }
}

if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error('Usage: node hook-runner.js <hook-script> [args...]');
    process.exit(0);
  }
  process.exit(runHook(args[0], args.slice(1)));
}

module.exports = { runHook, resolveRoot };
