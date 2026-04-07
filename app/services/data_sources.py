from __future__ import annotations

"""시장 지표 등 보조 데이터 소스 모듈."""

from datetime import date


def get_market_snapshot(day: date) -> list[dict[str, str]]:
    """시장 지표 스냅샷을 반환한다(현재 샘플 데이터)."""
    _ = day
    return [
        {"metric": "S&P 500", "value": "5,210", "change": "+0.38%"},
        {"metric": "NASDAQ 100", "value": "18,240", "change": "+0.52%"},
        {"metric": "US 10Y Yield", "value": "4.12%", "change": "-0.03%p"},
        {"metric": "Brent", "value": "$84.1", "change": "+1.10%"},
    ]
