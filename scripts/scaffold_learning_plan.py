#!/usr/bin/env python3
"""Scaffold a trackable learning plan from an inspect_project.py JSON report.

Reads the JSON emitted by scripts/inspect_project.py (via --inspect FILE or stdin)
and prints a learning_plan.md skeleton: project read, gap-driven milestones, a
week-by-week table (code / reading / validation task), and checkpoints.

Book titles are matched from references/catalog_seed.json; official links and the
newest related books should be filled in afterwards with fetch_ituring_public.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CATALOG = Path(__file__).resolve().parent.parent / "references" / "catalog_seed.json"

GAP_TITLE = {
    "ai-without-evaluation": "建立 AI 评估闭环",
    "auth-without-crypto-foundation": "补齐认证与加密基础",
    "db-access-without-orm": "加固数据层与防注入",
    "no-test-coverage": "建立测试基线",
}

GAP_FOCUS_TOPICS = {
    "ai-without-evaluation": ["评估", "AI工程", "AI系统", "模型产品化"],
    "auth-without-crypto-foundation": ["密码学", "安全", "加密", "认证"],
    "db-access-without-orm": ["安全", "后端", "数据结构"],
    "no-test-coverage": ["工程实践", "算法"],
}


def load_catalog() -> list[dict[str, Any]]:
    try:
        return json.loads(CATALOG.read_text(encoding="utf-8")).get("items", [])
    except OSError:
        return []


def match_titles(items: list[dict[str, Any]], project_types: list[str], topics: list[str]) -> list[str]:
    want_types, want_topics = set(project_types), set(topics)
    titles: list[str] = []
    for it in items:
        if (want_types & set(it.get("project_types", []))) or (want_topics & set(it.get("topics", []))):
            titles.append(it.get("title", ""))
    return [t for t in titles if t]


def read_report(path: str | None) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    return json.loads(text)


def build_plan(report: dict[str, Any], weeks: int, goal: str | None) -> str:
    types = report.get("inferred_project_types", [])
    gaps = report.get("gap_signals", [])
    langs = ", ".join(report.get("languages", [])) or "未知"
    frameworks = ", ".join(report.get("frameworks", [])) or "无"
    items = load_catalog()

    milestones: list[tuple[str, str, list[str]]] = []
    for g in gaps:
        titles = match_titles(items, [], GAP_FOCUS_TOPICS.get(g["id"], []))
        milestones.append((GAP_TITLE.get(g["id"], g["id"]), g.get("evidence", ""), titles))
    for t in types:
        milestones.append((f"深化 {t}", "围绕该项目类型补齐工程能力。", match_titles(items, [t], [])))

    out: list[str] = []
    out.append(f"# 学习计划（{weeks} 周）")
    out.append("")
    out.append("> 由 scripts/scaffold_learning_plan.py 基于项目诊断生成。书目匹配来自内置 catalog；")
    out.append("> 官方链接、价格与最新相关书请用 scripts/fetch_ituring_public.py 补全后再确认。")
    out.append("")
    out.append("## 项目诊断")
    out.append(f"- 技术栈：{langs}（框架：{frameworks}）")
    out.append(f"- 项目类型：{', '.join(types) or '未识别'}")
    if goal:
        out.append(f"- 目标：{goal}")
    if gaps:
        out.append("- 关键缺口：")
        for g in gaps:
            out.append(f"  - `{g['id']}`：{g.get('evidence', '')}")
    out.append("")
    out.append("## 周计划")
    out.append("")
    out.append("| 周 | 主题 | Code task | Reading task | Validation task |")
    out.append("| --- | --- | --- | --- | --- |")
    for w in range(1, weeks + 1):
        if milestones:
            title, _why, titles = milestones[(w - 1) % len(milestones)]
        else:
            title, titles = "自定主题", []
        reading = "；".join(titles[:2]) if titles else "（按 catalog topics 匹配后填）"
        out.append(f"| {w} | {title} | _待填：一个可运行产出_ | {reading} | _待填：如何验证（测试/curl/指标）_ |")
    out.append("")
    out.append("## Checkpoints")
    out.append("- 每周一个可演示产出（PR / demo / 截图）。")
    out.append("- 每周末复盘：完成了什么、卡在哪、下周怎么调。")
    out.append("- 阅读始终绑定当周 code task，不脱离项目空读。")
    out.append("")
    out.append("## 资源补全")
    out.append("- `scripts/fetch_ituring_public.py --query <书名>` 补官方链接与价格。")
    out.append("- `scripts/fetch_ituring_public.py --latest` 查看是否有更新的相关新书。")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a learning plan from an inspect_project report.")
    parser.add_argument("--inspect", help="Path to inspect_project.py JSON output (default: stdin)")
    parser.add_argument("--weeks", type=int, default=4, help="Number of weeks in the plan")
    parser.add_argument("--goal", help="Target deliverable for the plan")
    parser.add_argument("--out", help="Write to this file instead of stdout")
    args = parser.parse_args()

    try:
        report = read_report(args.inspect)
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"failed to read inspect report: {error}")

    plan = build_plan(report, max(1, args.weeks), args.goal)
    if args.out:
        Path(args.out).write_text(plan + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
