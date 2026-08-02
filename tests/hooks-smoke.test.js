'use strict';
/**
 * 插件 hooks 冒烟测试（Node）
 *
 * 验证核心 hook 基础设施的可运行性：
 *   - stage-contracts.js 导出 8 阶段 STAGE_OUTPUTS + EXEMPT 分离
 *   - stage-gate.js 空 stdin 2s 内 fail-open allow
 *   - hooks.json 有效且含 suggest-compact + observe
 *   - verdict.js 判定函数边界值
 *
 * 运行：node tests/hooks-smoke.test.js
 */
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  [OK]   ${name}`);
  } catch (e) {
    failed++;
    console.log(`  [FAIL] ${name}: ${e.message}`);
  }
}

// 1. stage-contracts
console.log('=== stage-contracts ===');
test('STAGE_OUTPUTS 含 8 阶段 key', () => {
  const sc = require(path.join(ROOT, 'scripts/lib/stage-contracts.js'));
  const keys = Object.keys(sc.STAGE_OUTPUTS);
  assert.deepStrictEqual(
    keys,
    ['0_workflow_control','1_spec_creation','3.5_api_contract','4_code_task','5_code_execute','6_code_test','7_spec_archive','9_knowledge_continuum']
  );
});
test('EXEMPT_SKILLS 无命令名混入', () => {
  const sc = require(path.join(ROOT, 'scripts/lib/stage-contracts.js'));
  const cmds = ['checkpoint','code-review','plan','quality-gate','session-resume','session-save','start-dev'];
  for (const c of cmds) assert.ok(!sc.EXEMPT_SKILLS.includes(c), `EXEMPT_SKILLS 含 ${c}`);
  assert.ok(Array.isArray(sc.EXEMPT_COMMANDS), 'EXEMPT_COMMANDS 存在');
});

// 2. stage-gate 空 stdin
console.log('=== stage-gate ===');
test('空 stdin 2s 内 fail-open allow', () => {
  const start = Date.now();
  const r = spawnSync('node', [path.join(ROOT, 'scripts/hooks/stage-gate.js')], {
    input: '', timeout: 3000, encoding: 'utf8',
  });
  assert.strictEqual(r.status, 0, `exit ${r.status}`);
  const out = JSON.parse(r.stdout.trim());
  assert.strictEqual(out.decision, 'allow');
  assert.ok(Date.now() - start < 6000, `耗时 ${Date.now() - start}ms`);
});

// 3. hooks.json
console.log('=== hooks.json ===');
test('hooks.json 有效且含 suggest-compact + observe', () => {
  const hooks = JSON.parse(fs.readFileSync(path.join(ROOT, 'hooks/hooks.json'), 'utf8'));
  const ids = [];
  for (const [ev, entries] of Object.entries(hooks.hooks)) {
    for (const e of entries) ids.push(e.id || '');
  }
  assert.ok(ids.includes('pre:compact'), '缺 pre:compact');
  assert.ok(ids.includes('pre:observe') && ids.includes('post:observe'), '缺 observe');
});

// 4. verdict.js
console.log('=== verdict.js ===');
test('judgeCoverage 边界值', () => {
  const v = require(path.join(ROOT, 'scripts/lib/verdict.js'));
  assert.strictEqual(v.judgeCoverage(85, 87), 'VERIFIED');
  assert.strictEqual(v.judgeCoverage(90, 72), 'PARTIAL');
});
test('judgeAutoResolve 规则自决 + 白名单人工', () => {
  const v = require(path.join(ROOT, 'scripts/lib/verdict.js'));
  assert.strictEqual(v.judgeAutoResolve('test failure'), 'auto-resolve');
  assert.strictEqual(v.judgeAutoResolve('requirement conflict'), 'pause-for-human');
});

// 5. worktree.js
console.log('=== worktree.js ===');
test('worktree.js 导出 5 子命令函数 + parseWorktreePorcelain', () => {
  const w = require(path.join(ROOT, 'scripts/worktree.js'));
  for (const fn of ['create', 'merge', 'cleanup', 'list', 'status']) {
    assert.strictEqual(typeof w[fn], 'function', `缺导出 ${fn}`);
  }
  assert.strictEqual(typeof w.parseWorktreePorcelain, 'function', '缺导出 parseWorktreePorcelain');
});
test('无参运行返回码 2 + Usage 提示', () => {
  const r = spawnSync('node', [path.join(ROOT, 'scripts/worktree.js')], { encoding: 'utf8' });
  assert.strictEqual(r.status, 2, `exit ${r.status}`);
  assert.ok(/Usage/i.test(r.stdout + r.stderr), '含 Usage');
});

console.log(`\nSummary: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
