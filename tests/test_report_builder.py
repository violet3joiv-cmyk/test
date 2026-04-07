from datetime import datetime, timezone

from app.services.report_builder import ReportComposer


def test_report_composer_builds_three_pages() -> None:
    composer = ReportComposer()
    pages = composer.build_pages(
        generated_at=datetime(2026, 4, 7, tzinfo=timezone.utc),
        trends=[{"keyword": "inflation", "url": "https://example.com"}],
        top_news=[
            {
                "title": "Fed keeps rates",
                "summary_ko": "연준이 금리를 동결",
                "url": "https://example.com/news",
                "country_code": "US",
                "category": "general",
            }
        ],
        market_line="S&P 500 5200(+0.3%)",
        image_url="https://image.example.com/a",
        theme="light",
    )

    assert len(pages) == 3
    assert "1면" in pages[0].markdown
    assert "2면" in pages[1].markdown
    assert "3면" in pages[2].markdown
