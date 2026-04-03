# OpenTeam

> AI-Powered Software Development Orchestration Framework for Claude Code

OpenTeam 是一个基于 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 的 **AI 研发调度框架**，通过 5 个专业 Agent 协作完成软件研发全流程。它将需求分析、架构设计、编码实现、测试验证、代码审查等环节编排为可调度的 Agent 流水线，让 AI 像一个真正的研发团队一样工作。

## 核心特性

- **5 Agent 协作** — Product（需求分析）、Plan（架构设计）、Develop（编码实现）、Testing（测试验证）、Review（代码审查）
- **3 种调度模式** — Pipeline（严格流水线）、Team（智能调度）、Auto（自主规划），适配不同研发场景
- **20+ Slash Commands** — 覆盖研发全流程的命令体系，包括代码生成、构建排障、安全重构等
- **14 个自动化 Hooks** — 阻断型 + 提醒型 + 会话管理，构建安全护栏
- **跨会话记忆持久化** — 通过 handoff.md + DESIGN.md + TODO.md 实现多会话接续开发
- **项目规范自动加载** — 根据文件类型自动识别前端/后端项目，加载对应编码规范

## 快速开始

### 1. 安装

将 OpenTeam 配置复制到你的项目根目录：

```bash
git clone https://github.com/zhanjindong/openteam.git
cp -r openteam/.claude your-project/
cp openteam/CLAUDE.md your-project/
```

### 2. 使用

在项目目录中启动 Claude Code，输入命令即可开始：

```bash
# 查看帮助
/openteam help

# 严格流水线模式 — 适合新功能开发
/openteam pipeline 实现用户登录功能

# 智能调度模式 — 适合明确需求或 Bug 修复
/openteam team 修复分页查询性能问题

# 自主规划模式 — 适合探索性或复杂任务
/openteam auto 重构认证模块
```

## 调度模式

### Pipeline — 严格流水线

按 `Product → Plan → Develop → Testing → Review` 顺序执行，每阶段需用户确认后推进，发现问题可回退迭代。适合新功能开发和需要全流程追溯的场景。

### Team — 智能调度

根据任务特征自动选择 Agent 组合：

| 任务特征 | 调度方案 |
|---------|---------|
| 需求模糊 | Product → Plan |
| 需求明确需设计 | Plan → Develop → Testing |
| 改动简单 / 修 Bug | Develop → Testing |
| 只需测试或审查 | Testing / Review |

### Auto — 自主规划

突破固定流程，自主设计最优策略，可并行 Agent、自定义顺序、动态调整。适合探索性任务和跨领域复杂任务。

## Agent 分工

| Agent | 角色 | 输入 | 输出 |
|-------|------|------|------|
| **Product** | 需求分析师 | 用户需求 | DESIGN.md 需求规格 |
| **Plan** | 架构设计师 | 需求规格 | DESIGN.md 技术方案 + TODO.md |
| **Develop** | 软件工程师 | 技术方案 + TODO.md | 代码实现 + 进度更新 |
| **Testing** | 测试工程师 | 验收标准 + 代码 | 测试用例 + 测试报告 |
| **Review** | 质量专家 | 全部产出物 | 审查报告（可触发回退） |

权限约束：只有 Develop 可修改源代码，Testing 可写测试但禁止改源码，Product/Plan 只产出文档。

## 命令速查

### 研发流程

| 命令 | 说明 |
|------|------|
| `/openteam pipeline` | 严格流水线模式 |
| `/openteam team` | 智能调度模式 |
| `/openteam auto` | 自主规划模式 |

### 研发阶段

| 命令 | 说明 | 产出 |
|------|------|------|
| `/ot-product` | 需求分析 | DESIGN.md 需求规格 |
| `/ot-plan` | 规划设计 | DESIGN.md 技术方案 + TODO.md |
| `/ot-develop` | 开发实现 | 代码 + TODO.md 进度 |
| `/ot-testing` | 测试验证 | 测试用例 + 测试报告 |
| `/ot-review` | 全流程审查 | 审查报告 |

### 工具命令

| 命令 | 说明 |
|------|------|
| `/ot-commit` | 智能提交（Angular 规范） |
| `/ot-build-fix` | 构建排障 |
| `/ot-debug` | 系统化排查 |
| `/ot-refactor` | 安全重构 |
| `/ot-changelog` | 变更日志生成 |
| `/ot-clear` | 清理项目状态 |

### 代码生成

| 命令 | 说明 | 适用 |
|------|------|------|
| `/ot-create-api` | 生成 API 接口 | 后端 |
| `/ot-create-test` | 生成测试用例 | 全栈 |
| `/ot-create-component` | 生成 Vue 组件 | 前端 |
| `/ot-create-page` | 生成页面全套 | 前端 |

## 自动化 Hooks

OpenTeam 内置 14 个 Hooks 构建安全护栏：

**阻断型** — 阻止危险操作
- 禁止使用 npm/yarn（强制 pnpm）
- 禁止 force push 和直接 push 到 master/release
- 拦截 `rm -rf`、`drop table` 等高危命令
- 拦截 Vue Options API 写法
- 扫描硬编码密钥

**提醒型** — 温和提醒
- 长耗时服务提醒使用 tmux
- 跳过测试时提醒
- 检查 System.out / console.log

**会话管理** — 自动维护上下文
- 会话结束时自动刷新 handoff.md
- 上下文接近限制时触发结构化压缩

## 跨会话接续开发

Claude Code 每次会话独立，上下文在会话结束后丢失。OpenTeam 通过 **记忆三件套** 实现跨会话接续：

| 文件 | 作用 | 维护者 |
|------|------|--------|
| `DESIGN.md` | 需求规格 + 技术方案 | Product / Plan Agent |
| `TODO.md` | 任务列表 + 进度 | Plan 生成，Develop 更新 |
| `.claude/memory/handoff.md` | 工作交接状态 | Claude + Stop Hook |

新会话启动时 Claude 自动读取这三份文件，恢复完整上下文，从上次中断处继续工作。

## 项目规范自动识别

通过 `.claude/rules/context-*.md` 的文件类型匹配自动加载对应规范：

| 检测到的文件 | 加载的规范 |
|-------------|-----------|
| `*.java` | Spring Boot 3.x + Java 21 + MyBatis-Plus |
| `*.vue` / `*.ts` / `*.tsx` | Vue 3.5 + TypeScript 5.8 + Element Plus + Tailwind CSS 4 |

可通过新增 `context-{type}.md` 文件扩展更多项目类型。

## 目录结构

```
your-project/
├── CLAUDE.md                          # AI 协作指南（入口配置）
└── .claude/
    ├── agents/                        # Agent 定义
    │   ├── product.md                 # 需求分析师
    │   ├── plan.md                    # 架构设计师
    │   ├── develop.md                 # 软件工程师
    │   ├── testing.md                 # 测试工程师
    │   └── review.md                  # 质量专家
    ├── commands/                       # Slash Commands
    │   ├── openteam.md                # 调度中心入口
    │   ├── ot-product.md              # 需求分析
    │   ├── ot-plan.md                 # 规划设计
    │   ├── ot-develop.md              # 开发实现
    │   ├── ot-testing.md              # 测试验证
    │   ├── ot-review.md               # 全流程审查
    │   ├── ot-commit.md               # 智能提交
    │   ├── ot-create-api.md           # 生成 API
    │   ├── ot-create-component.md     # 生成组件
    │   ├── ot-create-page.md          # 生成页面
    │   ├── ot-create-test.md          # 生成测试
    │   └── ...                        # 更多工具命令
    ├── rules/                          # 项目规范（按文件类型自动加载）
    │   ├── context-backend.md         # 后端规范
    │   ├── context-frontend.md        # 前端规范
    │   ├── git-workflow.md            # Git 工作流
    │   ├── security.md                # 安全规范
    │   └── testing.md                 # 测试规范
    ├── hooks/                          # 自动化护栏脚本
    │   ├── block-*.sh                 # 阻断型护栏
    │   ├── check-*.sh                 # 检查型护栏
    │   ├── memory-save.sh             # 记忆持久化
    │   └── strategic-compact.sh       # 上下文压缩
    ├── memory/                         # 跨会话记忆
    │   └── handoff.md                 # 工作交接文件
    └── settings.json                   # 权限与 Hooks 配置
```

## 前置要求

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) 已安装并配置
- Git

## 许可证

MIT License
