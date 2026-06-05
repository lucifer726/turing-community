# 运营复用流程

Use this file when the user is acting as Turing staff, editor, marketer, community operator, or wants campaign/content planning.

## 从开源项目反推选题

Input: a public repo path or clone (read-only). Reuse the developer-side inspection for ops content.

1. Run `scripts/inspect_project.py <path>` to get stack, project types, and `gap_signals`.
2. Turn `gap_signals` into a reader profile and pain point — the most frequent/severe gap is the sharpest angle.
3. Produce:
   - reader profile (who hits this kind of project problem),
   - 1 livestream topic aimed at the top gap,
   - 3 community discussion questions,
   - 1 restrained book hook, matched from `catalog_seed.json` by the gap's topics.
4. Run `scripts/fetch_ituring_public.py --latest` to check for a more timely new book to anchor on.

Boundary: only public repos; never scrape private code or account data; never present engineering advice as guaranteed by a book.

## 新书宣传

Input needed: book title, audience, release stage, comparable projects, channel.

Output:

- Core reader scenario
- Project pain point
- Book hook
- 3 social post angles
- 1 livestream topic
- 5 community discussion questions
- restrained official CTA

Keep claims tied to public metadata or supplied materials.

## 直播策划

Map from project scenario:

- AI app prototype failing evaluation -> "从 Demo 到可靠 AI 应用"
- Backend performance issue -> "一次服务端性能排查怎么做"
- Algorithm learning fatigue -> "把算法学成一个可运行项目"
- Math anxiety in ML -> "AI 开发者需要怎样补数学"

For each livestream:

- audience,
- promise,
- outline,
- reader interaction,
- related Turing resources,
- follow-up community task.

## 社群话题

Good topics:

- "你的 AI 项目现在卡在哪个环节？"
- "你做过最有效的一次项目复盘是什么？"
- "一个算法题怎样变成一个可展示的小工具？"
- "从书到项目，你最需要哪种陪跑服务？"

Avoid topics that require sharing private code, paid content, or personal account data.

## 短视频 / 小红书 / 公众号

Use compact formulas:

- Problem -> Misconception -> Better mental model -> Turing resource -> small next action.
- Project screenshot/idea -> technical gap -> learning path -> community invitation.
- Author/translator perspective -> reader problem -> book value -> official link.

Do not use fear-based or exaggerated claims.
