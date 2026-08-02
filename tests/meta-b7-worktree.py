#!/usr/bin/env python3
"""T-b7 测试 — worktree 生命周期脚本 (scripts/worktree.js)。

在隔离临时 git 仓库中测试（不污染 orch 主仓库）：
  - 用法边界：无参/未知子命令/缺参 → rc=2
  - list/status --json → rc=0 可解析
  - create + list + merge(noop) → rc=0，worktree 目录真实存在
  - merge 实际 cherry-pick（隔离 target 分支）
  - 孤儿检测：删除目录后 cleanup → orphansRemoved 非空
  - 未合并警示 + --force（rc=1 保留分支 → --force 删除）
  - 路径穿越：create '../evil' / --name ../../evil → rc=2
  - 无效 base → 自动兜底 HEAD 创建成功（rc=0）
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WT_SCRIPT = os.path.join(PLUGIN_ROOT, 'scripts', 'worktree.js')

errors = 0
warnings = 0

# 临时隔离仓库（finally 清理）
TMP_REPO = None


def check(cond, msg):
    global errors, warnings
    if cond:
        print(f'  [OK]   {msg}')
    else:
        errors += 1
        print(f'  [FAIL] {msg}')


def run_wt(args, cwd=None):
    """运行 worktree.js，返回 (rc, stdout, stderr)。"""
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'utf-8'
    proc = subprocess.run(
        ['node', WT_SCRIPT] + args,
        capture_output=True, cwd=cwd or TMP_REPO, env=env, timeout=30,
    )
    out = proc.stdout.decode('utf-8', errors='replace') if proc.stdout else ''
    err = proc.stderr.decode('utf-8', errors='replace') if proc.stderr else ''
    return proc.returncode, out, err


def git_run(args, cwd=None):
    """运行 git 命令，返回 (rc, stdout)。"""
    proc = subprocess.run(['git'] + args, capture_output=True, cwd=cwd or TMP_REPO, timeout=30)
    out = proc.stdout.decode('utf-8', errors='replace') if proc.stdout else ''
    return proc.returncode, out


def create_wt(task_id, branch, **extra):
    """创建 worktree，返回 (rc, worktree_path, branch)。"""
    args = ['create', task_id, branch, '--base', 'HEAD', '--json']
    for k, v in extra.items():
        args.extend([f'--{k}', v])
    rc, out, _ = run_wt(args)
    wt_path = None
    if rc == 0:
        try:
            wt_path = json.loads(out).get('worktree', {}).get('path')
        except json.JSONDecodeError:
            pass
    return rc, wt_path, branch


def setup_repo():
    """在临时目录创建隔离 git 仓库，含一个初始 commit。"""
    global TMP_REPO
    TMP_REPO = tempfile.mkdtemp(prefix='meta-b7-repo-')
    # 初始化并提交
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'utf-8'
    env['GIT_AUTHOR_NAME'] = 'orch-test'
    env['GIT_AUTHOR_EMAIL'] = 'test@orch.dev'
    env['GIT_COMMITTER_NAME'] = 'orch-test'
    env['GIT_COMMITTER_EMAIL'] = 'test@orch.dev'
    subprocess.run(['git', 'init', '-b', 'main'], capture_output=True, cwd=TMP_REPO, env=env)
    open(os.path.join(TMP_REPO, 'README.md'), 'w').write('# test repo\n')
    subprocess.run(['git', 'add', '.'], capture_output=True, cwd=TMP_REPO, env=env)
    subprocess.run(['git', 'commit', '-m', 'init'], capture_output=True, cwd=TMP_REPO, env=env)
    return env


def main():
    global errors
    env = setup_repo()
    try:
        # ============ A. 用法 / 退出码边界 ============
        print('=== A. 用法 / 退出码边界 ===')
        rc, out, err = run_wt([])
        check(rc == 2, f'无参 → rc=2（实际 {rc}）')
        check('Usage' in out + err, '输出含 Usage')

        rc, out, _ = run_wt(['bogus-subcmd'])
        check(rc == 2, f'未知子命令 → rc=2（实际 {rc}）')

        rc, out, _ = run_wt(['create'])
        check(rc == 2, f'create 缺参 → rc=2（实际 {rc}）')

        # ============ B. list/status ============
        print('\n=== B. list/status ===')
        rc, out, _ = run_wt(['list', '--json'])
        check(rc == 0, f'list --json → rc=0（实际 {rc}）')
        try:
            data = json.loads(out)
            check(len(data.get('worktrees', [])) >= 1, f'list 含 worktree（{len(data.get("worktrees", []))} 个）')
            root_norm = os.path.normpath(TMP_REPO)
            check(any(os.path.normpath(w.get('path', '')) == root_norm for w in data.get('worktrees', [])),
                  'list 含仓库根 worktree')
        except json.JSONDecodeError:
            check(False, 'list --json 输出可解析')

        rc, out, _ = run_wt(['status', '--json'])
        check(rc == 0, f'status --json → rc=0（实际 {rc}）')
        try:
            data = json.loads(out)
            check('currentBranch' in data.get('repo', {}), 'status 含 currentBranch')
            check('worktrees' in data, 'status 含 worktrees')
        except json.JSONDecodeError:
            check(False, 'status --json 输出可解析')

        # ============ C. create + merge(noop) ============
        print('\n=== C. create + merge(noop) ===')
        rc, wt_dir_c, _ = create_wt('C1', 'feat/c1')
        check(rc == 0, f'create → rc=0（实际 {rc}）')
        check(wt_dir_c and os.path.isdir(wt_dir_c), 'worktree 目录真实存在')

        rc, out, _ = run_wt(['merge', 'C1', 'main', '--json'])
        check(rc == 0, f'merge(noop) → rc=0（实际 {rc}）')
        try:
            data = json.loads(out)
            check(data.get('result') == 'up-to-date', f'merge(noop) → up-to-date（实际 {data.get("result")}）')
        except json.JSONDecodeError:
            check(False, 'merge --json 输出可解析')

        # ============ D. merge 实际 cherry-pick ============
        print('\n=== D. merge 实际 cherry-pick ===')
        subprocess.run(['git', 'branch', 'target-d', 'HEAD'], capture_output=True, cwd=TMP_REPO, env=env)
        rc, wt_dir_d, _ = create_wt('D1', 'feat/d1')
        check(rc == 0, f'create D → rc=0（实际 {rc}）')
        check(wt_dir_d and os.path.isdir(wt_dir_d), 'create D 目录存在')
        # 在 worktree 内做空 commit
        subprocess.run(['git', '-C', wt_dir_d, 'commit', '--allow-empty', '-m', 'meta-b7 test commit'],
                       capture_output=True, cwd=TMP_REPO, env=env)
        rc, out, _ = run_wt(['merge', 'D1', 'target-d', '--json'])
        check(rc == 0, f'merge D → rc=0（实际 {rc}）')
        try:
            data = json.loads(out)
            check(data.get('result') == 'merged', f'merge D → merged（实际 {data.get("result")}）')
            check(len(data.get('commits', [])) >= 1, f'merge D 含 commit（{len(data.get("commits", []))} 个）')
        except json.JSONDecodeError:
            check(False, 'merge D --json 输出可解析')
        # 验证 target 分支含测试 commit
        _, log_out = git_run(['log', '--oneline', 'target-d'])
        check('meta-b7' in log_out, 'target 分支含测试 commit')
        # merge 应恢复主分支
        _, cur = git_run(['branch', '--show-current'])
        check(cur.strip() == 'main', f'merge 后主分支恢复 main（实际 {cur.strip()}）')

        # ============ E. 孤儿检测 ============
        print('\n=== E. 孤儿检测 ===')
        rc, wt_dir_e, _ = create_wt('E1', 'feat/e1')
        # 手工删除目录制造孤儿
        shutil.rmtree(wt_dir_e, ignore_errors=True)
        rc, out, _ = run_wt(['cleanup', '--json'])
        try:
            data = json.loads(out)
            check(len(data.get('orphansRemoved', [])) >= 1, 'cleanup 检测到孤儿 worktree')
        except json.JSONDecodeError:
            check(False, 'cleanup --json 输出可解析')
        _, list_out = git_run(['worktree', 'list'])
        check(wt_dir_e not in list_out, '孤儿 worktree 已被清除')

        # ============ F. 未合并警示 + --force ============
        print('\n=== F. 未合并警示 + --force ===')
        rc, wt_dir_f, _ = create_wt('F1', 'sdd/test/f1')
        # 做空 commit 使分支领先 main
        subprocess.run(['git', '-C', wt_dir_f, 'commit', '--allow-empty', '-m', 'meta-b7 unmerged'],
                       capture_output=True, cwd=TMP_REPO, env=env)
        # 删除目录制造孤儿 + 未合并
        shutil.rmtree(wt_dir_f, ignore_errors=True)
        rc, out, _ = run_wt(['cleanup', '--json'])
        try:
            data = json.loads(out)
            has_unmerged = len(data.get('unmerged', [])) > 0 or rc == 1
            check(has_unmerged, 'cleanup 警示未合并项')
        except json.JSONDecodeError:
            check(False, 'cleanup F --json 输出可解析')
        _, br_out = git_run(['branch', '--list', 'sdd/test/f1'])
        check('sdd/test/f1' in br_out, '未合并分支默认保留')
        # --force 删除
        rc, out, _ = run_wt(['cleanup', '--force', '--json'])
        _, br_out = git_run(['branch', '--list', 'sdd/test/f1'])
        check('sdd/test/f1' not in br_out, '--force 删除未合并分支')

        # ============ G. 路径穿越 + 无效 base ============
        print('\n=== G. 路径穿越 + 无效 base ===')
        rc, _, _ = run_wt(['create', '../evil', 'x'])
        check(rc == 2, f'路径穿越 create → rc=2（实际 {rc}）')
        rc, _, _ = run_wt(['create', 'T1', 'y', '--name', '../../evil'])
        check(rc == 2, f'--name 路径穿越 → rc=2（实际 {rc}）')
        # 无效 base → 自动兜底 HEAD（容错设计）
        rc, wt_dir_g, _ = create_wt('G1', 'feat/g1', base='nonexistent-branch')
        check(rc == 0, f'无效 base 自动兜底 → rc=0（实际 {rc}）')
        check(wt_dir_g and os.path.isdir(wt_dir_g), '无效 base 兜底创建成功')

        # ============ --json 可解析性 ============
        print('\n=== --json 可解析性 ===')
        for sub in ['list', 'status', 'cleanup']:
            rc, out, _ = run_wt([sub, '--json'])
            try:
                json.loads(out)
                check(True, f'{sub} --json 可解析')
            except json.JSONDecodeError:
                check(False, f'{sub} --json 输出不可解析')
    finally:
        # 清理临时仓库
        if TMP_REPO:
            shutil.rmtree(TMP_REPO, ignore_errors=True)

    print(f'\n=== 结果: {errors} errors, {warnings} warnings ===')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
