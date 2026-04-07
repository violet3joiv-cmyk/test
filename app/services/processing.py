from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LabeledNews:
    title: str
    summary_en: str
    summary_ko: str
    url: str
    country_code: str
    category: str
    page_size: int


def add_hyperlinks_to_trends(trends: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            **t,
            "url": t.get("url")
            or f"https://www.google.com/search?q={t['keyword'].replace(' ', '+')}",
        }
        for t in trends
    ]


def map_news_labels(news: list[dict[str, str]], country_code: str, category: str, page_size: int) -> list[LabeledNews]:
    return [
        LabeledNews(
            title=n["title"],
            summary_en=n["summary_en"],
            summary_ko=n.get("summary_ko", n["summary_en"]),
            url=n["url"],
            country_code=country_code,
            category=category,
            page_size=page_size,
        )
        for n in news
    ]


def to_gemini_payload(labeled_news: list[LabeledNews], trends: list[dict[str, str]]) -> dict:
    return {
        "input_news": [
            {
                "title": n.title,
                "summary_en": n.summary_en,
                "summary_ko": n.summary_ko,
                "country_code": n.country_code,
                "category": n.category,
                "page_size": n.page_size,
                "url": n.url,
            }
            for n in labeled_news
        ],
        "trends": trends,
    }


def build_market_one_line(markets: list[dict[str, str]]) -> str:
    pieces = [f"{m['metric']} {m['value']}({m['change']})" for m in markets[:4]]
    return " | ".join(pieces)
