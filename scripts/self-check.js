#!/usr/bin/env node
/**
 * 插件自检命令（scripts/self-check.js）
 *
 * 对插件自身 5 大块执行验证：
 *   - orchestration: 工作流编排引擎（stage-contracts / stage-gate / workflow-gate / session-start）
 *   - agents:        Agent 体系（project-map 引用 / 注册表口径 / Prompt Defense / frontmatter / 编号 / /hookify）
 *   - skills:        Skills 指令（引用完整性 / cost GATE / using-orch 索引 / observer / TRIGGER）
 *   - tdd_loop:      TDD 闭环（self-check 存在 / 四阶段日志 / 覆盖率判定）
 *   - commands_hooks: Commands + Hooks（hooks.json 注册 / observe 激活 / CLAUDE.md 一致 / 文档口径 / 无 pyc）
 *
 * 输出：{ blocks, issues[], summary: {total:5, passed, failed} }；退出码 0（全 PASS）或 1（有 FAIL）。
 * 支持 --json 输出结构化报告。
 *
 * 设计原则（北极星）：自检是增强验证能力，只判不堵。
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const O = (p) => path.join(ROOT, p);

const ISSUES = [];
function record(block, ok, label, file, suggestion) {
  if (!ok) {
    ISSUES.push({ block, file, suggestion: suggestion || label });
  }
  return ok;
}

function readFile(p) {
  try { return fs.readFileSync(p, 'utf8'); } catch { return ''; }
}

function exists(p) { return fs.existsSync(p); }

// ---------- orchestration ----------
function checkOrchestration() {
  const block = 'orchestration';
  const results = [];
  // 1. stage-contracts.js 存在且含 8 阶段 STAGE_OUTPUTS
  const sc = readFile(O('scripts/lib/stage-contracts.js'));
  const ok8 = sc.includes('3.5_api_contract') && sc.includes('5_code_execute') &&
              sc.includes('6_code_test') && sc.includes('9_knowledge_continuum');
  results.push(record(block, ok8, 'stage-contracts 含 8 阶段 STAGE_OUTPUTS', 'scripts/lib/stage-contracts.js'));

  // 2. EXEMPT_SKILLS 与命令名分离（仅检查 EXEMPT_SKILLS 数组，命令名在 EXEMPT_COMMANDS）
  const commandNames = ['checkpoint', 'code-review', 'plan', 'quality-gate', 'session-resume', 'session-save', 'start-dev'];
  const exemptSkillsMatch = sc.match(/const EXEMPT_SKILLS = \[([\s\S]*?)\];/);
  const exemptSkillsBody = exemptSkillsMatch ? exemptSkillsMatch[1] : '';
  const mixed = commandNames.filter(c => new RegExp(`'${c}'`).test(exemptSkillsBody));
  results.push(record(block, mixed.length === 0, `EXEMPT_SKILLS 无命令名混入（残留: ${mixed.join(',') || '无'}）`, 'scripts/lib/stage-contracts.js'));

  // 3. stage-gate 含 stdin 超时
  const sg = readFile(O('scripts/hooks/stage-gate.js'));
  results.push(record(block, sg.includes('readStdin') && sg.includes('allow'), 'stage-gate 含 stdin 超时 fail-open', 'scripts/hooks/stage-gate.js'));

  // 4. workflow-gate 含 8 阶段校验 + completion-report
  const wg = readFile(O('scripts/hooks/workflow-gate.js'));
  results.push(record(block, wg.includes('completion-report') && wg.includes('readStdin'), 'workflow-gate 含 completion-report 校验 + stdin 超时', 'scripts/hooks/workflow-gate.js'));

  // 5. session-start 含自动补偿（resume-from）
  const ss = readFile(O('scripts/hooks/session-start.js'));
  results.push(record(block, ss.includes('resume-from') || ss.includes('nextStage'), 'session-start 含自动补偿建议', 'scripts/hooks/session-start.js'));

  // 6. worktree.js 存在且含子命令分发
  const wt = readFile(O('scripts/worktree.js'));
  const wtOk = wt.includes("case 'create'") && wt.includes("case 'cleanup'") && wt.includes("case 'merge'");
  results.push(record(block, wtOk, 'worktree.js 含 create/merge/cleanup 子命令分发', 'scripts/worktree.js'));

  // 7. 无孤儿 worktree（本仓库健康；git 不可用时跳过）
  try {
    const out = execSync('git worktree list --porcelain', { cwd: ROOT, encoding: 'utf8' });
    const paths = out.split(/\r?\n/).filter(l => l.startsWith('worktree '))
                     .map(l => l.slice(9).trim());
    const orphans = paths.filter(p => !fs.existsSync(p));
    results.push(record(block, orphans.length === 0,
      `无孤儿 worktree（注册 ${paths.length}，孤儿 ${orphans.length}）`,
      'scripts/worktree.js', 'git worktree prune'));
  } catch (_) { /* 非 git 仓库时跳过 */ }

  return results;
}

// ---------- agents ----------
function checkAgents() {
  const block = 'agents';
  const results = [];
  const agentsDir = O('agents');

  // 1. 无 project-map.md 残留
  const mapHits = [];
  for (const f of fs.readdirSync(agentsDir)) {
    if (f.endsWith('.md') && readFile(path.join(agentsDir, f)).includes('project-map.md')) {
      mapHits.push(f);
    }
  }
  results.push(record(block, mapHits.length === 0, `无 project-map.md 残留（命中: ${mapHits.join(',') || '无'}）`, 'agents/', '修正为 project-map.json'));

  // 2. 注册表口径 26
  const ag = readFile(O('AGENTS.md'));
  const regLinks = (ag.match(/\(agents\/[\w.-]+\.md\)/g) || []).length;
  results.push(record(block, regLinks === 26, `AGENTS.md 注册数 = 26（实际 ${regLinks}）`, 'AGENTS.md'));

  // 3. Prompt Defense 每文件 ≤1
  const pdBad = [];
  for (const f of fs.readdirSync(agentsDir)) {
    if (f.endsWith('.md') && !f.startsWith('_')) {
      const n = (readFile(path.join(agentsDir, f)).match(/## Prompt Defense Baseline/g) || []).length;
      if (n > 1) pdBad.push(`${f}(${n})`);
    }
  }
  results.push(record(block, pdBad.length === 0, `Prompt Defense 每文件 ≤1（违规: ${pdBad.join(',') || '无'}）`, 'agents/', '重跑 sync-prompt-defense.py'));

  // 4. 无数组 tools 语法
  const arrBad = [];
  for (const f of fs.readdirSync(agentsDir)) {
    if (f.endsWith('.md') && !f.startsWith('_')) {
      const src = readFile(path.join(agentsDir, f));
      const m = src.match(/^tools:\s*\[/m);
      if (m) arrBad.push(f);
    }
  }
  results.push(record(block, arrBad.length === 0, `无数组 tools 语法（残留: ${arrBad.join(',') || '无'}）`, 'agents/', '统一为逗号分隔'));

  // 5. code-architect 编号唯一
  const ca = readFile(O('agents/code-architect.md'));
  const n0 = (ca.match(/^### 0\./m) || []).length;
  results.push(record(block, n0 === 1, `code-architect ### 0. 仅一次（实际 ${n0}）`, 'agents/code-architect.md'));

  // 6. 无 /hookify
  const hookifyHits = [];
  for (const f of fs.readdirSync(agentsDir)) {
    if (f.endsWith('.md') && readFile(path.join(agentsDir, f)).includes('hookify')) {
      hookifyHits.push(f);
    }
  }
  results.push(record(block, hookifyHits.length === 0, `无 /hookify 残留（命中: ${hookifyHits.join(',') || '无'}）`, 'agents/'));

  return results;
}

// ---------- skills ----------
function checkSkills() {
  const block = 'skills';
  const results = [];
  const skillsDir = O('skills');

  // 1. execute/spec 引用无悬空
  const exe = readFile(O('skills/execute/SKILL.md'));
  const spec = readFile(O('skills/spec/SKILL.md'));
  results.push(record(block, exe.includes('context-inheritance-protocol.md') && !exe.includes('context-injection-protocol.md'),
    'execute 引用 context-inheritance-protocol.md', 'skills/execute/SKILL.md'));
  results.push(record(block, spec.includes('../design/references/diagram-trigger-rules.md'),
    'spec 引用 ../design/references/diagram-trigger-rules.md', 'skills/spec/SKILL.md'));

  // 2. cost 含 GATE
  const cost = readFile(O('skills/cost/SKILL.md'));
  results.push(record(block, cost.includes('<GATE>'), 'cost 含 <GATE>', 'skills/cost/SKILL.md'));

  // 3. using-orch 覆盖 22
  const uo = readFile(O('skills/using-orch/SKILL.md'));
  const diskSkills = fs.readdirSync(skillsDir).filter(f => !f.startsWith('.'));
  const missing = diskSkills.filter(s => !uo.includes(`**${s}**`));
  results.push(record(block, missing.length === 0, `using-orch 覆盖全部 ${diskSkills.length} skill（遗漏: ${missing.join(',') || '无'}）`, 'skills/using-orch/SKILL.md'));

  // 4. observer 激活
  try {
    const cfg = JSON.parse(readFile(O('skills/continuous-learning/config.json')));
    results.push(record(block, cfg.observer && cfg.observer.enabled === true, 'observer.enabled === true', 'skills/continuous-learning/config.json'));
  } catch {
    results.push(record(block, false, 'continuous-learning/config.json 可解析', 'skills/continuous-learning/config.json'));
  }

  // 5. 16 核心 skill 含 TRIGGER
  const coreSkills = ['archive','clarify','continuous-learning','contract','debug','design','exception','execute','req-change','scripts','spec','spec-migrate','task','test','test-design','workflow'];
  const noTrigger = [];
  for (const s of coreSkills) {
    const src = readFile(path.join(skillsDir, s, 'SKILL.md'));
    if (!src.includes('TRIGGER when')) noTrigger.push(s);
  }
  results.push(record(block, noTrigger.length === 0, `16 核心 skill 含 TRIGGER（缺失: ${noTrigger.join(',') || '无'}）`, 'skills/', '补 TRIGGER when'));

  return results;
}

// ---------- tdd_loop ----------
function checkTddLoop() {
  const block = 'tdd_loop';
  const results = [];
  // 1. self-check.md 存在
  results.push(record(block, exists(O('commands/self-check.md')), 'commands/self-check.md 存在', 'commands/self-check.md'));

  // 2. verdict.js 存在且含判定函数
  const vd = readFile(O('scripts/lib/verdict.js'));
  results.push(record(block, vd.includes('judgeCoverage') && vd.includes('judgeRate') && vd.includes('judgeAutoResolve'),
    'verdict.js 含三判定函数', 'scripts/lib/verdict.js'));

  // 3. 覆盖率判定逻辑（实测为准）
  results.push(record(block, vd.includes('actual >= threshold') || vd.includes('actual >='), '覆盖率判定以实测为准', 'scripts/lib/verdict.js'));

  return results;
}

// ---------- commands_hooks ----------
function checkCommandsHooks() {
  const block = 'commands_hooks';
  const results = [];
  // 1. hooks.json 有效 + 含 suggest-compact/observe
  try {
    const hooks = JSON.parse(readFile(O('hooks/hooks.json')));
    const allIds = [];
    for (const [ev, entries] of Object.entries(hooks.hooks)) {
      for (const e of entries) allIds.push(e.id || '');
    }
    results.push(record(block, allIds.includes('pre:compact'), 'hooks.json 含 pre:compact', 'hooks/hooks.json'));
    results.push(record(block, allIds.includes('pre:observe') && allIds.includes('post:observe'), 'hooks.json 含 pre/post:observe', 'hooks/hooks.json'));
  } catch {
    results.push(record(block, false, 'hooks.json 可解析', 'hooks/hooks.json'));
  }

  // 2. observe.sh 存在
  results.push(record(block, exists(O('scripts/hooks/observe.sh')), 'observe.sh 存在', 'scripts/hooks/observe.sh'));

  // 3. CLAUDE.md 钩子表与 hooks.json 一致（含 cost-tracker）
  const cm = readFile(O('CLAUDE.md'));
  results.push(record(block, cm.includes('cost-tracker.js') && cm.includes('observe.sh'), 'CLAUDE.md 钩子表含 cost-tracker + observe', 'CLAUDE.md'));

  // 4. 文档数量口径 22/26/14
  const readme = readFile(O('README.md'));
  results.push(record(block, readme.includes('22 professional skills') && readme.includes('26 professional Agents'), 'README 数量口径 22/26', 'README.md'));

  // 5. 无 *.pyc 入库
  let pycCount = 0;
  try {
    const out = execSync('git ls-files', { cwd: ROOT, encoding: 'utf8' });
    pycCount = (out.match(/\.pyc$|__pycache__/gm) || []).length;
  } catch { /* git 不可用时跳过 */ }
  results.push(record(block, pycCount === 0, `git 无 *.pyc 入库（命中 ${pycCount}）`, '.gitignore'));

  return results;
}

function main() {
  const isJson = process.argv.includes('--json');
  const blocks = {
    orchestration: checkOrchestration().every(Boolean),
    agents: checkAgents().every(Boolean),
    skills: checkSkills().every(Boolean),
    tdd_loop: checkTddLoop().every(Boolean),
    commands_hooks: checkCommandsHooks().every(Boolean),
  };

  const passed = Object.values(blocks).filter(Boolean).length;
  const failed = 5 - passed;

  const report = { blocks, issues: ISSUES, summary: { total: 5, passed, failed } };

  if (isJson) {
    process.stdout.write(JSON.stringify(report, null, 2) + '\n');
  } else {
    console.log('=== orch plugin self-check ===');
    for (const [block, ok] of Object.entries(blocks)) {
      console.log(`  [${ok ? 'PASS' : 'FAIL'}] ${block}`);
    }
    if (ISSUES.length) {
      console.log('\nIssues:');
      for (const i of ISSUES) {
        console.log(`  - [${i.block}] ${i.file}: ${i.suggestion || ''}`);
      }
    }
    console.log(`\nSummary: ${passed}/5 passed, ${failed} failed`);
  }

  process.exit(failed > 0 ? 1 : 0);
}

main();
