# eval-summary

# 从 .workflow-eval.json 生成评估摘要
# 用法: bash eval-summary.sh orch-spec/{requirement_id}/.workflow-eval.json

set -e

EVAL_FILE="${1:-.workflow-eval.json}"

if [ ! -f "$EVAL_FILE" ]; then
  echo "❌ 评估文件不存在: $EVAL_FILE"
  exit 1
fi

echo "===== SDD+TDD 工作流评估摘要 ====="
echo ""

# 基本信息
echo "📋 基本信息:"
jq -r '"  需求: \(.requirement_id) | 模式: \(.project_mode)/\(.mode) | 总耗时: \(.total_duration_sec)s"' "$EVAL_FILE"
echo ""

# 阶段统计
echo "📊 阶段统计:"
jq -r '.stages[] | "  [\(.stage)] \(.skill): \(.status) (\(.duration_sec)s) Agent:\(.agent.name)=\(.agent.status) HARD-GATE:\(.hard_gate_triggers)"' "$EVAL_FILE"
echo ""

# 汇总
echo "📈 汇总:"
jq -r '"  总阶段:\(.summary.stages_total) | 完成:\(.summary.stages_done) | 失败:\(.summary.stages_failed) | 跳过:\(.summary.stages_skipped)"' "$EVAL_FILE"
jq -r '"  Agent派遣:\(.summary.agents_dispatched) | 成功:\(.summary.agents_success) | 失败:\(.summary.agents_failed)"' "$EVAL_FILE"
jq -r '"  HARD-GATE总触发:\(.summary.hard_gates_total) | 用户交互:\(.summary.user_interactions_total)"' "$EVAL_FILE"
echo ""

# 诊断
echo "🔍 诊断:"
jq -r '.diagnosis.bottlenecks[]? | "  ⚠️ 瓶颈: \(.)"' "$EVAL_FILE"
jq -r '.diagnosis.warnings[]? | "  ⚡ 警告: \(.)"' "$EVAL_FILE"
jq -r '.diagnosis.suggestions[]? | "  💡 建议: \(.)"' "$EVAL_FILE"

# 无诊断时的默认输出
DIAG_COUNT=$(jq -r '.diagnosis.bottlenecks | length + .diagnosis.warnings | length + .diagnosis.suggestions | length' "$EVAL_FILE")
if [ "$DIAG_COUNT" -eq 0 ]; then
  echo "  ✅ 无诊断问题，流程执行良好"
fi
echo ""
echo "================================"
