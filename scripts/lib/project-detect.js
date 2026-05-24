'use strict';
/**
 * Project detection for orch.
 * Detects tech stack, frameworks, test frameworks, and package manager.
 */
const fs = require('fs');
const path = require('path');

function detectProject(rootDir) {
  const result = {
    name: path.basename(rootDir),
    language: 'unknown',
    framework: 'unknown',
    testFramework: 'unknown',
    packageManager: 'unknown',
    hasTypeScript: false,
    hasDatabase: false,
  };

  const files = [];
  try { files.push(...fs.readdirSync(rootDir)); } catch (_) {}

  // Package manager
  if (files.includes('package.json')) result.packageManager = 'npm';
  if (files.includes('yarn.lock')) result.packageManager = 'yarn';
  if (files.includes('pnpm-lock.yaml')) result.packageManager = 'pnpm';
  if (files.includes('go.mod')) result.packageManager = 'go';
  if (files.includes('Cargo.toml')) result.packageManager = 'cargo';
  if (files.includes('pom.xml') || files.includes('build.gradle')) result.packageManager = 'maven';

  // Language
  if (files.includes('tsconfig.json')) { result.language = 'typescript'; result.hasTypeScript = true; }
  else if (files.includes('pyproject.toml') || files.includes('requirements.txt')) result.language = 'python';
  else if (files.includes('go.mod')) result.language = 'go';
  else if (files.includes('Cargo.toml')) result.language = 'rust';

  // Test framework
  if (files.includes('vitest.config.ts') || files.includes('vitest.config.js')) result.testFramework = 'vitest';
  else if (files.includes('jest.config.ts') || files.includes('jest.config.js')) result.testFramework = 'jest';
  else if (files.includes('pytest.ini') || files.includes('pyproject.toml')) result.testFramework = 'pytest';

  // Database indicators
  if (files.includes('prisma') || files.includes('schema.prisma') ||
      files.some(f => f.includes('migration') || f.includes('sequelize') || f.includes('typeorm'))) {
    result.hasDatabase = true;
  }

  return result;
}

module.exports = { detectProject };
