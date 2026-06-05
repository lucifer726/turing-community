# 来源、版权与官网增强策略

## Allowed Sources

- Built-in seed catalog in `catalog_seed.json`.
- Official public pages on `https://www.ituring.com.cn/`.
- Public sample chapters, public book resources, public errata, public articles, public livestream/course pages.
- Public book detail metadata from `api/Book/{id}` (publish date, table-of-contents preview, e-book formats, related livestreams, companion-resource listings, public view/favorite counts).
- User-provided project files and user-provided context.

## Disallowed Actions

- Do not package copyrighted book body text into the skill.
- Do not reconstruct chapters from memory or snippets.
- Do not download, distribute, or help bypass access to paid ebooks.
- Do not bypass login, captcha, paywalls, rate limits, or technical access controls.
- Do not scrape private account data, orders, shelves, coupons, or personal information.
- Do not surface companion-resource download URLs as if bundled with this skill; list resource names/sizes and route downloads to the official book page.
- gap_signals from `inspect_project.py` are heuristic; confirm by reading the cited files and never state them as definitive defects.

## Attribution Rules

- If a recommendation comes from built-in catalog data, say it is based on the built-in seed catalog.
- If a recommendation comes from a public page lookup, include the official URL.
- If availability, price, publication date, or course status matters, verify on the official site before stating it as current.
- If lookup fails, say: "官网公开信息查询失败，以下基于内置资料包。"

## Engineering Advice Boundary

The skill may provide general engineering advice based on project inspection. It must not imply that such advice is quoted from or guaranteed by a Turing book unless the information is available in public metadata or supplied by the user.

Use wording such as:

- "工程建议：..."
- "图灵资源匹配：..."
- "推荐依据来自公开书目信息/内置资料包。"
