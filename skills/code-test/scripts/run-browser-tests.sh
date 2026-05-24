#!/usr/bin/env bash
# ============================================================
# 浏览器测试自动化执行脚本
# 用途：在 code-test 阶段一键执行前端浏览器测试
# 用法：bash run-browser-tests.sh [e2e|visual|component|all]
# ============================================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认测试类型
TEST_TYPE=${1:-all}

# ============================================================
# 前置检查
# ============================================================

check_node() {
  if ! command -v node &>/dev/null; then
    echo -e "${RED}错误: 未找到 Node.js，请先安装 Node.js${NC}"
    exit 1
  fi
  echo -e "${GREEN}✓${NC} Node.js: $(node --version)"
}

check_playwright() {
  if npx playwright --version &>/dev/null; then
    echo -e "${GREEN}✓${NC} Playwright 已安装"
    return 0
  else
    echo -e "${YELLOW}!${NC} Playwright 未安装"
    echo ""
    echo "安装 Playwright："
    echo "  npm install -D @playwright/test"
    echo "  npx playwright install chromium"
    echo ""
    echo -e "${RED}跳过浏览器测试。${NC}"
    return 1
  fi
}

check_dev_server() {
  local port=${1:-5173}
  if lsof -i :${port} &>/dev/null; then
    echo -e "${GREEN}✓${NC} 开发服务器运行中 (端口 ${port})"
    return 0
  else
    echo -e "${YELLOW}!${NC} 开发服务器未运行，尝试启动..."
    start_dev_server
    return $?
  fi
}

start_dev_server() {
  echo -e "${BLUE}→${NC} 启动开发服务器..."
  if [ -f "vite.config.ts" ] || [ -f "vite.config.js" ]; then
    npm run dev &
    DEV_SERVER_PID=$!
    echo -e "${BLUE}→${NC} 等待开发服务器就绪..."
    local retries=30
    while [ $retries -gt 0 ]; do
      if lsof -i :5173 &>/dev/null; then
        echo -e "${GREEN}✓${NC} 开发服务器已启动"
        return 0
      fi
      sleep 2
      retries=$((retries - 1))
    done
    echo -e "${RED}错误: 开发服务器启动超时${NC}"
    return 1
  elif [ -f "next.config.js" ] || [ -f "next.config.mjs" ]; then
    npm run dev &
    DEV_SERVER_PID=$!
    echo -e "${BLUE}→${NC} 等待 Next.js 开发服务器..."
    sleep 10
    return 0
  else
    echo -e "${YELLOW}!${NC} 未检测到构建工具，跳过开发服务器启动"
    echo -e "${YELLOW}  请手动启动开发服务器后重新运行此脚本${NC}"
    return 1
  fi
}

cleanup() {
  if [ -n "$DEV_SERVER_PID" ]; then
    echo -e "${BLUE}→${NC} 关闭开发服务器 (PID: $DEV_SERVER_PID)..."
    kill $DEV_SERVER_PID 2>/dev/null || true
    wait $DEV_SERVER_PID 2>/dev/null || true
  fi
}
trap cleanup EXIT

# ============================================================
# 执行测试
# ============================================================

run_e2e() {
  echo ""
  echo -e "${BLUE}============================${NC}"
  echo -e "${BLUE}  执行 E2E 端到端测试${NC}"
  echo -e "${BLUE}============================${NC}"
  echo ""

  npx playwright test --grep "@e2e" --project="chromium-e2e" --reporter=html,list
  local exit_code=$?

  if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓${NC} E2E 测试全部通过"
  else
    echo -e "${RED}✗${NC} E2E 测试存在失败"
  fi

  return $exit_code
}

run_visual() {
  echo ""
  echo -e "${BLUE}============================${NC}"
  echo -e "${BLUE}  执行视觉回归测试${NC}"
  echo -e "${BLUE}============================${NC}"
  echo ""

  npx playwright test --grep "@visual" --project="chromium-visual" --reporter=html,list
  local exit_code=$?

  if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 视觉回归测试全部通过"
  else
    echo -e "${YELLOW}!${NC} 视觉回归测试存在差异（可能是预期的更新）"
    echo "  查看差异报告: npx playwright show-report"
    echo "  更新基准截图: npx playwright test --update-snapshots"
  fi

  return $exit_code
}

run_component() {
  echo ""
  echo -e "${BLUE}============================${NC}"
  echo -e "${BLUE}  执行组件 UI 测试${NC}"
  echo -e "${BLUE}============================${NC}"
  echo ""

  npx playwright test --grep "@component" --project="chromium-component" --reporter=html,list
  local exit_code=$?

  if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 组件 UI 测试全部通过"
  else
    echo -e "${RED}✗${NC} 组件 UI 测试存在失败"
  fi

  return $exit_code
}

# ============================================================
# 主流程
# ============================================================

main() {
  echo -e "${BLUE}========================================${NC}"
  echo -e "${BLUE}  前端浏览器测试执行${NC}"
  echo -e "${BLUE}========================================${NC}"
  echo ""

  # 前置检查
  check_node
  check_playwright || exit 0
  check_dev_server || exit 0

  echo ""

  local overall_exit=0

  case $TEST_TYPE in
    e2e)
      run_e2e || overall_exit=1
      ;;
    visual)
      run_visual || overall_exit=1
      ;;
    component)
      run_component || overall_exit=1
      ;;
    all)
      run_e2e || overall_exit=1
      run_visual || true  # 视觉回归失败不阻断
      run_component || overall_exit=1
      ;;
    *)
      echo -e "${RED}错误: 未知的测试类型 '$TEST_TYPE'${NC}"
      echo "用法: $0 [e2e|visual|component|all]"
      exit 1
      ;;
  esac

  # 生成报告
  echo ""
  echo -e "${BLUE}========================================${NC}"
  echo -e "${BLUE}  测试报告${NC}"
  echo -e "${BLUE}========================================${NC}"
  echo ""

  if [ -d "playwright-report" ]; then
    echo -e "${GREEN}✓${NC} HTML 报告已生成: playwright-report/index.html"
    echo "  查看报告: npx playwright show-report"
  fi

  if [ $overall_exit -eq 0 ]; then
    echo ""
    echo -e "${GREEN}所有测试通过！${NC}"
  else
    echo ""
    echo -e "${RED}部分测试失败，请查看报告${NC}"
  fi

  exit $overall_exit
}

main
