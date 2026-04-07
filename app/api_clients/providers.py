from __future__ import annotations

"""외부 API 호출 계층.

실서비스에서는 각 함수에 실제 SDK/REST 호출을 연결하면 되고,
현재는 오프라인 환경에서도 동작하도록 fallback 데이터를 제공한다.
"""

import os
from datetime import date


class APIProviderManager:
    """API별 호출 함수를 통합 관리한다."""

    def fetch_pytrends(self, country_code: str) -> list[dict[str, str]]:
        """Pytrends(구글 인기검색어) 수집."""
        # 실서비스에서는 pytrends 라이브러리/Google Trends API 연동
        base = ["inflation", "ai chip", "oil price", "fed rate"]
        return [
            {
                "keyword": kw,
                "country_code": country_code,
                "url": f"https://trends.google.com/trends/explore?q={kw.replace(' ', '+')}",
            }
            for kw in base
        ]

    def fetch_newsapi(self, country_code: str, page_size: int = 30) -> list[dict[str, str]]:
        """NewsAPI를 사용해 국가별 헤드라인을 수집."""
        key = os.getenv("NEWSAPI_KEY")
        if not key:
            return self._fallback_news(country_code, page_size)

        try:
            import httpx

            response = httpx.get(
                "https://newsapi.org/v2/top-headlines",
                params={"country": country_code.lower(), "pageSize": page_size, "apiKey": key},
                timeout=20,
            )
            response.raise_for_status()
            articles = response.json().get("articles", [])
            return [
                {
                    "title": x.get("title", "Untitled"),
                    "summary_en": x.get("description") or "No summary",
                    "url": x.get("url", "https://example.com"),
                }
                for x in articles
            ]
        except Exception:
            return self._fallback_news(country_code, page_size)

    def call_gemini_translate(self, text: str, target_lang: str = "ko") -> str:
        """Gemini 번역 API 연결 지점."""
        # Gemini API 연결 지점(현재는 오프라인 친화적 fallback)
        return f"[{target_lang} 번역] {text}"

    def call_gemini_summary(self, text: str) -> str:
        """Gemini 요약 API 연결 지점."""
        return f"요약: {text[:120]}"

    def call_imagen3(self, prompt: str) -> str:
        """Imagen3 이미지 생성 API 연결 지점."""
        # Imagen3 API 연결 지점(placeholder URL)
        return f"https://image.example.com/render?prompt={prompt[:40].replace(' ', '+')}"

    @staticmethod
    def _fallback_news(country_code: str, page_size: int) -> list[dict[str, str]]:
        """API 호출 실패 시 사용할 샘플 뉴스."""
        today = date.today().isoformat()
        seed = [
            "Central bank policy guidance",
            "AI semiconductor investment outlook",
            "Energy supply chain volatility",
            "Global trade and logistics trend",
        ]
        return [
            {
                "title": f"[{today}] {country_code.upper()} {seed[i % len(seed)]}",
                "summary_en": "Fallback global headline for offline mode",
                "url": f"https://example.com/{country_code}/{i}",
            }
            for i in range(min(page_size, 12))
        ]
