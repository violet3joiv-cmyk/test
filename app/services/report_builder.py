from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.services.data_sources import MarketItem, NewsItem


@dataclass
class BuiltReport:
    title: str
    markdown: str
    html: str


class ReportBuilder:
    """Builds a 2-3 page style integrated global report in Markdown + HTML."""

    @staticmethod
    def build(news: list[NewsItem], markets: list[MarketItem], generated_at: datetime) -> BuiltReport:
        title = f"전세계 통합 뉴스·경제 리포트 ({generated_at:%Y-%m-%d})"

        md_sections: list[str] = [
            f"# {title}",
            "",
            f"생성 시각: {generated_at:%Y-%m-%d %H:%M:%S UTC}",
            "",
            "---",
            "",
            "## 1. 글로벌 뉴스 핵심 요약",
        ]

        for idx, item in enumerate(news, start=1):
            md_sections.extend(
                [
                    f"### 1-{idx}. {item.title}",
                    f"- 출처: {item.source}",
                    f"- 요약: {item.summary}",
                    f"- 링크: {item.url}",
                    "",
                ]
            )

        md_sections.extend(["---", "", "## 2. 글로벌 경제/시장 지표 요약", ""])
        for m in markets:
            md_sections.append(f"- **{m.metric}**: {m.value} ({m.change}) · 출처: {m.source}")

        md_sections.extend(
            [
                "",
                "---",
                "",
                "## 3. 인사이트 및 다음 체크포인트",
                "",
                "1) 정책/금리 이벤트 일정 확인",
                "2) 원자재 및 에너지 변동성 감시",
                "3) AI/반도체/클라우드 실적 가이던스 점검",
                "",
                "> 본 문서는 자동 생성 리포트이며 투자 자문이 아닙니다.",
            ]
        )

        markdown = "\n".join(md_sections)

        html_news = "".join(
            f"<li><h4>{n.title}</h4><p><b>출처:</b> {n.source}</p>"
            f"<p>{n.summary}</p><a href='{n.url}' target='_blank'>원문 보기</a></li>"
            for n in news
        )
        html_markets = "".join(
            f"<li><b>{m.metric}</b>: {m.value} ({m.change}) <i>{m.source}</i></li>" for m in markets
        )

        html = f"""
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px auto; max-width: 900px; line-height: 1.6; }}
    h1, h2 {{ border-bottom: 1px solid #ddd; padding-bottom: 6px; }}
    section {{ margin: 24px 0; }}
    .note {{ color: #555; font-size: 0.92rem; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p>생성 시각: {generated_at:%Y-%m-%d %H:%M:%S UTC}</p>

  <section>
    <h2>1. 글로벌 뉴스 핵심 요약</h2>
    <ol>{html_news}</ol>
  </section>

  <section>
    <h2>2. 글로벌 경제/시장 지표 요약</h2>
    <ul>{html_markets}</ul>
  </section>

  <section>
    <h2>3. 인사이트 및 다음 체크포인트</h2>
    <ol>
      <li>정책/금리 이벤트 일정 확인</li>
      <li>원자재 및 에너지 변동성 감시</li>
      <li>AI/반도체/클라우드 실적 가이던스 점검</li>
    </ol>
    <p class="note">본 문서는 자동 생성 리포트이며 투자 자문이 아닙니다.</p>
  </section>
</body>
</html>
""".strip()

        return BuiltReport(title=title, markdown=markdown, html=html)
