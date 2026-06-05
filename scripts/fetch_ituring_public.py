#!/usr/bin/env python3
"""Fetch public Turing Community metadata without login or paywall access."""

from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from typing import Any


WWW_BASE = "https://www.ituring.com.cn"
API_BASE = "https://api.ituring.com.cn"
USER_AGENT = "turing-community-skill/0.1 (+public metadata lookup)"


def request_text(url: str, accept: str = "application/json,text/plain,*/*") -> tuple[int, str, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": accept,
            "Origin": WWW_BASE,
            "Referer": f"{WWW_BASE}/",
        },
    )
    with urllib.request.urlopen(req, timeout=12) as response:
        body = response.read(1_500_000).decode("utf-8", errors="ignore")
        return response.status, response.headers.get("content-type", ""), body


def homepage() -> dict[str, Any]:
    status, content_type, body = request_text(f"{WWW_BASE}/", accept="text/html,*/*")
    title = ""
    description = ""
    title_match = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
    if title_match:
        title = re.sub(r"\s+", " ", unescape(title_match.group(1))).strip()
    desc_match = re.search(r'<meta\b[^>]*\bname=["\']?description["\']?[^>]*\bcontent=(["\']?)(.*?)\1(?=\s|/?>)', body, re.I)
    if desc_match:
        description = unescape(desc_match.group(2).strip(" \"'"))
    return {
        "status": "ok",
        "source": f"{WWW_BASE}/",
        "http_status": status,
        "content_type": content_type,
        "title": title,
        "description": description,
    }


def normalize_book(item: dict[str, Any]) -> dict[str, Any]:
    book_id = item.get("id")
    prices = item.get("bookEditionPrices") or []
    paper_price = next((p.get("name") for p in prices if isinstance(p, dict) and p.get("key") == "Paper"), None)
    return {
        "id": book_id,
        "title": item.get("name"),
        "authors": item.get("authorNameString") or ", ".join(a.get("name", "") for a in item.get("authors", []) if isinstance(a, dict)),
        "translators": item.get("translatorNameString"),
        "isbn": item.get("isbn"),
        "status": item.get("bookStatus"),
        "price": paper_price,
        "abstract": item.get("abstract"),
        "official_url": f"{WWW_BASE}/book/{book_id}" if book_id else None,
        "cover_url": f"https://file.ituring.com.cn/LargeCover/{item.get('coverKey')}" if item.get("coverKey") else None,
    }


def search_books(query: str, limit: int) -> dict[str, Any]:
    params = urllib.parse.urlencode({"q": query})
    url = f"{API_BASE}/api/Search/Books?{params}"
    status, content_type, body = request_text(url)
    if "json" not in content_type.lower():
        raise RuntimeError(f"unexpected content type from public API: {content_type}")
    data = json.loads(body)
    if not isinstance(data, list):
        raise RuntimeError("unexpected public API response shape")
    return {
        "status": "ok",
        "source": url,
        "http_status": status,
        "query": query,
        "results": [normalize_book(item) for item in data[:limit] if isinstance(item, dict)],
        "note": "Public metadata only. Verify availability, price, samples, resources, and errata on official pages.",
    }


def latest_books(limit: int) -> dict[str, Any]:
    url = f"{API_BASE}/api/Book?sort=newest"
    status, content_type, body = request_text(url)
    if "json" not in content_type.lower():
        raise RuntimeError(f"unexpected content type from public API: {content_type}")
    data = json.loads(body)
    items = data.get("bookItems") if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise RuntimeError("unexpected public API response shape")
    return {
        "status": "ok",
        "source": url,
        "http_status": status,
        "results": [normalize_book(item) for item in items[:limit] if isinstance(item, dict)],
        "note": "Ordered by the official 'newest' listing; no publish-date field is exposed, so recency follows the site's own order. Verify availability, price, samples, and errata on official pages.",
    }


def book_detail(book_id: int) -> dict[str, Any]:
    url = f"{API_BASE}/api/Book/{book_id}"
    status, content_type, body = request_text(url)
    if "json" not in content_type.lower():
        raise RuntimeError(f"unexpected content type from public API: {content_type}")
    item = json.loads(body)
    if not isinstance(item, dict) or not item.get("id"):
        raise RuntimeError("unexpected public API response shape")

    detail = normalize_book(item)
    detail.pop("status", None)  # detail endpoint returns an opaque numeric code; use availability flags instead
    formats = [label for label, ok in (("EPUB", item.get("supportEpub")), ("MOBI", item.get("supportMobi")), ("PDF", item.get("supportPdf"))) if ok]
    tags = [t.get("name") for t in (item.get("tags") or []) if isinstance(t, dict) and t.get("name")]
    categories = [c.get("name") for c in (item.get("categories") or []) if isinstance(c, dict) and c.get("name")]
    live_courses = [c.get("name") or c.get("title") for c in (item.get("relatedLiveCourses") or []) if isinstance(c, dict)]
    resources = [{"name": r.get("name"), "size": r.get("sizeString")} for r in (item.get("resources") or []) if isinstance(r, dict) and r.get("name")]
    toc = (item.get("contentTable") or "").strip()

    detail.update({
        "publish_date": (item.get("publishDate") or "")[:10] or None,
        "press": item.get("pressName"),
        "ebook_formats": formats,
        "categories": categories,
        "tags": tags,
        "toc_preview": toc[:600] or None,
        "related_live_courses": [c for c in live_courses if c],
        "companion_resources": resources,
        "sample_available": bool(item.get("sampleFileKey")),
        "availability": {"paper": item.get("canSalePaper"), "ebook": item.get("canSaleEbook"), "in_stock": item.get("hasStock")},
        "popularity": {"views": item.get("viewCount"), "favorites": item.get("favCount"), "comments": item.get("commentCount")},
        "note": "Public metadata only. Companion resource downloads, samples, and errata are on the official book page; do not present them as bundled with this skill.",
    })
    return detail


def graceful_error(error: BaseException, fallback_url: str | None = None) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "error": f"{type(error).__name__}: {error}",
        "fallback": "Use references/catalog_seed.json and state that public-site lookup failed.",
        "fallback_url": fallback_url,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Read public Turing Community metadata.")
    parser.add_argument("--query", help="Search public book metadata by query")
    parser.add_argument("--limit", type=int, default=5, help="Maximum results for search or latest")
    parser.add_argument("--latest", action="store_true", help="List the newest books from the public listing")
    parser.add_argument("--book", type=int, help="Fetch public detail for one book id")
    parser.add_argument("--homepage", action="store_true", help="Fetch homepage metadata")
    args = parser.parse_args()

    try:
        if args.latest:
            output = latest_books(max(1, args.limit))
        elif args.book is not None:
            output = book_detail(args.book)
        elif args.query:
            output = search_books(args.query, max(1, args.limit))
        else:
            output = homepage()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, RuntimeError, json.JSONDecodeError) as error:
        if args.latest:
            fallback_url = f"{WWW_BASE}/book"
        elif args.book is not None:
            fallback_url = f"{WWW_BASE}/book/{args.book}"
        elif args.query:
            fallback_url = f"{WWW_BASE}/search?q={urllib.parse.quote(args.query)}"
        else:
            fallback_url = WWW_BASE
        output = graceful_error(error, fallback_url=fallback_url)

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
