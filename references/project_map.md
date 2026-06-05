# 项目类型到图灵资源映射

Use this file after reading or summarizing the user's project. Match by actual project needs, not by fashionable keywords.

**Single source of truth for titles:** book titles live only in `catalog_seed.json`. Do NOT hardcode titles here. To recommend, take the `project_types` / `topics` below, filter `catalog_seed.json` items whose `project_types` or `topics` intersect, and present those. This keeps the catalog the one place to maintain.

## How to use

1. Read `inferred_project_types` and `gap_signals` from `scripts/inspect_project.py`.
2. For each project type, note the **advice focus** below (engineering guidance, not book titles).
3. Pull matching items from `catalog_seed.json` by intersecting `project_types`.
4. If `gap_signals` fired, prioritize the resource focus in the gap table — it overrides generic type matching, because it reflects a confirmed weakness, not just a present technology.

## 项目类型 → catalog 查询键 + advice focus

| 项目类型 | catalog `project_types` 查询键 | Advice focus |
| --- | --- | --- |
| AI 应用 / Agent / RAG | `ai-app`, `rag`, `agent`, `llm`, `semantic-search`, `production-ai` | scope control, evals before automation, retrieval quality, prompt/version management, hallucination handling, data privacy |
| Web 后端 / 服务端 / API | `backend`, `web-service`, `infrastructure`, `performance`, `security` | API contracts, tests, data model boundaries, authn/authz, observability, deployment assumptions |
| 前端工具 / 开发者工具 | `frontend-tool`, `education-tool`, `content-tool` | state model, user workflow, responsive constraints, accessibility, testable component boundaries |
| 算法学习 / 面试 / 计算机基础 | `algorithm-learning`, `interview-prep`, `cs-foundation` | topic sequence, deliberate practice, test cases, complexity analysis, explanation quality |
| 数据分析 / 机器学习 | `machine-learning`, `deep-learning`, `data-tool` | data leakage, baseline, metrics, reproducibility, model evaluation, documentation |
| 数学基础 / 研究型项目 | `math-foundation`, `research-prototype` | definitions, assumptions, proof obligations, experiment design, notation clarity |
| 学习计划 / 项目陪跑 | `learning-plan`, `personal-productivity`, `team-workflow` | one deliverable per week, reading tied to code tasks, retrospectives, checkpoints |

## Gap signals → resource focus

When `scripts/inspect_project.py` reports a `gap_signal`, confirm it by reading the cited files, then match `catalog_seed.json` items whose `topics` cover the focus. Recommend because of the gap, not the buzzword.

| gap_signal id | 含义 | catalog `topics` 方向 |
| --- | --- | --- |
| `ai-without-evaluation` | 在调用 LLM 但没有评估闭环 | `评估`, `AI工程`, `AI系统`, `模型产品化` |
| `auth-without-crypto-foundation` | 有认证逻辑但缺成熟加密基础 | `密码学`, `安全`, `加密`, `认证` |
| `db-access-without-orm` | 裸数据库访问，SQL 注入与数据层风险 | `安全`, `后端`, `数据结构` |
| `no-test-coverage` | 有源码但无测试 | `工程实践`, `算法`（用可测的小问题练测试） |

## Non-book assets

视频课/共学营/图灵直播 不在 `catalog_seed.json` 里（时效性强）。需要时用 `scripts/fetch_ituring_public.py --book <id>` 读 `related_live_courses`，或引导到官网，不要凭记忆给出课程名。
