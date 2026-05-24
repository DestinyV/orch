# 后端静态分析指南

> test 阶段 1 静态分析参考

## 分析维度

| 维度 | Python | Go | Java | Rust |
|------|--------|----|----|------|
| 代码规范 | pylint / ruff | golangci-lint | checkstyle | clippy |
| 类型检查 | mypy | go vet | Error Prone | cargo check |
| 格式化 | black | gofmt | google-java-format | rustfmt |
| 安全扫描 | bandit | gosec | spotbugs | cargo audit |
| 复杂度 | radon | gocyclo | pmd-cpd | cargo clippy |

## 通过标准

- 0 编译错误
- 0 严重 lint 问题
- 类型检查通过
- 格式化检查通过
- 无安全漏洞（≥80 置信度）

## 常见反模式

| 反模式 | 检测方式 | 修复 |
|--------|---------|------|
| 未使用变量 | linter 警告 | 删除或标注 `_` |
| 重复代码 | pmd-cpd/radon | 提取函数 |
| 魔法数字 | sonarqube | 命名常量 |
| 过长函数 | linter (max 50 行) | 拆分子函数 |
| 未处理错误 | go vet / mypy | 添加错误处理 |

## 执行命令

```bash
# Python
pylint src/ --fail-under=8.0 && mypy src/ --strict && black --check src/

# Go
go vet ./... && golangci-lint run && gofmt -d .

# Java
mvn checkstyle:check spotbugs:check compile

# Rust
cargo clippy -- -D warnings && cargo fmt --check && cargo check
```
