# OpenTeam — AI 协作指南

## 会话初始化

每次会话启动时：
1. 如果 `.claude/memory/` 目录存在，先读取其中所有 .md 文件，快速了解项目上下文、进行中的任务、已知问题和关键决策
2. 如果 `TODO.md` 存在，读取当前任务进度，从上次中断的位置继续
3. 如果 `DESIGN.md` 存在，了解当前需求的设计方案

## 上下文压缩

当对话过长或上下文接近限制时，按照 `.claude/hooks/strategic-compact.md` 中的压缩协议执行结构化压缩：
- L1（核心锚点）完整保留：任务目标、设计方案、已改文件、当前进度
- L2（工作状态）压缩为摘要
- L3/L4（过程细节）丢弃
- 将有价值的发现写入 `.claude/memory/` 持久化

## 项目概述

- **项目名称**: [填写项目名称]
- **项目描述**: [填写项目描述]
- **技术栈**: [自动通过 rules/context-*.md 按文件类型加载]

## 分支规范

- `master`: 生产代码，只用于创建开发版本或 hotfix
- `release`: 生产构建基准分支
- `feature/*`: 功能开发，合入后删除
- `hotfix/*`: 线上修复，合入后删除

## OpenTeam 命令速查

### 研发流程（调度入口）

```
/openteam pipeline|team|auto [需求]   总调度中心
```

### 研发阶段

```
/ot-product    需求分析 → DESIGN.md
/ot-plan       规划设计 → DESIGN.md + TODO.md
/ot-develop    开发实现 → 代码 + TODO.md 进度
/ot-testing    测试验证 → 测试报告
/ot-review     审查迭代 → 审查报告
```

### 工具命令

```
/ot-commit     智能提交
/ot-build-fix  构建排障
/ot-refactor   安全重构
/ot-changelog  变更日志
/ot-debug      系统排查
```

### 生成命令

```
/ot-create-api        生成API接口（后端项目）
/ot-create-test       生成测试用例
/ot-create-component  生成Vue组件（前端项目）
/ot-create-page       生成页面全套（前端项目）
```

## 项目类型自动识别

本规范通过 `rules/context-*.md` 的 `globs` 配置自动识别项目类型并加载对应规范：
- 检测到 `*.java` → 加载后端规范 (`context-backend.md`)
- 检测到 `*.vue` / `*.ts` / `*.tsx` → 加载前端规范 (`context-frontend.md`)
- 扩展新项目类型：只需新增 `rules/context-{type}.md` 并配置 globs
