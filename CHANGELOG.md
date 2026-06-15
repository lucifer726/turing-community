# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 风格。

## [Unreleased]

### Added
- MIT 开源许可证。
- 离线测试套件（`tests/test_skill.py`，仅用标准库 unittest）覆盖项目诊断、学习计划生成、团队技能图谱、内置书目结构校验，以及公开元数据解析的纯函数逻辑。
- GitHub Actions CI：在 Python 3.10 / 3.11 / 3.12 上运行测试并对诊断脚本做自检冒烟测试。
- 贡献指南（`CONTRIBUTING.md`）、Issue / PR 模板。

### Changed
- README 增加状态徽章与测试说明。

## [0.1.0]

### Added
- 初版 turing-community Claude Skill：项目只读诊断（`inspect_project.py`）、公开元数据查询（`fetch_ituring_public.py`）、学习计划脚手架（`scaffold_learning_plan.py`）、团队技能图谱（`team_skill_map.py`）。
- 内置书目种子数据与品牌/匹配/流程/版权策略引用文件。
- `SKILL.md` 工作流定义与 README 功能演示。
