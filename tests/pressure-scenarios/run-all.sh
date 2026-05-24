#!/usr/bin/env bash
# ============================================================
# 批量运行所有压力场景
# 用途：在隔离环境中验证 Skill 在压力下的有效性
# 用法：bash run-all.sh [--type <type>]
# ============================================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCENARIOS_DIR="$(cd "$(dirname "$0")/scenarios" && pwd)"

# 运行统计
total=0
passed=0
failed=0
skipped=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Skill 压力测试${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "📋 压力测试需要在隔离的 Claude 会话中手动运行"
echo ""
echo "每个场景文件包含："
echo "  - 测试输入（模拟用户消息）"
echo "  - 期望行为（Agent 应该如何响应）"
echo "  - 失败行为（没有门控时 Agent 会怎么做）"
echo "  - 预期的 Agent 合理化借口"
echo ""
echo "使用方法："
echo "  1. 打开场景文件，阅读测试输入"
echo "  2. 在新的 Claude 会话中输入该消息"
echo "  3. 观察 Agent 行为是否符合期望"
echo "  4. 记录结果到场景文件的'修复记录'表格"
echo ""
echo -e "${BLUE}可用场景：${NC}"
echo ""

# 列出所有场景
scenario_files=("$SCENARIOS_DIR"/*.md)
for file in "${scenario_files[@]}"; do
  [ -f "$file" ] || continue
  filename=$(basename "$file")
  total=$((total + 1))
  # 提取场景标题
  title=$(head -1 "$file" | sed 's/^# //')
  echo -e "  ${YELLOW}${total}.${NC} ${filename}: ${title}"
done

echo ""
echo -e "${BLUE}========================================${NC}"
echo ""

# 输出测试指南
echo -e "${BLUE}📖 测试指南${NC}"
echo ""
echo "1. 选择一个场景文件"
echo "2. 复制「测试输入」中的内容"
echo "3. 在新的 Claude 会话中粘贴并发送"
echo "4. 观察 Agent 是否："
echo "   - 跳过了必要步骤？（失败）"
echo "   - 使用了合理化借口？（失败）"
echo "   - 遵循了 HARD-GATE？（通过）"
echo "   - 执行了完成验证？（通过）"
echo "5. 将结果记录到场景文件的修复记录表格"
echo ""
echo -e "${YELLOW}注意：此脚本仅列出场景，实际测试需要在 Claude 会话中手动执行。${NC}"
echo -e "${YELLOW}未来将实现自动化测试框架。${NC}"
