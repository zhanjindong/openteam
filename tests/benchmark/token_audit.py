#!/usr/bin/env python3
"""
OpenTeam Token 消耗审计工具

按场景统计 spec 文件的 token 消耗，支持优化前后对比。

用法:
    python3 tests/benchmark/token_audit.py                  # 单次测量
    python3 tests/benchmark/token_audit.py --save baseline   # 保存为基线
    python3 tests/benchmark/token_audit.py --compare baseline # 与基线对比
"""

import json
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CLAUDE_DIR = PROJECT_ROOT / ".claude"
BASELINE_DIR = Path(__file__).resolve().parent / "baseline"

# ──────────────────────────────────────────
# Token 估算（Claude tokenizer 近似）
# ──────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """
    估算 Claude token 数。
    中文字符 ≈ 1.5 tokens/char，ASCII ≈ 0.25 tokens/char（4 chars/token）。
    这是近似值，用于相对对比，不追求绝对精确。
    """
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', text))
    ascii_chars = len(text) - chinese_chars
    return int(chinese_chars * 1.5 + ascii_chars * 0.25)


def file_metrics(filepath: Path) -> dict:
    """计算单个文件的指标"""
    if not filepath.exists():
        return {"exists": False, "lines": 0, "chars": 0, "tokens": 0}
    content = filepath.read_text(encoding="utf-8")
    lines = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
    return {
        "exists": True,
        "lines": lines,
        "chars": len(content),
        "tokens": estimate_tokens(content),
    }


# ──────────────────────────────────────────
# 场景定义：每个场景 = 该场景会加载哪些文件
# ──────────────────────────────────────────

def build_scenarios():
    """构建测量场景"""
    # 基础文件（每次会话必加载）
    base_always = [
        "CLAUDE.md",
        ".claude/rules/git-workflow.md",
        ".claude/rules/security.md",
        ".claude/rules/testing.md",
    ]

    # 后端项目额外加载（code-style 已合并到 context）
    base_backend = base_always + [
        ".claude/rules/context-backend.md",
    ]
    # 兼容旧基线：如果 code-style 文件存在则加入
    if (PROJECT_ROOT / ".claude/rules/code-style-backend.md").exists():
        base_backend.append(".claude/rules/code-style-backend.md")

    # 前端项目额外加载
    base_frontend = base_always + [
        ".claude/rules/context-frontend.md",
    ]
    if (PROJECT_ROOT / ".claude/rules/code-style-frontend.md").exists():
        base_frontend.append(".claude/rules/code-style-frontend.md")

    # 全加载（后端+前端 context 都加载，无 code-style 时仅 context）
    base_all = base_always + [
        ".claude/rules/context-backend.md",
        ".claude/rules/context-frontend.md",
    ]
    if (PROJECT_ROOT / ".claude/rules/code-style-backend.md").exists():
        base_all.append(".claude/rules/code-style-backend.md")
    if (PROJECT_ROOT / ".claude/rules/code-style-frontend.md").exists():
        base_all.append(".claude/rules/code-style-frontend.md")

    scenarios = {
        "S1_基础会话_后端项目": {
            "desc": "后端项目每次对话的固定消耗",
            "files": base_backend,
        },
        "S2_基础会话_前端项目": {
            "desc": "前端项目每次对话的固定消耗",
            "files": base_frontend,
        },
        "S3_基础会话_无globs全加载": {
            "desc": "rules 无 globs 配置时全部加载（当前现状）",
            "files": base_all,
        },
        "S4_ot-product命令": {
            "desc": "/ot-product 需求分析",
            "files": base_all + [
                ".claude/commands/ot-product.md",
                ".claude/agents/product.md",
            ],
        },
        "S5_ot-plan命令": {
            "desc": "/ot-plan 规划设计",
            "files": base_all + [
                ".claude/commands/ot-plan.md",
                ".claude/agents/plan.md",
            ],
        },
        "S6_ot-develop命令": {
            "desc": "/ot-develop 开发实现",
            "files": base_all + [
                ".claude/commands/ot-develop.md",
                ".claude/agents/develop.md",
            ],
        },
        "S7_ot-testing命令": {
            "desc": "/ot-testing 测试验证",
            "files": base_all + [
                ".claude/commands/ot-testing.md",
                ".claude/agents/testing.md",
            ],
        },
        "S8_ot-review命令": {
            "desc": "/ot-review 全流程审查",
            "files": base_all + [
                ".claude/commands/ot-review.md",
                ".claude/agents/review.md",
            ],
        },
        "S9_完整pipeline": {
            "desc": "/openteam pipeline 全流程（调度器 + 全部 Agent）",
            "files": base_all + [
                ".claude/commands/openteam.md",
                ".claude/commands/ot-product.md",
                ".claude/agents/product.md",
                ".claude/commands/ot-plan.md",
                ".claude/agents/plan.md",
                ".claude/commands/ot-develop.md",
                ".claude/agents/develop.md",
                ".claude/commands/ot-testing.md",
                ".claude/agents/testing.md",
                ".claude/commands/ot-review.md",
                ".claude/agents/review.md",
            ],
        },
        "S10_ot-commit工具": {
            "desc": "/ot-commit 智能提交",
            "files": base_all + [
                ".claude/commands/ot-commit.md",
            ],
        },
        "S11_ot-create-api生成": {
            "desc": "/ot-create-api 生成接口",
            "files": base_all + [
                ".claude/commands/ot-create-api.md",
            ],
        },
        "S12_openteam_help": {
            "desc": "/openteam help 查看帮助",
            "files": base_all + [
                ".claude/commands/openteam.md",
                ".claude/docs/openteam-guide.md",
            ],
        },
    }
    return scenarios


# ──────────────────────────────────────────
# 重复内容检测
# ──────────────────────────────────────────

def detect_duplication():
    """检测跨文件重复的规则/约束语句"""
    rule_patterns = [
        (r'禁止', 'prohibit'),
        (r'必须', 'must'),
        (r'不允许', 'not_allowed'),
        (r'不能|不可以', 'cannot'),
        (r'只能|只限|仅限', 'only'),
    ]

    # 收集每个文件中的约束语句
    file_rules = {}
    spec_dirs = [
        CLAUDE_DIR / "rules",
        CLAUDE_DIR / "agents",
        CLAUDE_DIR / "commands",
    ]
    extra_files = [PROJECT_ROOT / "CLAUDE.md"]

    all_files = list(extra_files)
    for d in spec_dirs:
        if d.exists():
            all_files.extend(sorted(d.glob("*.md")))

    for fp in all_files:
        if not fp.exists():
            continue
        content = fp.read_text(encoding="utf-8")
        rules = []
        for line in content.splitlines():
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith("#") or line_stripped.startswith("|"):
                continue
            for pattern, _ in rule_patterns:
                if re.search(pattern, line_stripped):
                    rules.append(line_stripped[:80])
                    break
        if rules:
            rel = str(fp.relative_to(PROJECT_ROOT))
            file_rules[rel] = rules

    # 检测跨文件重复（简单文本相似度）
    duplicates = []
    files = list(file_rules.keys())
    for i, f1 in enumerate(files):
        for f2 in files[i + 1:]:
            for r1 in file_rules[f1]:
                for r2 in file_rules[f2]:
                    # 提取关键词比较
                    words1 = set(re.findall(r'[\u4e00-\u9fff]+', r1))
                    words2 = set(re.findall(r'[\u4e00-\u9fff]+', r2))
                    if len(words1) < 2 or len(words2) < 2:
                        continue
                    overlap = words1 & words2
                    union = words1 | words2
                    if len(union) > 0 and len(overlap) / len(union) > 0.5:
                        duplicates.append({
                            "file1": f1,
                            "rule1": r1,
                            "file2": f2,
                            "rule2": r2,
                            "similarity": round(len(overlap) / len(union), 2),
                        })

    return file_rules, duplicates


# ──────────────────────────────────────────
# 输出
# ──────────────────────────────────────────

def measure_all():
    """执行全部测量，返回结构化结果"""
    scenarios = build_scenarios()
    results = {}

    for name, scenario in scenarios.items():
        file_details = []
        total = {"lines": 0, "chars": 0, "tokens": 0}

        for rel_path in scenario["files"]:
            fp = PROJECT_ROOT / rel_path
            m = file_metrics(fp)
            file_details.append({"file": rel_path, **m})
            total["lines"] += m["lines"]
            total["chars"] += m["chars"]
            total["tokens"] += m["tokens"]

        results[name] = {
            "desc": scenario["desc"],
            "file_count": len(scenario["files"]),
            "files": file_details,
            "total": total,
        }

    _, duplicates = detect_duplication()

    return {
        "scenarios": results,
        "duplicate_count": len(duplicates),
        "duplicates_sample": duplicates[:20],
    }


def print_report(data: dict, compare_data: dict = None):
    """打印可读报告"""
    print("=" * 72)
    print("  OpenTeam Token 消耗审计报告")
    print("=" * 72)
    print()

    for name, result in data["scenarios"].items():
        t = result["total"]
        print(f"┌─ {name}")
        print(f"│  {result['desc']}")
        print(f"│")

        for fd in result["files"]:
            status = "" if fd["exists"] else " [NOT FOUND]"
            print(f"│  {fd['file']:<52s} {fd['lines']:>4d}行  {fd['tokens']:>5d}tk{status}")

        print(f"│")
        line = f"│  合计: {result['file_count']}文件  {t['lines']}行  {t['chars']}字符  ≈{t['tokens']} tokens"

        if compare_data and name in compare_data["scenarios"]:
            old_t = compare_data["scenarios"][name]["total"]
            diff_tokens = t["tokens"] - old_t["tokens"]
            diff_pct = (diff_tokens / old_t["tokens"] * 100) if old_t["tokens"] > 0 else 0
            sign = "+" if diff_tokens >= 0 else ""
            line += f"  ({sign}{diff_tokens}tk / {sign}{diff_pct:.1f}%)"

        print(line)
        print(f"└{'─' * 71}")
        print()

    # 重复检测摘要
    print(f"┌─ 跨文件重复约束检测")
    print(f"│  发现 {data['duplicate_count']} 条疑似重复约束")
    for d in data.get("duplicates_sample", [])[:10]:
        print(f"│  [{d['similarity']}] {d['file1']} ↔ {d['file2']}")
        print(f"│    A: {d['rule1'][:60]}")
        print(f"│    B: {d['rule2'][:60]}")
        print(f"│")
    print(f"└{'─' * 71}")

    # 总览表
    print()
    print("=" * 72)
    print("  场景总览对比表")
    print("=" * 72)
    print(f"{'场景':<30s} {'文件':>4s} {'行数':>5s} {'Tokens':>7s}", end="")
    if compare_data:
        print(f" {'基线Tk':>7s} {'差异':>8s}", end="")
    print()
    print("-" * 72)

    for name, result in data["scenarios"].items():
        t = result["total"]
        short_name = name.split("_", 1)[1] if "_" in name else name
        print(f"{short_name:<30s} {result['file_count']:>4d} {t['lines']:>5d} {t['tokens']:>7d}", end="")
        if compare_data and name in compare_data["scenarios"]:
            old_tk = compare_data["scenarios"][name]["total"]["tokens"]
            diff = t["tokens"] - old_tk
            sign = "+" if diff >= 0 else ""
            print(f" {old_tk:>7d} {sign}{diff:>7d}", end="")
        print()


def main():
    args = sys.argv[1:]

    save_name = None
    compare_name = None

    i = 0
    while i < len(args):
        if args[i] == "--save" and i + 1 < len(args):
            save_name = args[i + 1]
            i += 2
        elif args[i] == "--compare" and i + 1 < len(args):
            compare_name = args[i + 1]
            i += 2
        elif args[i] == "--json":
            # JSON 输出模式
            data = measure_all()
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return
        else:
            i += 1

    data = measure_all()

    # 加载对比基线
    compare_data = None
    if compare_name:
        baseline_file = BASELINE_DIR / f"{compare_name}.json"
        if baseline_file.exists():
            compare_data = json.loads(baseline_file.read_text(encoding="utf-8"))
        else:
            print(f"[WARN] 基线文件不存在: {baseline_file}")

    print_report(data, compare_data)

    # 保存
    if save_name:
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        out = BASELINE_DIR / f"{save_name}.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[OK] 基线已保存: {out}")


if __name__ == "__main__":
    main()
