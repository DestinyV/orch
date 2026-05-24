'use strict';
/**
 * Hook flags — profile gating for hooks.
 *
 * Environment variables:
 *   SDD_HOOK_PROFILE=minimal|standard|strict  (default: standard)
 *   SDD_DISABLED_HOOKS=comma,separated,hook,ids
 */

const DEFAULT_PROFILE = 'standard';

const PROFILES = {
  minimal: new Set([
    'pre:observe',
    'post:observe',
  ]),
  standard: new Set([
    'pre:observe',
    'post:observe',
    'pre:compact',
    'stop:evaluate',
    'session:init',
    'precompact:state',
  ]),
  strict: new Set([
    'pre:observe',
    'post:observe',
    'pre:compact',
    'stop:evaluate',
    'session:init',
    'precompact:state',
    'stop:workflow-check',
  ]),
};

function resolveProfile() {
  const env = process.env.SDD_HOOK_PROFILE || DEFAULT_PROFILE;
  if (PROFILES[env]) return env;
  return DEFAULT_PROFILE;
}

function resolveDisabled() {
  const raw = process.env.SDD_DISABLED_HOOKS || '';
  return new Set(raw.split(',').map(s => s.trim()).filter(Boolean));
}

function isHookEnabled(hookId, options = {}) {
  const profileName = options.profile || resolveProfile();
  const profileHooks = PROFILES[profileName] || PROFILES[DEFAULT_PROFILE];
  const disabled = options.disabled || resolveDisabled();

  if (disabled.has(hookId)) return false;
  return profileHooks.has(hookId);
}

module.exports = { isHookEnabled, resolveProfile, PROFILES };
