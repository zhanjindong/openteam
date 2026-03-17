#!/bin/bash
# 【会话结束钩子】管理 handoff.md 的 git 元数据
# 触发时机: Stop 事件（会话结束时）
#
# 策略：
#   - 文件不存在 → 创建带占位符的模板
#   - 文件已存在 → 只 sed 更新头部 3 行元数据（时间/用户/分支），其余内容原封不动

MEMORY_DIR=".claude/memory"
HANDOFF_FILE="$MEMORY_DIR/handoff.md"

mkdir -p "$MEMORY_DIR"

# === 收集 git 元数据 ===

BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
GIT_USER=$(git config user.name 2>/dev/null || echo "unknown")
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

# === 文件已存在：只更新元数据行 ===

if [ -f "$HANDOFF_FILE" ]; then
  sed -i '' "s|^> 最后更新:.*|> 最后更新: $TIMESTAMP|" "$HANDOFF_FILE" 2>/dev/null
  sed -i '' "s|^> 更新者:.*|> 更新者: $GIT_USER|" "$HANDOFF_FILE" 2>/dev/null
  sed -i '' "s|^> 分支:.*|> 分支: $BRANCH|" "$HANDOFF_FILE" 2>/dev/null

  echo "📝 [handoff] 已更新 handoff.md 元数据（时间/用户/分支），内容未变"
  exit 0
fi

# === 文件不存在：创建模板 ===

# 变更文件列表
CHANGED_FILES=$(git diff --name-only 2>/dev/null)
STAGED_FILES=$(git diff --cached --name-only 2>/dev/null)
UNTRACKED_FILES=$(git ls-files --others --exclude-standard 2>/dev/null)
ALL_CHANGES=$(printf '%s\n%s\n%s' "$CHANGED_FILES" "$STAGED_FILES" "$UNTRACKED_FILES" | sort -u | grep -v '^$')

RECENT_COMMITS=$(git log --oneline -5 2>/dev/null)

# 构建变更文件块
CHANGES_BLOCK=""
if [ -n "$ALL_CHANGES" ]; then
  while IFS= read -r f; do
    CHANGES_BLOCK="${CHANGES_BLOCK}- \`${f}\`
"
  done <<< "$ALL_CHANGES"
else
  CHANGES_BLOCK="- 无未提交的文件变更
"
fi

# 构建提交记录块
COMMITS_BLOCK=""
if [ -n "$RECENT_COMMITS" ]; then
  COMMITS_BLOCK="\`\`\`
${RECENT_COMMITS}
\`\`\`"
else
  COMMITS_BLOCK="- 无最近提交"
fi

# 写入模板
printf '%s\n' "# 工作交接" "" "> 最后更新: $TIMESTAMP" "> 更新者: $GIT_USER" "> 分支: $BRANCH" "" \
  "## 当前状态" "[Claude 未写入 - 请在会话结束前更新此段]" "" \
  "## 本次改动" > "$HANDOFF_FILE"
printf '%s\n' "$CHANGES_BLOCK" >> "$HANDOFF_FILE"
printf '%s\n' "## 最近提交" "$COMMITS_BLOCK" "" \
  "## 关键决策" "[Claude 未写入 - 请在会话结束前更新此段]" "" \
  "## 注意事项" "[Claude 未写入 - 请在会话结束前更新此段]" "" \
  "## 下一步" "[Claude 未写入 - 请在会话结束前更新此段]" >> "$HANDOFF_FILE"

echo "📝 [handoff] 已创建 handoff.md 模板"
echo ""
echo "请用 Edit 工具更新 .claude/memory/handoff.md 中的 [Claude 未写入] 段落："
echo "1. 当前状态：一句话总结本次会话做了什么"
echo "2. 关键决策：本次做出的技术决策及理由"
echo "3. 注意事项：坑、临时方案、脆弱区域"
echo "4. 下一步：接手后应该先做什么"
echo ""
echo "补充完成后执行: git add .claude/memory/"
