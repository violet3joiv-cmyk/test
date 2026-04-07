from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class BuiltPage:
    page_no: int
    markdown: str
    html: str


class ReportComposer:
    def build_pages(
        self,
        generated_at: datetime,
        trends: list[dict[str, str]],
        top_news: list[dict[str, str]],
        market_line: str,
        image_url: str,
        theme: str,
    ) -> list[BuiltPage]:
        title = f"전세계 통합 뉴스·경제 리포트 ({generated_at:%Y-%m-%d})"

        page1_md = "\n".join(
            [
                f"# {title} - 1면",
                f"생성 시각: {generated_at:%Y-%m-%d %H:%M:%S UTC}",
                "## 인기검색어",
                *[f"- [{t['keyword']}]({t['url']})" for t in trends[:10]],
                "## 오늘의 핵심 뉴스",
                *[f"- {n['title']} ({n['country_code']}/{n['category']})" for n in top_news[:10]],
                f"\n시장 동향 한줄: {market_line}",
            ]
        )

        body_class = "dark" if theme == "dark" else "light"
        trend_items = "".join([f"<li><a href='{t['url']}'>{t['keyword']}</a></li>" for t in trends[:10]])
        news_items = "".join([f"<li>{n['title']} ({n['country_code']}/{n['category']})</li>" for n in top_news[:10]])
        page1_html = (
            f"<html><body class='{body_class}'><h1>{title} - 1면</h1>"
            f"<h2>인기검색어</h2><ul>{trend_items}</ul>"
            f"<h2>오늘의 핵심 뉴스</h2><ul>{news_items}</ul>"
            f"<p><b>시장 동향 한줄:</b> {market_line}</p>"
            f"<img src='{image_url}' alt='report image' width='540'/></body></html>"
        )

        page2_md = "\n".join(
            [
                f"# {title} - 2면",
                "## 상세 요약",
                *[f"- {n['title']}: {n['summary_ko']}\n  - 원문: {n['url']}" for n in top_news[:20]],
            ]
        )
        detail_items = "".join(
            [
                f"<li><b>{n['title']}</b><p>{n['summary_ko']}</p><a href='{n['url']}'>링크</a></li>"
                for n in top_news[:20]
            ]
        )
        page2_html = f"<html><body class='{body_class}'><h1>{title} - 2면</h1><ol>{detail_items}</ol></body></html>"

        page3_md = "\n".join(
            [
                f"# {title} - 3면",
                "## 운영 메모",
                "- 중복 제거: MMR 적용",
                "- 알람 키워드 후보: 고빈도 단어 기반",
                "- 사용자 설정(알람 시간/테마) 반영",
            ]
        )
        page3_html = (
            f"<html><body class='{body_class}'><h1>{title} - 3면</h1>"
            "<p>알고리즘/설정/히스토리 정보</p></body></html>"
        )

        return [
            BuiltPage(page_no=1, markdown=page1_md, html=page1_html),
            BuiltPage(page_no=2, markdown=page2_md, html=page2_html),
            BuiltPage(page_no=3, markdown=page3_md, html=page3_html),
        ]
