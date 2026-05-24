'use strict';
/**
 * Resolve orch plugin root directory.
 * Tries: CLAUDE_PLUGIN_ROOT → standard install → plugin cache → fallback
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

const PLUGIN_SLUG = 'orch';
const PROBE = path.join('skills', 'package.json');

function resolveRoot(options = {}) {
  const envRoot = options.envRoot !== undefined ? options.envRoot : (process.env.CLAUDE_PLUGIN_ROOT || '');
  if (envRoot && envRoot.trim()) return envRoot.trim();

  const homeDir = options.homeDir || os.homedir();
  const claudeDir = path.join(homeDir, '.claude');

  // Check standard install
  if (fs.existsSync(path.join(claudeDir, PROBE))) return claudeDir;

  // Plugin install
  const pluginDir = path.join(claudeDir, 'plugins', PLUGIN_SLUG);
  if (fs.existsSync(path.join(pluginDir, PROBE))) return pluginDir;

  // Cache fallback
  const cacheDir = path.join(claudeDir, 'plugins', 'cache', PLUGIN_SLUG);
  if (fs.existsSync(cacheDir)) {
    for (const ver of fs.readdirSync(cacheDir)) {
      const candidate = path.join(cacheDir, ver, ver);
      if (fs.existsSync(path.join(candidate, PROBE))) return candidate;
    }
  }

  return claudeDir;
}

module.exports = { resolveRoot };
