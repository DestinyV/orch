#!/usr/bin/env bash
# validate-outputs.sh — 批量验证产出文件存在性（非空）+ 空目录清理
# 用法: validate-outputs.sh <file1> <file2> ... 或 validate-outputs.sh --dir <dir1> <dir2>
set -euo pipefail

failures=0
total=0

# 验证文件非空
for f in "$@"; do
    [[ "$f" == "--dir" ]] && break
    total=$((total + 1))
    if [ -s "$f" ]; then
        echo "✓ $f"
    else
        echo "✗ $f (empty or missing)"
        failures=$((failures + 1))
    fi
done

# 清理空目录
shift_args=()
in_dir=false
for arg in "$@"; do
    if [[ "$arg" == "--dir" ]]; then
        in_dir=true
        continue
    fi
    if $in_dir; then
        if [ -d "$arg" ]; then
            if [ -z "$(ls -A "$arg" 2>/dev/null)" ]; then
                echo "🗑️ 清理空目录: $arg"
                rmdir "$arg"
            fi
        fi
    fi
done

echo ""
echo "验证结果: $((total - failures))/$total 通过"
[ $failures -eq 0 ] && exit 0 || exit 1
