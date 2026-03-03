# OpenTeam 使用指南

## 简介

OpenTeam 是一个基于 Claude Code 的 **AI 研发调度中心**，通过 5 个专业 Agent 协作完成软件研发全流程。它将需求分析、架构设计、编码实现、测试验证、代码审查组织为可调度的工作流，支持三种执行模式适配不同场景。

## 安装方式

将 `openteam` 目录下文件复制到你的项目根目录下即可：

```bash
cp -r openteam/*/ your-project/
```

然后在你的项目目录下启动claude，`/openteam help` 命令查看使用帮助。

确保项目根目录包含：
- `.claude/commands/` — 所有命令文件
- `.claude/agents/` — Agent 定义文件
- `.claude/rules/` — 项目规范文件
- `.claude/hooks/` — 自动化护栏脚本
- `CLAUDE.md` — AI 协作指南

## 命令速查表

### 研发流程（调度入口）

| 命令 | 说明 |
|------|------|
| `/openteam help` | 查看本使用说明 |
| `/openteam pipeline [需求]` | 严格流水线模式 |
| `/openteam team [需求]` | 智能调度模式 |
| `/openteam auto [需求]` | 自主规划模式 |

### 研发阶段命令

| 命令 | 说明 | 产出 |
|------|------|------|
| `/ot-product` | 需求分析 | DESIGN.md 需求规格 |
| `/ot-plan` | 规划设计 | DESIGN.md 技术方案 + TODO.md |
| `/ot-develop` | 开发实现 | 代码 + TODO.md 进度更新 |
| `/ot-testing` | 测试验证 | 测试用例 + 测试报告 |
| `/ot-review` | 审查迭代 | 审查报告 |

### 工具命令

| 命令 | 说明 |
|------|------|
| `/ot-commit` | 智能提交（Angular 格式） |
| `/ot-build-fix` | 构建排障 |
| `/ot-refactor` | 安全重构 |
| `/ot-debug` | 系统排查 |
| `/ot-changelog` | 变更日志生成 |

### 生成命令

| 命令 | 说明 | 适用项目 |
|------|------|---------|
| `/ot-create-api` | 生成 API 接口 | 后端 |
| `/ot-create-test` | 生成测试用例 | 全栈 |
| `/ot-create-component` | 生成 Vue 组件 | 前端 |
| `/ot-create-page` | 生成页面全套 | 前端 |

---

## 三种调度模式

### 🏭 Pipeline — 严格流水线

**适用场景**: 新功能开发、需求不明确、团队要求全流程可追溯

按固定顺序执行全部 5 个阶段，每个阶段需用户确认后才进入下一阶段：

```
① product → ② plan → ③ develop → ④ testing → ⑤ review
   需求分析    规划设计   开发实现    测试验证    审查迭代
```

**特点**:
- 严格顺序执行，不跳过任何阶段
- 每阶段完成后展示产出摘要，等待用户确认
- 发现问题可回退到对应阶段迭代修复
- 全程记录到 DESIGN.md / TODO.md，完整可追溯

### 🧑‍🤝‍🧑 Team — 智能调度

**适用场景**: 需求明确只需部分阶段、Bug 修复、小功能迭代、日常开发

调度中心根据任务自动选择 Agent 组合：

| 任务类型 | 调度方案 |
|---------|---------|
| 需求模糊 | product → plan |
| 需求明确，需要设计 | plan → develop → testing |
| 改动简单 | develop → testing |
| 单纯修 Bug | develop → testing |
| 只需写测试 | testing |
| 只需代码审查 | review |
| 大规模变更 | 全流程 |

**特点**:
- 自动分析任务需要哪些 Agent
- 展示调度计划供用户确认或调整
- 执行过程中可动态追加 Agent

### 🤖 Auto — 自主规划

**适用场景**: 探索性任务、跨领域复杂任务、创造性解决方案、非标准流程

突破固定流程，自主设计最优执行策略：

- 可以并行执行多个 Agent
- 可以自定义执行顺序和交互方式
- 可以根据中间结果动态调整策略
- 可以引入固定流程之外的工作方式

**示例**: 性能优化任务 → `review(定位瓶颈) → [plan→develop→testing]×N → review(整体验收)`

---

## 研发流程闭环

```
     ┌─────────────────────────────────────────────┐
     │            OpenTeam 研发流程闭环               │
     │                                             │
     │  需求 ─→ product ─→ plan ─→ develop          │
     │            │          │        │             │
     │            ▼          ▼        ▼             │
     │        DESIGN.md   TODO.md   代码实现         │
     │                                │             │
     │                    testing ◄───┘             │
     │                      │                      │
     │                      ▼                      │
     │                    review                    │
     │                    ╱    ╲                    │
     │              ✅ 通过    🔄 迭代               │
     │                ↓        ↓                   │
     │            🎉 完成    回到对应阶段             │
     └─────────────────────────────────────────────┘
```

---

## Agent 分工表

| Agent | 角色 | 输入 | 输出 |
|-------|------|------|------|
| **Product** | 需求分析师 | 用户需求 | DESIGN.md 需求规格 |
| **Plan** | 架构设计师 | 需求规格 | DESIGN.md 技术方案 + TODO.md |
| **Develop** | 软件工程师 | 技术方案 + TODO.md | 代码实现 + TODO.md 进度 |
| **Testing** | 测试工程师 | 验收标准 + 代码 | 测试方案 + 测试报告 |
| **Review** | 质量专家 | 全部产出物 | 审查报告（可触发迭代回退） |

### Agent 权限模型

各 Agent 有严格的权限边界，**只有 Develop Agent 可以修改源代码**：

| Agent | 读取代码 | 修改源代码 | 修改测试代码 | 写入文档 | 执行命令 |
|-------|---------|-----------|-------------|---------|---------|
| Product | ✅ | ❌ | ❌ | DESIGN.md（需求部分） | ✅ |
| Plan | ✅ | ❌ | ❌ | DESIGN.md（方案部分）+ TODO.md | ✅ |
| Develop | ✅ | ✅ | ✅ | TODO.md 进度 + DESIGN.md 状态 | ✅ |
| Testing | ✅ | ❌ | ✅ | ❌ | ✅ 运行测试 |
| Review | ✅ | ❌ | ❌ | ❌ | ✅ |

- Testing 可以编写测试用例代码，但禁止修改源代码；发现 Bug 记录到报告中由 Develop 修复
- Review 发现问题只输出报告，由对应 Agent 修复
- Product / Plan 只产出文档，不触碰任何代码

---

## Hooks 自动化护栏

OpenTeam 通过 `.claude/hooks/` 下的脚本实现自动化质量护栏：

### 阻断型（违规时阻止操作）

| 护栏 | 说明 |
|------|------|
| `block-npm-yarn.sh` | 禁止使用 npm/yarn（前端只允许 pnpm） |
| `block-force-push.sh` | 禁止 force push |
| `block-push-main-branch.sh` | 禁止直接 push 到 master/release |
| `block-dangerous-command.sh` | 拦截 `rm -rf`、`drop table` 等高危命令 |
| `block-options-api.sh` | 检测并拦截 Vue Options API 写法 |
| `check-hardcoded-secret.sh` | 扫描硬编码密钥 |

### 提醒型（提示但不阻止）

| 护栏 | 说明 |
|------|------|
| `check-tmux-reminder.sh` | 启动长耗时服务时提醒使用 tmux |
| `check-skip-tests-reminder.sh` | 跳过测试编译时提醒 |
| `check-system-out.sh` | 编辑 Java 文件后检查 System.out |
| `check-console-log.sh` | 编辑前端文件后扫描 console.log |

### 会话管理

| 护栏 | 说明 |
|------|------|
| `memory-save.sh` | 会话结束时持久化关键上下文 |
| `strategic-compact.sh` | 上下文接近限制时触发结构化压缩 |

---

## 项目类型自动识别

OpenTeam 通过 `.claude/rules/context-*.md` 的 `globs` 配置自动识别项目类型：

| 检测到的文件 | 加载的规范 |
|-------------|-----------|
| `*.java` | `context-backend.md` — Spring Boot 3.x + Java 21 + MyBatis-Plus |
| `*.vue` / `*.ts` / `*.tsx` | `context-frontend.md` — Vue 3.5 + TypeScript 5.8 + Element Plus |

### 扩展新项目类型

新增 `.claude/rules/context-{type}.md` 并配置 `globs` 即可，例如：

```yaml
---
globs: "*.go"
description: Go 项目规范
---
```

OpenTeam 会自动根据当前编辑的文件类型加载对应规范，无需修改任何命令逻辑。

---

## 核心文档说明

| 文档 | 用途 | 维护时机 |
|------|------|---------|
| `DESIGN.md` | 需求规格 + 技术方案，随 product/plan 阶段生成和更新 | product、plan 阶段 |
| `TODO.md` | 任务列表 + 进度追踪，开发过程中实时更新 | plan 生成，develop 更新 |
| `.claude/memory/` | 跨会话知识持久化（项目上下文、活跃任务、决策记录等） | 每次会话结束自动保存 |
| `CLAUDE.md` | AI 协作指南，项目入口文件 | 项目初始化时配置 |

### Memory 持久化文件

| 文件 | 内容 |
|------|------|
| `project-context.md` | 项目整体上下文 |
| `active-tasks.md` | 进行中的任务 |
| `decisions.md` | 关键决策记录 |
| `patterns.md` | 代码模式与约定 |
| `issues.md` | 已知问题 |
| `contacts.md` | 相关人员 |

---

## 快速开始

1. 将 OpenTeam 配置复制到项目中
2. 在 Claude Code 中打开项目
3. 输入 `/openteam` 选择模式开始工作

**推荐**：首次使用建议选择 `pipeline` 模式体验完整流程，熟悉后切换到 `team` 模式提高效率。
