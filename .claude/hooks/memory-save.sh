#!/bin/bash
# 【会话结束钩子】提醒 Claude 持久化本次会话的关键记忆
# 触发时机: Stop 事件（会话结束时）

MEMORY_DIR=".claude/memory"

# 确保记忆目录存在
if [ ! -d "$MEMORY_DIR" ]; then
  mkdir -p "$MEMORY_DIR"
  echo "📁 已创建记忆目录: $MEMORY_DIR"
fi

cat << 'EOF'
📝 [会话记忆持久化] 会话即将结束，请检查是否需要保存以下信息:

1. 【关键决策】本次会话是否做出了影响架构或技术选型的决策？
   → 写入 .claude/memory/decisions.md

2. 【踩坑经验】本次会话是否发现并解决了非显而易见的问题？
   → 写入 .claude/memory/issues.md

3. 【代码模式】本次会话是否发现了项目特有的编码模式或惯例？
   → 写入 .claude/memory/patterns.md

4. 【任务进度】进行中的任务状态是否需要更新？
   → 更新 .claude/memory/active-tasks.md

5. 【项目上下文】是否有需要记录的项目架构变化？
   → 更新 .claude/memory/project-context.md

如果以上均无变化，则无需写入。不要为了写而写。

格式要求:
- 每条记忆不超过 3 行
- 必须包含日期和上下文
- 增量更新，不覆盖已有内容
EOF
