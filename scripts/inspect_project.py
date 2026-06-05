#!/usr/bin/env python3
"""Read-only project inspector for the turing-community skill."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


EXCLUDE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "target",
    "__pycache__",
}

MANIFESTS = {
    "package.json": "node",
    "pnpm-lock.yaml": "node",
    "yarn.lock": "node",
    "requirements.txt": "python",
    "pyproject.toml": "python",
    "Pipfile": "python",
    "poetry.lock": "python",
    "Cargo.toml": "rust",
    "go.mod": "go",
    "pom.xml": "java",
    "build.gradle": "java",
    "build.gradle.kts": "java",
    "Gemfile": "ruby",
    "composer.json": "php",
    "Dockerfile": "container",
    "docker-compose.yml": "container",
    "compose.yml": "container",
}

EXT_LANG = {
    ".py": "python",
    ".ipynb": "python",
    ".js": "javascript",
    ".jsx": "react",
    ".ts": "typescript",
    ".tsx": "react",
    ".vue": "vue",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".swift": "swift",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".sql": "sql",
}

FRAMEWORK_MARKERS = {
    "next": ["next.config.js", "next.config.mjs", "next.config.ts"],
    "vite": ["vite.config.js", "vite.config.ts", "vite.config.mjs"],
    "react": ["src/App.jsx", "src/App.tsx"],
    "vue": ["vue.config.js", "src/App.vue"],
    "fastapi": ["main.py", "app/main.py"],
    "django": ["manage.py"],
    "flask": ["wsgi.py"],
    "pytest": ["pytest.ini", "conftest.py"],
    "docker": ["Dockerfile", "docker-compose.yml", "compose.yml"],
}

AI_KEYWORDS = {
    "openai": "ai-app",
    "langchain": "ai-app",
    "llamaindex": "ai-app",
    "transformers": "ai-app",
    "chromadb": "rag",
    "faiss": "rag",
    "pinecone": "rag",
    "qdrant": "rag",
    "sklearn": "machine-learning",
    "tensorflow": "machine-learning",
    "torch": "machine-learning",
    "pandas": "data-tool",
}


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def safe_read(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def walk_files(root: Path, max_files: int) -> list[Path]:
    files: list[Path] = []
    for current_root, dirs, names in os.walk(root):
        current = Path(current_root)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not should_skip(current / d)]
        for name in names:
            path = current / name
            if should_skip(path):
                continue
            files.append(path)
            if len(files) >= max_files:
                return files
    return files


def detect_dependencies(root: Path, manifests: list[str]) -> list[str]:
    deps: set[str] = set()
    package_json = root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(safe_read(package_json))
            for section in ("dependencies", "devDependencies", "peerDependencies"):
                deps.update((data.get(section) or {}).keys())
        except json.JSONDecodeError:
            pass
    for req_name in ("requirements.txt",):
        req = root / req_name
        if req.exists():
            for line in safe_read(req).splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    deps.add(line.split("==")[0].split(">=")[0].split("[")[0].strip())
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        text = safe_read(pyproject).lower()
        for keyword in AI_KEYWORDS:
            if keyword in text:
                deps.add(keyword)
    return sorted(d for d in deps if d)


def has_test_file(relative_file: str) -> bool:
    path = Path(relative_file)
    return (
        "test" in path.parts
        or "tests" in path.parts
        or path.name.startswith("test_")
        or ".test." in path.name
        or path.name.endswith("_test.py")
        or path.name.endswith("_test.go")
    )


def infer_project_types(languages: set[str], frameworks: set[str], deps: list[str], relative_files: list[str]) -> list[str]:
    types: set[str] = set()
    dep_text = " ".join(deps).lower()
    for keyword, project_type in AI_KEYWORDS.items():
        if keyword in dep_text:
            types.add(project_type)
    if {"react", "vue"} & languages or {"next", "vite", "react", "vue"} & frameworks:
        types.add("frontend-tool")
    node_backend = any(m in dep_text for m in ("express", "koa", "fastify", "nestjs", "@nestjs", "hapi"))
    if {"fastapi", "django", "flask"} & frameworks or node_backend or any(lang in languages for lang in ("go", "java", "rust")):
        types.add("backend")
    if "sql" in languages or "pandas" in dep_text:
        types.add("data-tool")
    if any(has_test_file(path) for path in relative_files):
        types.add("has-tests")
    if not types:
        types.add("general-software")
    return sorted(types)


def detect_gap_signals(
    languages: set[str],
    deps: list[str],
    relative_files: list[str],
    tests: list[str],
) -> list[dict[str, Any]]:
    """Detect anti-patterns / missing-foundation signals, not just present keywords."""
    signals: list[dict[str, Any]] = []
    dep_text = " ".join(deps).lower()
    dep_tokens = {d.lower() for d in deps}
    file_text = " ".join(relative_files).lower()

    ai_libs = [d for d in ("openai", "anthropic", "langchain", "llamaindex", "transformers") if d in dep_text]
    has_eval = "eval" in file_text or any("eval" in t.lower() for t in tests)
    if ai_libs and not has_eval:
        signals.append({
            "id": "ai-without-evaluation",
            "evidence": f"检测到 LLM 依赖 {ai_libs}，但未发现 eval/评估脚本或相关测试。",
            "resource_focus": ["评估闭环", "AI 工程化", "输出可靠性"],
        })

    auth_markers = [m for m in ("auth", "login", "jwt", "oauth", "password", "session", "jsonwebtoken") if m in file_text or m in dep_text]
    crypto_markers = [m for m in ("cryptography", "bcrypt", "passlib", "argon2", "pyjwt", "jose", "hashlib") if m in dep_text or m in file_text]
    if auth_markers and not crypto_markers:
        signals.append({
            "id": "auth-without-crypto-foundation",
            "evidence": f"出现认证相关标识 {auth_markers}，但未见成熟加密/哈希库。",
            "resource_focus": ["密码学基础", "认证与加密", "数据保护"],
        })

    db_markers = [m for m in ("psycopg2", "pymysql", "mysql", "sqlite3", "asyncpg", "mongodb") if m in dep_text]
    if "pg" in dep_tokens:  # node 'pg' — exact match, too short for substring search
        db_markers.append("pg")
    orm_markers = [m for m in ("sqlalchemy", "django", "peewee", "tortoise", "prisma", "sequelize", "typeorm", "mongoose") if m in dep_text]
    if ("sql" in languages or db_markers) and not orm_markers:
        signals.append({
            "id": "db-access-without-orm",
            "evidence": "检测到数据库访问但未使用 ORM，需关注 SQL 注入风险与数据层边界。",
            "resource_focus": ["数据层设计", "安全", "SQL 注入防护"],
        })

    if languages and not tests:
        signals.append({
            "id": "no-test-coverage",
            "evidence": "有源码但未发现测试文件。",
            "resource_focus": ["测试策略", "工程实践"],
        })

    return signals


def inspect(root: Path, max_files: int) -> dict[str, Any]:
    root = root.resolve()
    files = walk_files(root, max_files=max_files)
    rel_files = [str(p.relative_to(root)) for p in files]

    manifest_names = sorted(name for name in MANIFESTS if (root / name).exists())
    languages: set[str] = set()
    for p in files:
        lang = EXT_LANG.get(p.suffix.lower())
        if lang:
            languages.add(lang)
    for name in manifest_names:
        languages.add(MANIFESTS[name])

    frameworks: set[str] = set()
    for framework, markers in FRAMEWORK_MARKERS.items():
        if any((root / marker).exists() for marker in markers):
            frameworks.add(framework)

    deps = detect_dependencies(root, manifest_names)
    project_types = infer_project_types(languages, frameworks, deps, rel_files)
    docs = [f for f in rel_files if Path(f).name.lower() in {"readme.md", "docs", "architecture.md"} or f.startswith("docs/")]
    tests = [f for f in rel_files if has_test_file(f)]
    gap_signals = detect_gap_signals(languages, deps, rel_files, tests)

    return {
        "root": str(root),
        "file_count_sampled": len(files),
        "manifests": manifest_names,
        "languages": sorted(languages),
        "frameworks": sorted(frameworks),
        "notable_dependencies": deps[:80],
        "inferred_project_types": project_types,
        "gap_signals": gap_signals,
        "docs": docs[:30],
        "tests": tests[:40],
        "sample_files": rel_files[:80],
        "notes": [
            "Read-only heuristic summary; inspect important files directly before making high-risk engineering claims.",
            "Use inferred_project_types with references/project_map.md for Turing resource matching.",
            "gap_signals are heuristic anti-pattern hints; confirm by reading the cited files before recommending resources.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a project without modifying it.")
    parser.add_argument("path", nargs="?", default=".", help="Project directory to inspect")
    parser.add_argument("--max-files", type=int, default=800, help="Maximum files to sample")
    args = parser.parse_args()

    root = Path(args.path)
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    print(json.dumps(inspect(root, args.max_files), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
