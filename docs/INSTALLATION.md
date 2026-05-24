# 安装说明

## 快速安装

### 方法1：从 Git 仓库安装（推荐）

一次性安装所有5个skills：

```bash
npx skills add https://github.com/DestinyV/orch.git
```

或单独安装需要的skill：

```bash
npx skills add https://github.com/DestinyV/orch.git --skill spec-creation
npx skills add https://github.com/DestinyV/orch.git --skill code-design
npx skills add https://github.com/DestinyV/orch.git --skill code-task
npx skills add https://github.com/DestinyV/orch.git --skill code-execute
npx skills add https://github.com/DestinyV/orch.git --skill code-test
```

### 方法2：从本地安装（开发测试）

1. **克隆或下载本项目**
```bash
git clone https://github.com/DestinyV/orch.git 
```

2. **本地使用**

Claude Code会自动从 `.claude/skills/` 目录加载本地skills，无需额外配置，直接使用：

```bash
/spec-generator
/code-execution
...
```

---

## 验证安装

安装成功后，在Claude Code中运行以下命令验证：

```bash
/spec-creation
```

如果看到spec-creation的交互式分析，说明安装成功！

---

## 前置要求

- ✅ Claude Code CLI 已安装
- ✅ Node.js 14+ （用于npx命令）
- ✅ Git（推荐，用于克隆项目）

---

## 故障排查

### 问题1：找不到skill
**症状**：运行 `/spec-creation` 报错 "skill not found"

**解决**：
1. 确认安装完成：`npx skills add https://github.com/DestinyV/orch.git`
2. 重启Claude Code CLI
3. 检查skill是否加载：在Claude Code中输入 `/` 应该能看到skills列表

### 问题2：权限错误
**症状**：安装时报错 "permission denied"

**解决**：
- Windows：以管理员身份运行终端
- Mac/Linux：使用 `sudo` 或检查目录权限

### 问题3：找不到spec目录
**症状**：运行 `/code-design` 时报错 "spec directory not found"

**解决**：
1. 首先运行 `/spec-creation` 生成spec规范
2. 确保规范文件已生成到 `spec-dev/{requirement_desc_abstract}/spec/` 目录

---

## 支持的技术栈

- ✅ Spring Boot / Spring Cloud
- ✅ Django / Flask
- ✅ Node.js / Express / Next.js
- ✅ 其他任何技术栈（通过自定义ai-doc规范）

---

## 下一步

安装完成后，按照以下步骤开始使用：

1. **需求规范化**
   ```bash
   /spec-creation [需求描述]
   ```

2. **代码设计规划**
   ```bash
   /code-design
   ```

3. **任务列表生成**
   ```bash
   /code-task
   ```

4. **代码执行实现**
   ```bash
   /code-execute
   ```

5. **测试和验证**
   ```bash
   /code-test
   ```

详见 [使用指南](./USAGE.md) 和 [完整命令说明](../commands/sdd-dev.md)

---
