# turing-community

一个 [Claude](https://claude.com/claude-code) **Skill**：把开发者的真实代码项目和图灵社区（[ituring.com.cn](https://www.ituring.com.cn/)）的公开知识资产连接起来——诊断项目、定位知识缺口、按理由推荐图灵图书/公开资源，并为图灵运营把项目场景转成读者内容。

> 推荐基于公开书目信息与项目匹配度，不替代完整阅读；涉及购买、电子书、样章、勘误、课程报名以图灵社区官方页面为准。

---

## 给普通用户

### 这是什么

一个装进 Claude 的技能包。当你把一个代码项目（或一个项目想法）交给 Claude 时，它会：

- **只读诊断**你的项目：语言、框架、项目类型，以及"反模式缺口"（比如在调 LLM 却没有评估闭环、有登录却没用加密库）。
- **按理由推荐**图灵的书或公开资源——说明"这本书解决你项目里的哪个问题"，而不是甩一句"必读"。
- **生成可追踪的学习计划**（周计划：写代码 / 读书 / 验证）。
- 给图灵运营：把项目场景转成直播选题、社群话题、新书宣传角度。

它**不会**：泄露受版权保护的书正文、帮你绕过登录/付费、伪造价格或库存。

### 安装

需要本机已安装 Claude Code 与 `python3`（脚本仅用标准库，无需第三方依赖）。

```bash
# 个人级（所有项目可用）
git clone https://github.com/lucifer726/turing-community.git ~/.claude/skills/turing-community

# 或项目级（只在某个项目里可用）
git clone https://github.com/lucifer726/turing-community.git .claude/skills/turing-community
```

装好后 Claude 会自动按需触发，无需手动开启。

### 怎么用

直接用自然语言描述你的项目和目标，例如：

- "我在做一个 RAG 客服 demo，用 openai + chromadb，准备上线，怎么保证回答质量？"
- "我想从零学会做大模型应用，有 Python 基础，给我一条学习路径。"
- "帮我看看 `./my-project` 这个仓库，缺什么基础该补哪本图灵书？"
- "我读到密码学里的'盐值'，我的登录功能怎么用上？"
- （运营）"想给后端开发者做一场图灵直播，帮我策划。"

### 功能概览

| 能力 | 说明 |
|------|------|
| 项目诊断 | 只读扫描仓库，推断技术栈、项目类型、缺口信号 |
| 资源匹配 | 按项目类型 / 缺口匹配图灵图书，附匹配理由与官方链接 |
| 最新书查询 | 拉取图灵官网"最新上架"书目 |
| 书详情查询 | 出版日期、目录预览、电子书格式、配套资源、关联直播课 |
| 学习计划 | 生成可追踪的周计划文件 |
| 团队技能图谱 | 跨多个仓库汇总团队共性缺口，作为共学营/书单依据 |
| 运营内容 | 直播策划、社群话题、新书宣传、双向桥接（书 → 项目） |

---

## 给 Agent（调用本 Skill 的助手）

> 完整规则见 [`SKILL.md`](SKILL.md)；本节是面向调用方的速查。

### 何时触发

帮助 AI 编程用户做：项目诊断、技术学习路径、图书/资源推荐、读者服务，或为图灵运营生成内容。关键词：图灵社区、图灵图书、技术书推荐、AI 编程项目学习、project-aware learning、Turing operations。

### 工作流（摘要）

1. **理解项目**：有本地仓库就先只读检查 `scripts/inspect_project.py <path>`，重点读 `gap_signals`（启发式反模式，**需读引用文件确认**后再据此匹配资源；它优先于泛化的类型匹配）。
2. **选引用**：见下表。
3. **可选官网增强**：用 `fetch_ituring_public.py` 查公开元数据；查不到就用内置 catalog 并明确说明。
4. **产出**：区分"工程建议"与"图灵资源推荐"，每条推荐说明匹配理由 + 官方链接 + 来源（内置 seed / 公开页）。

### 脚本接口

所有脚本仅依赖 Python 标准库，只读、不修改用户项目（`scaffold_learning_plan.py --out` 除外，它写计划文件）。

| 脚本 | 命令 | 用途 |
|------|------|------|
| `inspect_project.py` | `python3 scripts/inspect_project.py <path>` | 只读诊断 → JSON：`languages` / `frameworks` / `inferred_project_types` / `gap_signals` |
| `fetch_ituring_public.py` | `--latest --limit N` | 官网最新上架书目 |
| | `--book <id>` | 单本详情：`publish_date` / 目录预览 / 电子书格式 / `related_live_courses` / 配套资源 / 热度 |
| | `--query "<词>" --limit N` | 按关键词搜公开书目元数据 |
| | `--homepage` | 首页标题/描述 |
| `scaffold_learning_plan.py` | `inspect_project.py <p> \| scaffold_learning_plan.py --weeks N --goal "..." [--out learning_plan.md]` | 由诊断生成缺口驱动的周计划 |
| `team_skill_map.py` | `python3 scripts/team_skill_map.py <repo1> <repo2> ...` | 跨仓库汇总语言/类型/缺口频次 |

查询失败时脚本返回 `status: unavailable` + `fallback_url`，不抛异常——此时改用内置 catalog 并声明"官网公开信息查询失败，以下基于内置资料包"。

### 引用文件

| 文件 | 何时读 |
|------|--------|
| [`references/brand.md`](references/brand.md) | 品牌定位、对外表达原则 |
| [`references/catalog_seed.json`](references/catalog_seed.json) | 内置书目（标题的唯一来源；非图书资产动态获取） |
| [`references/project_map.md`](references/project_map.md) | 项目类型 / 缺口信号 → 资源匹配逻辑 |
| [`references/reader_flows.md`](references/reader_flows.md) | 找书、学习路径、项目卡住、双向桥接 |
| [`references/ops_playbooks.md`](references/ops_playbooks.md) | 运营内容：直播、社群、新书宣传、开源项目反推 |
| [`references/source_policy.md`](references/source_policy.md) | 来源、版权与官网增强边界 |

### 边界（必须遵守）

- 不包含、不重建受版权保护的书正文；不声称用过非公开书内容。
- 不绕过登录、付费墙、验证码、限流或访问控制；不帮下载付费电子书或分发受保护资源。
- 配套资源只列名称/大小并指向官方书页，不当作本 skill 自带分发。
- 账户、订单、退款、版权、售后问题一律引导到图灵社区官方渠道。
- `gap_signals` 是启发式提示，需读被引用文件确认后才能当作缺陷陈述。

---

## 仓库结构

```
turing-community/
├── SKILL.md                 # Skill 定义与工作流（Claude 入口）
├── README.md
├── agents/openai.yaml       # 接入元数据
├── references/              # 品牌、书目、匹配逻辑、流程、版权策略
└── scripts/                 # 只读诊断与公开元数据查询工具
```

## 数据来源与免责声明

书目推荐基于内置 seed catalog 与图灵社区**公开**页面/接口元数据。本仓库不包含任何受版权保护的书籍正文。价格、库存、样章、勘误、课程状态以 [图灵社区官方页面](https://www.ituring.com.cn/) 为准。本项目与北京图灵文化发展有限公司无官方隶属关系，图灵社区相关名称与内容版权归其所有。
