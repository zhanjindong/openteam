#!/usr/bin/env python3
"""
OpenTeam 规则基线提取 & 验证工具

从 spec 文件中提取所有行为约束规则，生成可 diff 的基线文件。
优化后重新提取并对比，确保规则无丢失。

用法:
    python3 tests/benchmark/rules_baseline.py extract          # 提取并显示
    python3 tests/benchmark/rules_baseline.py save baseline     # 保存为基线
    python3 tests/benchmark/rules_baseline.py verify baseline   # 与基线对比
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BASELINE_DIR = Path(__file__).resolve().parent / "baseline"

# ──────────────────────────────────────────
# 规则提取
# ──────────────────────────────────────────

# 约束关键词模式
CONSTRAINT_PATTERNS = [
    (r'禁止', 'prohibit'),
    (r'必须', 'must'),
    (r'不允许|不得', 'not_allowed'),
    (r'不能|不可以|不要', 'cannot'),
    (r'只能|只限|仅限|只使用|只负责', 'only'),
    (r'不超过|不少于|至少', 'limit'),
    (r'严格', 'strict'),
]

# 行为指令模式
ACTION_PATTERNS = [
    (r'^-\s*\[[ x]\]', 'checklist'),          # - [ ] / - [x]
    (r'^\d+\.\s+', 'numbered_rule'),           # 1. 2. 3.
    (r'^>\s*⚠️', 'warning'),                   # > ⚠️
]

# 输出格式指令
FORMAT_PATTERNS = [
    (r'格式[:：]', 'format'),
    (r'模板', 'template'),
    (r'命名.*[:：]', 'naming'),
]


def extract_rules_from_file(filepath: Path) -> list[dict]:
    """从单个文件中提取规则"""
    if not filepath.exists():
        return []

    content = filepath.read_text(encoding="utf-8")
    rules = []
    current_section = ""

    for line_num, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()

        # 跟踪当前章节
        if stripped.startswith("#"):
            current_section = stripped.lstrip("#").strip()
            continue

        # 跳过空行、纯表格分割线、代码块标记
        if not stripped or stripped.startswith("```") or re.match(r'^[-|]+$', stripped):
            continue

        # 检测约束关键词
        for pattern, category in CONSTRAINT_PATTERNS:
            if re.search(pattern, stripped):
                rules.append({
                    "line": line_num,
                    "section": current_section,
                    "category": category,
                    "type": "constraint",
                    "text": stripped[:120],
                })
                break
        else:
            # 检测编号规则（仅保留包含实质内容的）
            for pattern, category in ACTION_PATTERNS:
                if re.match(pattern, stripped) and len(stripped) > 10:
                    # 过滤掉纯列表项（如目录结构）
                    if any(kw in stripped for kw in ['禁止', '必须', '使用', '遵循', '确认', '检查', '运行', '读取', '写入', '输出', '生成']):
                        rules.append({
                            "line": line_num,
                            "section": current_section,
                            "category": category,
                            "type": "action",
                            "text": stripped[:120],
                        })
                    break

    return rules


def extract_all_rules() -> dict:
    """从所有 spec 文件中提取规则"""
    scan_paths = [
        ("CLAUDE.md", PROJECT_ROOT / "CLAUDE.md"),
    ]

    # 扫描目录
    for subdir in ["rules", "agents", "commands", "hooks", "docs"]:
        d = PROJECT_ROOT / ".claude" / subdir
        if d.exists():
            for f in sorted(d.glob("*.md")):
                rel = f".claude/{subdir}/{f.name}"
                scan_paths.append((rel, f))

    all_rules = {}
    summary = {"total_rules": 0, "by_file": {}, "by_category": {}}

    for rel_path, abs_path in scan_paths:
        rules = extract_rules_from_file(abs_path)
        if rules:
            all_rules[rel_path] = rules
            summary["by_file"][rel_path] = len(rules)
            summary["total_rules"] += len(rules)
            for r in rules:
                cat = r["category"]
                summary["by_category"][cat] = summary["by_category"].get(cat, 0) + 1

    return {"rules": all_rules, "summary": summary}


# ──────────────────────────────────────────
# 规则指纹（用于跨版本对比）
# ──────────────────────────────────────────

def normalize_rule(text: str) -> str:
    """规则文本标准化，用于模糊匹配"""
    # 去掉编号、markdown 标记、多余空格
    text = re.sub(r'^[\d]+[.、)]\s*', '', text)
    text = re.sub(r'^[-*]\s*(\[[ x]\]\s*)?', '', text)
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'`[^`]*`', '', text)
    text = re.sub(r'\s+', '', text)
    return text[:60]


def build_fingerprints(data: dict) -> dict[str, set]:
    """为每个文件的规则建立指纹集合"""
    fps = {}
    for filepath, rules in data["rules"].items():
        fps[filepath] = set()
        for r in rules:
            fp = normalize_rule(r["text"])
            if len(fp) > 5:
                fps[filepath].add(fp)
    return fps


# ──────────────────────────────────────────
# 对比验证
# ──────────────────────────────────────────

def verify_against_baseline(current: dict, baseline: dict) -> dict:
    """对比当前规则与基线，检测丢失和新增"""
    curr_fps = build_fingerprints(current)
    base_fps = build_fingerprints(baseline)

    # 合并所有指纹
    all_curr = set()
    for fps in curr_fps.values():
        all_curr.update(fps)

    all_base = set()
    for fps in base_fps.values():
        all_base.update(fps)

    missing = all_base - all_curr
    added = all_curr - all_base
    preserved = all_base & all_curr

    # 反查丢失规则的原始文本
    missing_details = []
    for filepath, rules in baseline["rules"].items():
        for r in rules:
            fp = normalize_rule(r["text"])
            if fp in missing:
                missing_details.append({
                    "file": filepath,
                    "line": r["line"],
                    "text": r["text"],
                })

    coverage = len(preserved) / len(all_base) * 100 if all_base else 100

    return {
        "baseline_total": len(all_base),
        "current_total": len(all_curr),
        "preserved": len(preserved),
        "missing": len(missing),
        "added": len(added),
        "coverage_pct": round(coverage, 1),
        "missing_details": missing_details,
        "verdict": "PASS" if coverage >= 95 else "WARN" if coverage >= 85 else "FAIL",
    }


# ──────────────────────────────────────────
# 输出
# ──────────────────────────────────────────

def print_extraction(data: dict):
    """打印提取结果"""
    s = data["summary"]
    print("=" * 72)
    print("  OpenTeam 规则提取报告")
    print("=" * 72)
    print(f"\n  总规则数: {s['total_rules']}")
    print(f"\n  按分类:")
    for cat, count in sorted(s["by_category"].items(), key=lambda x: -x[1]):
        label = {
            "prohibit": "禁止类",
            "must": "必须类",
            "not_allowed": "不允许类",
            "cannot": "不能类",
            "only": "只能/仅限类",
            "limit": "数值限制类",
            "strict": "严格类",
            "numbered_rule": "编号规则",
            "checklist": "检查清单",
            "warning": "警告",
        }.get(cat, cat)
        print(f"    {label:<16s} {count:>3d}")

    print(f"\n  按文件:")
    for fp, count in sorted(s["by_file"].items(), key=lambda x: -x[1]):
        print(f"    {fp:<52s} {count:>3d}条")

    print(f"\n{'─' * 72}")
    print("  规则明细")
    print(f"{'─' * 72}")
    for filepath, rules in data["rules"].items():
        print(f"\n  ◆ {filepath}")
        for r in rules:
            marker = "🚫" if r["category"] in ("prohibit", "not_allowed", "cannot") else \
                     "✅" if r["category"] in ("must", "strict") else \
                     "📌" if r["category"] == "only" else "  "
            print(f"    {marker} L{r['line']:>3d} [{r['category']:<12s}] {r['text'][:70]}")


def print_verification(result: dict):
    """打印验证结果"""
    print("=" * 72)
    print("  OpenTeam 规则覆盖验证报告")
    print("=" * 72)

    verdict_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(result["verdict"], "?")
    print(f"\n  结论: {verdict_icon} {result['verdict']}")
    print(f"  覆盖率: {result['coverage_pct']}%")
    print(f"  基线规则: {result['baseline_total']} 条")
    print(f"  当前规则: {result['current_total']} 条")
    print(f"  保留: {result['preserved']} | 丢失: {result['missing']} | 新增: {result['added']}")

    if result["missing_details"]:
        print(f"\n{'─' * 72}")
        print("  丢失的规则:")
        for d in result["missing_details"]:
            print(f"    ❌ {d['file']}:L{d['line']}")
            print(f"       {d['text'][:70]}")

    print()


# ──────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "extract":
        data = extract_all_rules()
        print_extraction(data)

    elif cmd == "save":
        name = sys.argv[2] if len(sys.argv) > 2 else "baseline"
        data = extract_all_rules()
        print_extraction(data)
        BASELINE_DIR.mkdir(parents=True, exist_ok=True)
        out = BASELINE_DIR / f"rules_{name}.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[OK] 规则基线已保存: {out}")

    elif cmd == "verify":
        name = sys.argv[2] if len(sys.argv) > 2 else "baseline"
        baseline_file = BASELINE_DIR / f"rules_{name}.json"
        if not baseline_file.exists():
            print(f"[ERROR] 基线文件不存在: {baseline_file}")
            print(f"请先运行: python3 {__file__} save {name}")
            sys.exit(1)
        baseline = json.loads(baseline_file.read_text(encoding="utf-8"))
        current = extract_all_rules()
        result = verify_against_baseline(current, baseline)
        print_verification(result)
        # 退出码: 0=PASS, 1=WARN, 2=FAIL
        sys.exit(0 if result["verdict"] == "PASS" else 1 if result["verdict"] == "WARN" else 2)

    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
