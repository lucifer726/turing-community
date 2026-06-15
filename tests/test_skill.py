#!/usr/bin/env python3
"""Offline test suite for the turing-community skill scripts.

Uses only the standard library (unittest) to match the skill's zero-dependency
design. No network access: the fetch_ituring_public tests cover only its pure
parsing/fallback helpers, never live HTTP.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import fetch_ituring_public  # noqa: E402
import inspect_project  # noqa: E402
import scaffold_learning_plan  # noqa: E402


def _write(root: Path, rel: str, body: str = "") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


class InspectProjectTests(unittest.TestCase):
    def test_ai_rag_project_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "requirements.txt", "openai>=1.0\nlangchain\nchromadb\n")
            _write(root, "app.py", "import openai\n")
            report = inspect_project.inspect(root, max_files=800)

            self.assertIn("python", report["languages"])
            self.assertIn("ai-app", report["inferred_project_types"])
            self.assertIn("rag", report["inferred_project_types"])
            gap_ids = {g["id"] for g in report["gap_signals"]}
            self.assertIn("ai-without-evaluation", gap_ids)
            self.assertIn("no-test-coverage", gap_ids)

    def test_tests_present_clears_coverage_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/core.py", "def add(a, b):\n    return a + b\n")
            _write(root, "tests/test_core.py", "def test_add():\n    assert True\n")
            report = inspect_project.inspect(root, max_files=800)

            self.assertIn("has-tests", report["inferred_project_types"])
            gap_ids = {g["id"] for g in report["gap_signals"]}
            self.assertNotIn("no-test-coverage", gap_ids)

    def test_node_backend_auth_and_db_signals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                "dependencies": {"express": "^4.0.0", "pg": "^8.0.0", "jsonwebtoken": "^9.0.0"}
            }
            _write(root, "package.json", json.dumps(manifest))
            report = inspect_project.inspect(root, max_files=800)

            self.assertIn("backend", report["inferred_project_types"])
            gap_ids = {g["id"] for g in report["gap_signals"]}
            self.assertIn("auth-without-crypto-foundation", gap_ids)
            self.assertIn("db-access-without-orm", gap_ids)


class LearningPlanTests(unittest.TestCase):
    def test_build_plan_renders_gaps_and_weeks(self):
        report = {
            "inferred_project_types": ["ai-app", "rag"],
            "gap_signals": [
                {"id": "ai-without-evaluation", "evidence": "no eval found"},
                {"id": "no-test-coverage", "evidence": "no tests found"},
            ],
            "languages": ["python"],
            "frameworks": [],
        }
        plan = scaffold_learning_plan.build_plan(report, weeks=4, goal="ship RAG demo")

        self.assertIn("周计划", plan)
        self.assertIn("建立 AI 评估闭环", plan)
        self.assertIn("ai-without-evaluation", plan)
        self.assertIn("ship RAG demo", plan)
        # one table row per week
        for week in range(1, 5):
            self.assertIn(f"| {week} |", plan)


class TeamSkillMapTests(unittest.TestCase):
    def test_rollup_across_repos(self):
        team_skill_map = _import_team_skill_map()
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            _write(Path(a), "main.py", "print('a')\n")
            _write(Path(b), "service.py", "print('b')\n")
            result = team_skill_map.build_map([a, b, "/no/such/path"], max_files=800)

            self.assertEqual(result["project_count"], 2)
            self.assertEqual(result["skipped_paths"], ["/no/such/path"])
            self.assertTrue(result["team_gap_signals"])


class CatalogSeedTests(unittest.TestCase):
    def test_catalog_is_well_formed(self):
        catalog = json.loads((ROOT / "references" / "catalog_seed.json").read_text(encoding="utf-8"))
        items = catalog.get("items")
        self.assertIsInstance(items, list)
        self.assertGreater(len(items), 0)
        for item in items:
            self.assertTrue(item.get("title"), "every item needs a title")
            self.assertIsInstance(item.get("topics", []), list)
            self.assertIsInstance(item.get("project_types", []), list)


class FetchPublicPureTests(unittest.TestCase):
    def test_normalize_book_builds_url_and_price(self):
        book = fetch_ituring_public.normalize_book({
            "id": 3404,
            "name": "AI工程：大模型应用开发实战",
            "bookEditionPrices": [{"key": "Paper", "name": "159.80"}],
            "coverKey": "abc123",
        })
        self.assertEqual(book["title"], "AI工程：大模型应用开发实战")
        self.assertEqual(book["price"], "159.80")
        self.assertTrue(book["official_url"].endswith("/book/3404"))
        self.assertTrue(book["cover_url"].endswith("abc123"))

    def test_normalize_book_handles_missing_fields(self):
        book = fetch_ituring_public.normalize_book({})
        self.assertIsNone(book["official_url"])
        self.assertIsNone(book["cover_url"])
        self.assertIsNone(book["price"])

    def test_graceful_error_shape(self):
        result = fetch_ituring_public.graceful_error(RuntimeError("boom"), fallback_url="https://x/book")
        self.assertEqual(result["status"], "unavailable")
        self.assertIn("RuntimeError", result["error"])
        self.assertEqual(result["fallback_url"], "https://x/book")


def _import_team_skill_map():
    import importlib

    return importlib.import_module("team_skill_map")


if __name__ == "__main__":
    unittest.main()
