from __future__ import annotations

from datetime import date


def get_market_snapshot(day: date) -> list[dict[str, str]]:
    _ = day
    return [
        {"metric": "S&P 500", "value": "5,210", "change": "+0.38%"},
        {"metric": "NASDAQ 100", "value": "18,240", "change": "+0.52%"},
        {"metric": "US 10Y Yield", "value": "4.12%", "change": "-0.03%p"},
        {"metric": "Brent", "value": "$84.1", "change": "+1.10%"},
    ]
