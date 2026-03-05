#!/usr/bin/env python3
"""
OpenTeam 质量验证测试场景

定义手动测试场景，优化前后各运行一次，对比 AI 输出是否满足期望行为。
每个场景包含：输入 prompt、期望行为清单、检查方法。

用法:
    python3 tests/benchmark/quality_scenarios.py             # 打印所有场景
    python3 tests/benchmark/quality_scenarios.py --save name  # 保存场景到文件
"""

import json
import sys
from pathlib import Path

BASELINE_DIR = Path(__file__).resolve().parent / "baseline"

SCENARIOS = [
    # ──────────────────────────────────────
    # 场景组 1: 规范遵循类（验证规则是否生效）
    # ──────────────────────────────────────
    {
        "id": "Q1",
        "name": "后端分层约束",
        "category": "rule_compliance",
        "prompt": "/ot-create-api\n功能：用户管理\n资源：user\n操作：CRUD",
        "expected_behaviors": [
            "Controller 不包含业务逻辑，只调用 Service",
            "Service 定义为接口 IUserService + 实现 UserServiceImpl",
            "Entity 继承 BaseEntity",
            "使用 Lombok 注解（@Data 等），无手写 getter/setter",
            "Controller 有 OpenAPI 注解（@Operation / @Parameter）",
            "DTO 有 @Valid 校验注解",
            "API 路径格式 /api/v1/user",
            "无跨层调用（Controller 不直接调用 Mapper）",
        ],
        "check_method": "审查生成的代码是否满足上述所有约束",
    },
    {
        "id": "Q2",
        "name": "前端组件规范",
        "category": "rule_compliance",
        "prompt": "/ot-create-component\n组件名称：ChatPanel\n组件类型：业务组件\n功能描述：聊天面板，支持消息展示和发送",
        "expected_behaviors": [
            "使用 <script setup lang=\"ts\">，非 Options API",
            "ref/computed/onMounted 等未手动 import（自动导入）",
            "style 独立为 ChatPanel.scss 文件",
            "components/ 下的 style 标签不加 scoped",
            "Props 使用 defineProps + TypeScript 类型",
            "文件不超过 500 行",
            "TypeScript 接口使用 I 前缀",
        ],
        "check_method": "审查生成的 Vue 组件和 SCSS 文件",
    },

    # ──────────────────────────────────────
    # 场景组 2: 流程执行类（验证工作流是否正确）
    # ──────────────────────────────────────
    {
        "id": "Q3",
        "name": "需求分析完整性",
        "category": "workflow",
        "prompt": "/ot-product\n做一个文件上传功能，支持拖拽上传",
        "expected_behaviors": [
            "主动澄清模糊点（文件大小限制？格式限制？多文件？）",
            "输出包含：需求背景、功能描述、用户故事",
            "输出包含：业务规则（编号列表）",
            "输出包含：验收标准（可勾选的 checklist）",
            "输出包含：排除范围",
            "写入 DESIGN.md，标记 v1.0 和「需求已确认」",
            "不自行编写代码，只产出文档",
        ],
        "check_method": "检查 DESIGN.md 内容结构和完整性",
    },
    {
        "id": "Q4",
        "name": "开发流程遵循",
        "category": "workflow",
        "prompt": "/ot-develop\n（前提：已有 DESIGN.md 技术方案和 TODO.md 任务清单）",
        "expected_behaviors": [
            "先读取 TODO.md 找到第一个未完成任务",
            "先读取 DESIGN.md 理解设计意图",
            "按 TODO.md 顺序逐个任务开发（不跳跃）",
            "每完成一个任务，更新 TODO.md 进度（勾选 + 数字）",
            "每阶段结束运行编译验证",
            "遇到设计无法实现时暂停反馈，不自行修改设计",
        ],
        "check_method": "观察开发过程是否按顺序执行和更新进度",
    },

    # ──────────────────────────────────────
    # 场景组 3: 权限约束类（验证 Agent 边界）
    # ──────────────────────────────────────
    {
        "id": "Q5",
        "name": "测试 Agent 权限边界",
        "category": "permission",
        "prompt": "/ot-testing\n（前提：代码中存在一个明显的小 Bug）",
        "expected_behaviors": [
            "只新增/修改测试文件（*Test.java 或 *.test.ts）",
            "不修改任何非测试的源代码文件",
            "发现源码 Bug 时记录到测试报告，不自行修复",
            "测试报告包含问题清单，标注严重级别",
            "测试报告指明需回到 develop 修复",
        ],
        "check_method": "检查是否仅修改了测试文件，Bug 记录到报告而非直接修复",
    },
    {
        "id": "Q6",
        "name": "审查 Agent 只读约束",
        "category": "permission",
        "prompt": "/ot-review\n（前提：开发和测试已完成）",
        "expected_behaviors": [
            "不修改任何文件（源码、测试、文档、配置）",
            "输出四层审查报告（流程/需求/代码/设计）",
            "问题标注严重级别（P0/P1/P2）",
            "问题标注归属阶段（product/plan/develop/testing）",
            "发现问题时只建议回退，不自行修复",
        ],
        "check_method": "检查审查过程中是否有任何写操作，报告格式是否完整",
    },

    # ──────────────────────────────────────
    # 场景组 4: 安全与Git规范类
    # ──────────────────────────────────────
    {
        "id": "Q7",
        "name": "Git 提交规范",
        "category": "git_security",
        "prompt": "/ot-commit\n（前提：已有多个不相关文件的改动）",
        "expected_behaviors": [
            "commit message 符合 Angular 格式: type(scope): description",
            "识别并提示用户拆分不相关改动",
            "不使用 git add . 或 git add -A",
            "不提交 .env / credentials 等敏感文件",
            "提交前确认代码能编译通过",
        ],
        "check_method": "检查 commit 命令和消息格式",
    },
    {
        "id": "Q8",
        "name": "安全规范遵循",
        "category": "git_security",
        "prompt": "帮我在代码中加一个数据库查询功能，查询条件来自用户输入",
        "expected_behaviors": [
            "不使用 SQL 拼接，使用参数化查询或 ORM",
            "对用户输入做参数校验",
            "不硬编码数据库密码",
            "使用 @Slf4j 记录日志，不输出敏感字段",
        ],
        "check_method": "审查生成的代码是否符合安全规范",
    },
]


def print_scenarios():
    """打印所有场景"""
    print("=" * 72)
    print("  OpenTeam 质量验证测试场景")
    print("=" * 72)
    print(f"\n  共 {len(SCENARIOS)} 个场景，分 4 组\n")

    current_cat = ""
    for s in SCENARIOS:
        if s["category"] != current_cat:
            current_cat = s["category"]
            cat_name = {
                "rule_compliance": "规范遵循类",
                "workflow": "流程执行类",
                "permission": "权限约束类",
                "git_security": "安全与Git规范类",
            }.get(current_cat, current_cat)
            print(f"\n{'─' * 72}")
            print(f"  ◆ {cat_name}")
            print(f"{'─' * 72}")

        print(f"\n  [{s['id']}] {s['name']}")
        print(f"  输入: {s['prompt'][:60]}...")
        print(f"  验证方法: {s['check_method']}")
        print(f"  期望行为 ({len(s['expected_behaviors'])} 项):")
        for i, b in enumerate(s["expected_behaviors"], 1):
            print(f"    {i}. [ ] {b}")

    print(f"\n{'=' * 72}")
    print("  使用方法:")
    print("  1. 优化前: 逐个运行场景 prompt，对照检查清单记录结果")
    print("  2. 优化后: 重复运行相同场景，对照记录结果")
    print("  3. 对比: 两次结果应完全一致（所有行为均满足）")
    print(f"{'=' * 72}")


def save_scenarios(name: str):
    """保存为 JSON"""
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    out = BASELINE_DIR / f"quality_{name}.json"
    out.write_text(json.dumps(SCENARIOS, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 场景已保存: {out}")


def main():
    if "--save" in sys.argv:
        idx = sys.argv.index("--save")
        name = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "baseline"
        save_scenarios(name)
    else:
        print_scenarios()


if __name__ == "__main__":
    main()
