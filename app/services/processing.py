from __future__ import annotations

"""데이터 처리 유틸리티 모음."""

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
    """인기검색어에 URL을 보강한다."""
    return [
        {
            **t,
            "url": t.get("url")
            or f"https://www.google.com/search?q={t['keyword'].replace(' ', '+')}",
        }
        for t in trends
    ]


def map_news_labels(news: list[dict[str, str]], country_code: str, category: str, page_size: int) -> list[LabeledNews]:
    """뉴스 아이템에 국가/카테고리/페이지크기 라벨을 매핑한다."""
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
    """Gemini 입력 포맷으로 데이터 구조를 변환한다."""
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
    """시장 지표를 1줄 요약 문자열로 가공한다."""
    pieces = [f"{m['metric']} {m['value']}({m['change']})" for m in markets[:4]]
    return " | ".join(pieces)
