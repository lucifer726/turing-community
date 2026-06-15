# 贡献指南

欢迎为 turing-community 这个 Claude Skill 贡献代码、书目数据或文档改进。

## 设计约束（请先读）

- **零第三方依赖**：所有脚本只用 Python 标准库，测试也是。请不要引入 `requirements.txt` 依赖。
- **只读、不越权**：诊断脚本不得修改用户项目（`scaffold_learning_plan.py --out` 写计划文件除外）。不绕过登录/付费墙，不分发受版权保护的书籍正文，详见 [`references/source_policy.md`](references/source_policy.md)。
- **推荐要有理由**：任何资源推荐都要说明"匹配了项目的哪个缺口/阶段/技术栈"，附官方链接与来源。

## 本地开发

```bash
git clone https://github.com/lucifer726/turing-community.git
cd turing-community

# 运行测试（无需联网、无需安装依赖）
python -m unittest discover -s tests -v

# 用项目自己的工具诊断自己
python scripts/inspect_project.py .
```

需要 Python 3.10+。

## 提交前检查

1. `python -m unittest discover -s tests` 全绿。
2. 新增/修改脚本逻辑时补对应测试（参考 `tests/test_skill.py`）。
3. 改动只读边界或网络行为时，同步更新 [`SKILL.md`](SKILL.md) 与 `references/source_policy.md`。
4. 一个 PR 只做一件事，commit message 用祈使句说明动机。

## 想加一本书 / 资源？

编辑 [`references/catalog_seed.json`](references/catalog_seed.json)，每个条目需包含 `title`、`topics`、`project_types`、`official_url` 等字段（CI 会校验结构）。只填**公开**元数据与官方链接，不要复制书籍正文。

## 报告问题

用 issue 模板描述：你的项目场景、期望的诊断/推荐、实际得到的结果。
