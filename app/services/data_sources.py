from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date


@dataclass
class NewsItem:
    title: str
    source: str
    summary: str
    url: str


@dataclass
class MarketItem:
    metric: str
    value: str
    change: str
    source: str


class GlobalDataCollector:
    """Collects global news and macro-economic snapshots from APIs."""

    def __init__(self) -> None:
        self.news_api_key = os.getenv("NEWSAPI_KEY")
        self.alpha_vantage_key = os.getenv("ALPHAVANTAGE_KEY")

    def fetch_news(self, day: date) -> list[NewsItem]:
        if not self.news_api_key:
            return self._fallback_news(day)

        endpoint = "https://newsapi.org/v2/top-headlines"
        params = {"language": "en", "pageSize": 12, "apiKey": self.news_api_key}

        try:
            import httpx

            response = httpx.get(endpoint, params=params, timeout=20)
            response.raise_for_status()
            payload = response.json()
            items = payload.get("articles", [])
            parsed: list[NewsItem] = []
            for item in items[:10]:
                parsed.append(
                    NewsItem(
                        title=item.get("title", "Untitled"),
                        source=item.get("source", {}).get("name", "Unknown"),
                        summary=(item.get("description") or "요약 정보 없음"),
                        url=item.get("url", ""),
                    )
                )
            return parsed or self._fallback_news(day)
        except Exception:
            return self._fallback_news(day)

    def fetch_market_data(self, day: date) -> list[MarketItem]:
        if not self.alpha_vantage_key:
            return self._fallback_market(day)

        symbols = ["SPY", "QQQ", "GLD", "USO"]
        result: list[MarketItem] = []
        for symbol in symbols:
            endpoint = "https://www.alphavantage.co/query"
            params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": self.alpha_vantage_key}
            try:
                import httpx

                response = httpx.get(endpoint, params=params, timeout=20)
                response.raise_for_status()
                quote = response.json().get("Global Quote", {})
                result.append(
                    MarketItem(
                        metric=symbol,
                        value=quote.get("05. price", "N/A"),
                        change=quote.get("10. change percent", "N/A"),
                        source="Alpha Vantage",
                    )
                )
            except Exception:
                result.append(
                    MarketItem(metric=symbol, value="N/A", change="N/A", source="Alpha Vantage")
                )
        return result

    @staticmethod
    def _fallback_news(day: date) -> list[NewsItem]:
        iso = day.isoformat()
        return [
            NewsItem(
                title=f"[{iso}] 글로벌 지정학 핵심 이슈",
                source="Fallback Feed",
                summary="주요 지역의 정책/외교 이벤트를 종합한 브리핑입니다.",
                url="https://example.com/geopolitics",
            ),
            NewsItem(
                title=f"[{iso}] AI/반도체 산업 동향",
                source="Fallback Feed",
                summary="미국·유럽·아시아 공급망 및 투자 흐름 요약입니다.",
                url="https://example.com/ai-semiconductor",
            ),
            NewsItem(
                title=f"[{iso}] 에너지/원자재 시장 이슈",
                source="Fallback Feed",
                summary="유가/가스/금속 가격 변동 요인과 리스크를 정리했습니다.",
                url="https://example.com/commodities",
            ),
        ]

    @staticmethod
    def _fallback_market(day: date) -> list[MarketItem]:
        _ = day
        return [
            MarketItem(metric="S&P 500", value="5,210", change="+0.38%", source="Fallback"),
            MarketItem(metric="NASDAQ 100", value="18,240", change="+0.52%", source="Fallback"),
            MarketItem(metric="US 10Y Yield", value="4.12%", change="-0.03%p", source="Fallback"),
            MarketItem(metric="Brent Oil", value="$84.1", change="+1.10%", source="Fallback"),
            MarketItem(metric="Gold", value="$2,320", change="-0.25%", source="Fallback"),
        ]
