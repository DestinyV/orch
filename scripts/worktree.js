'use strict';
/**
 * Git Worktree 生命周期管理脚本
 *
 * 统一封装 execute 阶段 worktree 的创建/合并/清理/列出/状态，消除散落在
 * skills/execute/SKILL.md 及 references 中的 16+ 处内联 git 命令。
 *
 * 子命令：
 *   create  {task-id} {branch} [--name <short>] [--base <ref>] [--fallback-branch <name>]
 *   merge   {task-id} {target-branch} [--dry-run]
 *   cleanup [--target <branch>] [--dry-run] [--force]
 *   list    [--json]
 *   status  [--json]
 *
 * 退出码：0 成功 / 1 完成但有警示 / 2 用法错误
 *
 * 北极星原则：脚本是护栏（自动化可靠性保障），不限制模型能力——模型仍可自由使用
 * 原生 git 命令，脚本作为辅助与兜底。安全：git 操作统一 execFileSync（无 shell 防注入）。
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const DEFAULT_TIMEOUT_MS = 20000;
const WORKTREES_DIR = path.join('.claude', 'worktrees');

// ---- 参数解析 ----
function parseFlags(argv) {
  const json = argv.includes('--json');
  const dryRun = argv.includes('--dry-run');
  const force = argv.includes('--force');
  const pos = argv.filter(a => !a.startsWith('--'));
  const opt = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--name') opt.name = argv[++i];
    if (argv[i] === '--base') opt.base = argv[++i];
    if (argv[i] === '--target') opt.target = argv[++i];
    if (argv[i] === '--fallback-branch') opt.fallbackBranch = argv[++i];
  }
  return { json, dryRun, force, pos, opt };
}

// ---- git 执行（无 shell，防注入）----
function git(args, opts = {}) {
  try {
    const stdout = execFileSync('git', args, {
      cwd: opts.cwd,
      encoding: 'utf8',
      timeout: opts.timeout || DEFAULT_TIMEOUT_MS,
      windowsHide: true,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    return { ok: true, status: 0, stdout: String(stdout).trim(), stderr: '' };
  } catch (err) {
    return {
      ok: false,
      status: typeof err.status === 'number' ? err.status : 1,
      stdout: String(err.stdout || '').trim(),
      stderr: String(err.stderr || err.message || err).trim(),
    };
  }
}

function repoRoot() {
  const r = git(['rev-parse', '--show-toplevel'], { cwd: process.cwd() });
  return r.ok ? r.stdout : null;
}

function currentBranch() {
  const r = git(['branch', '--show-current']);
  return r.ok ? r.stdout : null;
}

// ---- 解析 `git worktree list --porcelain` ----
// 格式：
//   worktree <path>
//   HEAD <sha>
//   branch refs/heads/<name>      ← detached 时无此行
function parseWorktreePorcelain(out) {
  const entries = [];
  let cur = null;
  for (const raw of String(out).split(/\r?\n/)) {
    const line = raw.trim();
    if (!line) { cur = null; continue; }
    if (line.startsWith('worktree ')) {
      cur = { path: line.slice(9).trim() };
      entries.push(cur);
    } else if (line.startsWith('HEAD ')) {
      if (cur) cur.head = line.slice(5).trim();
    } else if (line.startsWith('branch ')) {
      if (cur) cur.branch = line.slice(7).trim().replace('refs/heads/', '');
    }
  }
  return entries;
}

// ---- 输出 ----
function output(result, flags) {
  if (flags.json) {
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
    return;
  }
  for (const w of result.warnings || []) console.log(`  [WARN] ${w}`);
  for (const e of result.errors || []) console.log(`  [ERR]  ${e}`);
  console.log(`  [${result.ok ? 'OK' : 'FAIL'}] ${result.message || result.command}`);
}

// ---- task-id / name 合法性（防路径穿越）----
const SAFE_ID = /^[A-Za-z0-9_.-]+$/;
// 分支名允许斜杠（sdd/<abbrev>/<n>-<desc>），其余同 SAFE_ID
const SAFE_BRANCH = /^[A-Za-z0-9_.\/-]+$/;

function validateId(id) {
  return !!id && SAFE_ID.test(id);
}

// ============ create ============
function cmdCreate(argv) {
  const flags = parseFlags(argv);
  const [taskId, branch] = flags.pos;
  const name = flags.opt.name || (branch || '').split('/').pop() || taskId;
  const base = flags.opt.base || currentBranch() || 'HEAD';
  const fallbackBranch = flags.opt.fallbackBranch || `${taskId}-${name}`;

  const result = { command: 'create', ok: false, exitCode: 0, taskId, name, warnings: [], errors: [] };

  // 参数校验
  if (!taskId || !branch) return usage(argv, 'create 需要 {task-id} {branch}');
  if (!validateId(taskId) || !validateId(name)) {
    result.errors.push('task-id/name 仅允许字母数字及 _ . -（防路径穿越）');
    result.exitCode = 2;
    result.ok = false;
    return finish(result, flags);
  }

  const root = repoRoot();
  if (!root) {
    result.errors.push('当前目录不是 git 仓库');
    result.exitCode = 1;
    result.ok = false;
    return finish(result, flags);
  }
  const dir = path.join(root, WORKTREES_DIR, `${taskId}-${name}`);

  // 5 步重试协议（对应 SKILL.md 创建协议）
  let attempt = 0;
  let lastErr = '';
  for (attempt = 1; attempt <= 4; attempt++) {
    // 尝试 add（branch 不存在则 -b 新建）
    const branchExists = git(['rev-parse', '--verify', `refs/heads/${branch}`]).ok;
    const addArgs = branchExists
      ? ['worktree', 'add', dir, branch]
      : ['worktree', 'add', '-b', branch, dir, base];
    let r = git(addArgs);

    // 失败 → 清理目录重试
    if (!r.ok && attempt < 4) {
      lastErr = r.stderr;
      try { fs.rmSync(dir, { recursive: true, force: true }); } catch (_) {}
      continue;
    }
    if (r.ok) break;
    lastErr = r.stderr;

    // attempt 3/4：尝试 fallback 分支从 HEAD
    if (attempt >= 3) {
      try { fs.rmSync(dir, { recursive: true, force: true }); } catch (_) {}
      if (attempt === 4) git(['worktree', 'prune']);
      r = git(['worktree', 'add', '-b', fallbackBranch, dir, 'HEAD']);
      if (r.ok) break;
      lastErr = r.stderr;
    }
  }

  if (attempt <= 4 && git(['rev-parse', '--verify', dir]).ok !== true && fs.existsSync(dir)) {
    // 目录已创建即视为成功（verify 对路径不一定有效）
    result.ok = true;
  } else if (fs.existsSync(dir) || (attempt <= 4)) {
    result.ok = true;
  }

  if (result.ok) {
    result.message = `worktree 创建成功: ${dir} (branch: ${branch})`;
    result.attempt = attempt;
    result.worktree = { path: dir, branch };
  } else {
    // attempt 5：降级（子代理同目录，仍并行），返回码 1
    result.ok = false;
    result.exitCode = 1;
    result.message = 'worktree 创建失败，子代理在同目录工作（仍保持并行）';
    result.warnings.push('worktree 创建失败，子代理在同目录工作（仍保持并行）。禁止降级到主上下文串行。');
    if (lastErr) result.errors.push(lastErr);
  }
  return finish(result, flags);
}

// ============ merge ============
function cmdMerge(argv) {
  const flags = parseFlags(argv);
  const [taskId, target] = flags.pos;
  const result = { command: 'merge', ok: false, exitCode: 0, taskId, target, commits: [], warnings: [], errors: [] };

  if (!taskId || !target) return usage(argv, 'merge 需要 {task-id} {target-branch}');
  if (!validateId(taskId)) {
    result.errors.push('task-id 非法');
    result.exitCode = 2;
    result.ok = false;
    return finish(result, flags);
  }

  const root = repoRoot();
  if (!root) {
    result.errors.push('当前目录不是 git 仓库');
    result.exitCode = 1;
    return finish(result, flags);
  }

  // 定位 worktree 分支
  const wts = parseWorktreePorcelain(git(['worktree', 'list', '--porcelain']).stdout);
  const matches = wts.filter(w => w.branch && path.basename(w.path).startsWith(`${taskId}-`));
  const exact = flags.opt.name ? matches.filter(w => path.basename(w.path) === `${taskId}-${flags.opt.name}`) : matches;
  const wt = exact[0] || matches[0];
  if (!wt || !wt.branch) {
    result.errors.push(`未找到 task-id=${taskId} 的 worktree/分支`);
    result.exitCode = 1;
    result.ok = false;
    return finish(result, flags);
  }
  const branch = wt.branch;

  // 校验 target
  if (!git(['rev-parse', '--verify', `refs/heads/${target}`]).ok) {
    result.errors.push(`目标分支不存在: ${target}`);
    result.exitCode = 1;
    result.ok = false;
    return finish(result, flags);
  }

  // 取待 cherry-pick 的 commit 序列（旧→新）
  const logR = git(['log', '--reverse', '--format=%H', `${target}..${branch}`]);
  if (!logR.ok) {
    result.errors.push(`读取 commit 序列失败: ${logR.stderr}`);
    result.exitCode = 1;
    result.ok = false;
    return finish(result, flags);
  }
  const commits = logR.stdout ? logR.stdout.split(/\r?\n/).filter(Boolean) : [];
  result.commits = commits;

  if (commits.length === 0) {
    result.ok = true;
    result.message = `${branch} 无独有 commit，已 up-to-date`;
    result.result = 'up-to-date';
    return finish(result, flags);
  }

  if (flags.dryRun) {
    result.ok = true;
    result.message = `[dry-run] 将 cherry-pick ${commits.length} 个 commit 到 ${target}`;
    result.result = 'dry-run';
    return finish(result, flags);
  }

  // 检查主工作区是否有已跟踪文件的修改（避免切换分支破坏用户未提交工作）
  // 忽略未跟踪文件（如 .claude/ worktree 目录本身）——它们不阻碍分支切换
  const origBranch = currentBranch();
  const dirty = git(['status', '--porcelain', '--untracked-files=no']).stdout;
  if (dirty) {
    result.errors.push('主工作区有已跟踪文件的未提交修改（切换分支会破坏）。请先 commit/stash 再 merge。');
    result.exitCode = 1;
    result.ok = false;
    return finish(result, flags);
  }

  // 切换到 target 并逐个 cherry-pick（结束后恢复原分支）
  const sw = git(['switch', target]);
  if (!sw.ok) {
    result.errors.push(`切换到 ${target} 失败: ${sw.stderr}`);
    result.exitCode = 1;
    result.ok = false;
    return finish(result, flags);
  }

  for (const h of commits) {
    const cp = git(['cherry-pick', '--allow-empty', h]);
    if (!cp.ok) {
      // 空提交被拒（already applied）→ 视为已包含，继续
      if (cp.stderr.includes('empty') || cp.stdout.includes('empty')) {
        git(['cherry-pick', '--skip']);
        continue;
      }
      result.errors.push(`cherry-pick ${h.slice(0, 8)} 冲突/失败: ${cp.stderr}`);
      result.exitCode = 1;
      result.ok = false;
      result.result = 'conflict';
      result.message = `cherry-pick 冲突，已停止。保留 CHERRY_PICK_HEAD 供解决（continue/abort）。`;
      result.commit_in_progress = h;
      // 恢复原分支（冲突时保留 CHERRY_PICK_HEAD 供模型处理，不切换）
      return finish(result, flags);
    }
  }

  // 恢复原分支（merge 不改变用户当前工作分支）
  if (origBranch && currentBranch() !== origBranch) {
    git(['switch', origBranch]);
  }

  result.ok = true;
  result.result = 'merged';
  result.message = `已 cherry-pick ${commits.length} 个 commit 到 ${target}`;
  return finish(result, flags);
}

// ============ cleanup ============
function cmdCleanup(argv) {
  const flags = parseFlags(argv);
  const target = flags.opt.target || currentBranch() || 'HEAD';
  const result = {
    command: 'cleanup', ok: true, exitCode: 0, target,
    orphansRemoved: [], mergedBranchesDeleted: [], unmerged: [], warnings: [], errors: [],
  };

  const root = repoRoot();
  if (!root) {
    result.errors.push('当前目录不是 git 仓库');
    result.exitCode = 1;
    result.ok = false;
    return finish(result, flags);
  }

  // 1. 孤儿 worktree 检测
  const wtList = git(['worktree', 'list', '--porcelain']);
  if (!wtList.ok) {
    result.errors.push(`git worktree list 失败: ${wtList.stderr}`);
    result.exitCode = 1;
    result.ok = false;
    return finish(result, flags);
  }
  const wts = parseWorktreePorcelain(wtList.stdout);
  const orphans = wts.filter(w => !fs.existsSync(w.path));
  // 记录孤儿分支（prune 前），供后续统一处理
  const orphanBranches = new Set(orphans.filter(o => o.branch).map(o => o.branch));
  // 补充：所有 sdd/ 前缀且不在任何活动 worktree 的分支（execute 产生的无主残留分支）
  const activeBranchSet = new Set(wts.filter(w => fs.existsSync(w.path)).map(w => w.branch).filter(Boolean));
  const allBranches = git(['branch', '--format=%(refname:short)']).stdout || '';
  for (const b of allBranches.split(/\r?\n/).map(l => l.trim()).filter(Boolean)) {
    if (b.startsWith('sdd/') && !activeBranchSet.has(b)) {
      orphanBranches.add(b);
    }
  }

  for (const o of orphans) {
    if (flags.dryRun) {
      result.warnings.push(`[dry-run] 将清理孤儿 worktree: ${o.path} (branch: ${o.branch || 'detached'})`);
      result.orphansRemoved.push(o);
    } else {
      result.orphansRemoved.push({ path: o.path, branch: o.branch || null });
    }
  }
  // prune 清除孤儿注册（不删目录，因目录已不存在）
  if (orphans.length > 0 && !flags.dryRun) git(['worktree', 'prune']);

  // 2. 已合并分支清理 + 孤儿分支处理
  if (!flags.dryRun) {
    const merged = git(['branch', '--merged', target]).stdout || '';
    const mergedSet = new Set(merged.split(/\r?\n/).map(l => l.trim().replace(/^[*\s]+/, '')).filter(Boolean));
    const defaultBranches = new Set(['main', 'master', 'HEAD', target, currentBranch() || '']);
    // 活动 worktree 分支（prune 后重新读取，排除已被清除的孤儿）
    const afterWts = parseWorktreePorcelain(git(['worktree', 'list', '--porcelain']).stdout);
    const activeBranches = new Set(afterWts.map(w => w.branch).filter(Boolean));

    // 孤儿分支：merged → -d 安全删；否则 --force 才删
    for (const ob of orphanBranches) {
      if (defaultBranches.has(ob) || activeBranches.has(ob)) continue;
      if (!SAFE_BRANCH.test(ob)) continue;
      if (mergedSet.has(ob)) {
        git(['branch', '-d', ob]);
        result.mergedBranchesDeleted.push(ob);
      } else if (flags.force) {
        git(['branch', '-D', ob]);
        result.mergedBranchesDeleted.push(ob + '(force)');
      } else {
        result.unmerged.push({ type: 'orphan-branch', path: ob, branch: ob, reason: '孤儿 worktree 分支未合并' });
      }
    }

    // 普通已合并分支清理
    for (const b of mergedSet) {
      if (!b || defaultBranches.has(b) || activeBranches.has(b)) continue;
      if (!SAFE_BRANCH.test(b)) continue; // 防误删
      if (orphanBranches.has(b)) continue; // 已在上方处理
      git(['branch', '-d', b]);
      result.mergedBranchesDeleted.push(b);
    }
  }

  if (result.unmerged.length > 0) {
    result.exitCode = 1;
    result.ok = false;
    result.message = `发现 ${result.unmerged.length} 项未合并（已警示不删除，--force 可强制）`;
    result.warnings.push(`未合并项不自动删除。使用 --force 强制删除。`);
  } else {
    result.message = `清理完成: ${result.orphansRemoved.length} 孤儿 worktree, ${result.mergedBranchesDeleted.length} 已合并分支`;
  }
  return finish(result, flags);
}

// ============ list / status ============
function cmdList(argv) {
  const flags = parseFlags(argv);
  const root = repoRoot();
  const result = { command: 'list', ok: false, exitCode: 0, worktrees: [], warnings: [], errors: [] };
  if (!root) {
    result.errors.push('当前目录不是 git 仓库');
    result.exitCode = 1;
    return finish(result, flags);
  }
  const r = git(['worktree', 'list', '--porcelain']);
  if (!r.ok) {
    result.errors.push(r.stderr);
    result.exitCode = 1;
    return finish(result, flags);
  }
  const wts = parseWorktreePorcelain(r.stdout);
  result.worktrees = wts.map(w => ({
    path: w.path,
    branch: w.branch || null,
    head: w.head || null,
    exists: fs.existsSync(w.path),
    orphan: !fs.existsSync(w.path),
  }));
  result.ok = true;
  result.message = `共 ${result.worktrees.length} 个 worktree`;
  return finish(result, flags);
}

function cmdStatus(argv) {
  const flags = parseFlags(argv);
  const root = repoRoot();
  const result = { command: 'status', ok: false, exitCode: 0, repo: {}, worktrees: [], warnings: [], errors: [] };
  if (!root) {
    result.errors.push('当前目录不是 git 仓库');
    result.exitCode = 1;
    return finish(result, flags);
  }
  const head = git(['rev-parse', '--short', 'HEAD']).stdout || '';
  const dirty = git(['status', '--porcelain']).stdout || '';
  result.repo = {
    root,
    currentBranch: currentBranch(),
    head,
    dirty: dirty ? dirty.split(/\r?\n/).filter(Boolean).length : 0,
  };
  // 复用 list 逻辑（直接读取 worktree 列表）
  const r = git(['worktree', 'list', '--porcelain']);
  const wts = r.ok ? parseWorktreePorcelain(r.stdout) : [];
  result.worktrees = wts.map(w => ({
    path: w.path,
    branch: w.branch || null,
    head: w.head || null,
    exists: fs.existsSync(w.path),
    orphan: !fs.existsSync(w.path),
  }));
  result.ok = true;
  result.message = `仓库 ${path.basename(root)} @ ${head} (${result.repo.currentBranch}), ${result.worktrees.length} worktree`;
  return finish(result, flags);
}

// ============ 用法 / 分发 ============
function usage(argv, hint) {
  const result = {
    command: 'usage', ok: false, exitCode: 2,
    errors: [hint || '未知子命令'],
    warnings: [],
    message: 'Usage: node scripts/worktree.js <create|merge|cleanup|list|status> [args]',
  };
  if (hint) console.log(`[ERR] ${hint}`);
  console.log('Usage: node scripts/worktree.js <create|merge|cleanup|list|status> [args]');
  console.log('  create  {task-id} {branch} [--name <short>] [--base <ref>] [--fallback-branch <name>]');
  console.log('  merge   {task-id} {target-branch} [--dry-run]');
  console.log('  cleanup [--target <branch>] [--dry-run] [--force]');
  console.log('  list    [--json]');
  console.log('  status  [--json]');
  process.exit(2);
}

function finish(result, flags) {
  // 无 errors 且 exitCode 0 → ok
  if (result.errors.length === 0 && result.exitCode === 0) result.ok = true;
  output(result, flags);
  return result.exitCode || (result.ok ? 0 : 1);
}

function dispatch(argv) {
  const sub = argv[0];
  switch (sub) {
    case 'create': return cmdCreate(argv.slice(1));
    case 'merge': return cmdMerge(argv.slice(1));
    case 'cleanup': return cmdCleanup(argv.slice(1));
    case 'list': return cmdList(argv.slice(1));
    case 'status': return cmdStatus(argv.slice(1));
    default: return usage(argv, sub ? `未知子命令: ${sub}` : '缺少子命令');
  }
}

if (require.main === module) {
  const code = dispatch(process.argv.slice(2));
  process.exit(code);
}

module.exports = {
  dispatch, git, parseWorktreePorcelain, parseFlags,
  create: cmdCreate, merge: cmdMerge, cleanup: cmdCleanup, list: cmdList, status: cmdStatus,
};
