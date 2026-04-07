from app.algorithms.analytics import run_mmr_selection, select_alarm_keywords, sentiment_score_en
from app.services.processing import add_hyperlinks_to_trends, build_market_one_line


def test_processing_hyperlinks_and_market_line() -> None:
    trends = add_hyperlinks_to_trends([{"keyword": "ai chip", "country_code": "US"}])
    assert trends[0]["url"].startswith("https://")

    line = build_market_one_line(
        [
            {"metric": "S&P 500", "value": "5200", "change": "+0.3%"},
            {"metric": "NASDAQ", "value": "18200", "change": "+0.4%"},
        ]
    )
    assert "S&P 500" in line


def test_algorithms_work() -> None:
    texts = ["growth up", "growth up up", "conflict risk down"]
    selected = run_mmr_selection(texts, lambda_value=0.7, k=2)
    assert len(selected) == 2
    assert sentiment_score_en("growth up") > sentiment_score_en("conflict down")
    assert len(select_alarm_keywords(texts, top_n=2)) == 2
