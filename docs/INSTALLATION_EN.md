# Installation Guide

## Quick Installation

### Method 1: Install from Git Repository (Recommended)

Install all 6 skills at once:

```bash
npx skills add https://github.com/DestinyV/orch.git
```

Or install individual skills:

```bash
npx skills add https://github.com/DestinyV/orch.git --skill spec-creation
npx skills add https://github.com/DestinyV/orch.git --skill code-design
npx skills add https://github.com/DestinyV/orch.git --skill code-task
npx skills add https://github.com/DestinyV/orch.git --skill code-execute
npx skills add https://github.com/DestinyV/orch.git --skill code-test
npx skills add https://github.com/DestinyV/orch.git --skill spec-archive
```

### Method 2: Local Installation (Development/Testing)

1. **Clone or download the project**
```bash
git clone https://github.com/DestinyV/orch.git 
```

2. **Use locally**

Claude Code automatically loads local skills from `.claude/skills/` directory, no additional configuration needed. Just use directly:

```bash
/spec-creation
/code-design
/code-task
/code-execute
/code-test
/spec-archive
```

---

## Verify Installation

After successful installation, verify in Claude Code:

```bash
/spec-creation
```

If you see the interactive analysis prompt from spec-creation, installation was successful!

---

## Prerequisites

- ✅ Claude Code CLI installed
- ✅ Node.js 14+ (for npx commands)
- ✅ Git (recommended, for cloning the project)

## 🌐 Multi-Platform Support

While installation instructions above are optimized for **Claude Code**, the SDD+TDD workflow skills are **platform-agnostic** and can be used on:

| Platform | Installation Method |
|----------|-------------------|
| **Claude Code** | `npx skills add` or local `.claude/skills/` loading |
| **OpenAI Codex** | Copy skill content into project context |
| **GitHub Copilot CLI** | Paste skill content as initial context |
| **Cursor** | Load skill content in chat/project context |
| **Gemini CLI** | Copy skill content into system prompt |
| **OpenCode** | Copy skill content into project context |

The skill files (`SKILL.md`) are standard Markdown and can be loaded as context in any AI coding platform. For tool mappings between platforms, see `skills/using-superpowers/references/`.

---

## Troubleshooting

### Issue 1: Skill Not Found
**Symptoms**: Running `/spec-creation` throws "skill not found" error

**Solution**:
1. Confirm installation completed: `npx skills add https://github.com/DestinyV/orch.git`
2. Restart Claude Code CLI
3. Check if skills loaded: Type `/` in Claude Code - you should see the skills list

### Issue 2: Permission Error
**Symptoms**: "permission denied" error during installation

**Solution**:
- Windows: Run terminal as Administrator
- Mac/Linux: Use `sudo` or check directory permissions

### Issue 3: Spec Directory Not Found
**Symptoms**: Running `/code-design` throws "spec directory not found" error

**Solution**:
1. First run `/spec-creation` to generate spec specifications
2. Ensure spec files were generated to `spec-dev/{requirement_desc_abstract}/spec/` directory

---

## Supported Tech Stacks

- ✅ Spring Boot / Spring Cloud
- ✅ Django / Flask
- ✅ Node.js / Express / Next.js
- ✅ React / Vue / Angular / Svelte
- ✅ PostgreSQL / MongoDB / MySQL
- ✅ Any other tech stack (through custom AI-doc specifications)

---

## Next Steps

After installation, follow these steps to start using:

1. **Requirements Specification**
   ```bash
   /spec-creation [Requirements Description]
   ```

2. **Code Design Planning**
   ```bash
   /code-design
   ```

3. **Task List Generation**
   ```bash
   /code-task
   ```

4. **Code Execution**
   ```bash
   /code-execute
   ```

5. **Testing and Verification**
   ```bash
   /code-test
   ```

6. **Spec Archiving** (automatic after tests pass)
   ```bash
   /spec-archive
   ```

For more details, see [Usage Guide](./USAGE_EN.md) and [Plugin README](../README_EN.md)

---
