#!/bin/bash
# OpenTeam 基准测试入口
# 用法:
#   bash tests/benchmark/run.sh save before    # 保存优化前基线
#   bash tests/benchmark/run.sh save after     # 保存优化后数据
#   bash tests/benchmark/run.sh compare        # 对比 before vs after
#   bash tests/benchmark/run.sh                # 仅运行测量（不保存）

set -e
cd "$(dirname "$0")/../.."

CMD="${1:-measure}"
NAME="${2:-baseline}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  OpenTeam 基准测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

case "$CMD" in
  save)
    echo "► 模式: 保存基线 ($NAME)"
    echo ""
    echo "═══ 1/3 Token 消耗测量 ═══"
    python3 tests/benchmark/token_audit.py --save "$NAME"
    echo ""
    echo "═══ 2/3 规则基线提取 ═══"
    python3 tests/benchmark/rules_baseline.py save "$NAME"
    echo ""
    echo "═══ 3/3 质量场景保存 ═══"
    python3 tests/benchmark/quality_scenarios.py --save "$NAME"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  基线 '$NAME' 已保存到 tests/benchmark/baseline/"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ;;

  compare)
    BEFORE="${NAME:-before}"
    AFTER="${2:-after}"
    if [ "$#" -ge 3 ]; then
      AFTER="$3"
    fi
    echo "► 模式: 对比 ($BEFORE vs $AFTER)"
    echo ""
    echo "═══ 1/2 Token 消耗对比 ═══"
    python3 tests/benchmark/token_audit.py --compare "$BEFORE"
    echo ""
    echo "═══ 2/2 规则覆盖验证 ═══"
    python3 tests/benchmark/rules_baseline.py verify "$BEFORE"
    RESULT=$?
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ $RESULT -eq 0 ]; then
      echo "  规则验证: ✅ PASS"
    elif [ $RESULT -eq 1 ]; then
      echo "  规则验证: ⚠️  WARN (部分规则可能丢失)"
    else
      echo "  规则验证: ❌ FAIL (规则丢失严重)"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ;;

  measure|*)
    echo "► 模式: 仅测量（不保存）"
    echo ""
    echo "═══ Token 消耗测量 ═══"
    python3 tests/benchmark/token_audit.py
    echo ""
    echo "═══ 规则提取 ═══"
    python3 tests/benchmark/rules_baseline.py extract
    ;;
esac
