from datetime import datetime, timezone

from app.services.data_sources import MarketItem, NewsItem
from app.services.report_builder import ReportBuilder


def test_report_builder_contains_key_sections() -> None:
    news = [
        NewsItem(title="Test News", source="UnitTest", summary="Summary", url="https://example.com"),
    ]
    markets = [
        MarketItem(metric="S&P 500", value="5000", change="+0.1%", source="UnitTest"),
    ]

    report = ReportBuilder.build(news, markets, datetime(2026, 1, 1, tzinfo=timezone.utc))

    assert "글로벌 뉴스 핵심 요약" in report.markdown
    assert "글로벌 경제/시장 지표 요약" in report.markdown
    assert "Test News" in report.html
    assert "S&P 500" in report.html
