from __future__ import annotations

"""분석/알고리즘 모듈.

MMR, 감성분석, 키워드 추출, 가중치 계산 등을 담당한다.
"""

from collections import Counter


def _tokenize(text: str) -> set[str]:
    """간단 토크나이저."""
    return {x.strip(',.!?"\'').lower() for x in text.split() if x.strip()}


def _jaccard(a: set[str], b: set[str]) -> float:
    """두 토큰 집합의 자카드 유사도."""
    if not a or not b:
        return 0.0
    return len(a & b) / max(len(a | b), 1)


def run_mmr_selection(texts: list[str], lambda_value: float = 0.7, k: int = 20) -> list[int]:
    """MMR 기반으로 중복을 낮춘 인덱스 목록을 반환한다."""
    if not texts:
        return []

    scores = [len(t) for t in texts]
    tokens = [_tokenize(t) for t in texts]
    selected: list[int] = []
    candidates = set(range(len(texts)))

    while candidates and len(selected) < min(k, len(texts)):
        best_idx = None
        best_score = float("-inf")
        for i in candidates:
            relevance = scores[i]
            diversity_penalty = 0.0
            if selected:
                diversity_penalty = max(_jaccard(tokens[i], tokens[s]) for s in selected)
            mmr = lambda_value * relevance - (1 - lambda_value) * diversity_penalty
            if mmr > best_score:
                best_score = mmr
                best_idx = i

        if best_idx is None:
            break
        selected.append(best_idx)
        candidates.remove(best_idx)

    return selected


def sentiment_score_en(text: str) -> float:
    """영문 텍스트 단순 감성 점수."""
    positive = {"growth", "up", "rise", "gain", "improve", "optimistic"}
    negative = {"down", "fall", "risk", "decline", "conflict", "inflation"}
    tokens = _tokenize(text)
    return float(sum(1 for t in tokens if t in positive) - sum(1 for t in tokens if t in negative))


def gdp_weighted_country_score(country_counts: dict[str, int], gdp_ratio: dict[str, float]) -> dict[str, float]:
    """국가별 빈도에 GDP 가중치를 반영한다."""
    return {country: count * gdp_ratio.get(country, 1.0) for country, count in country_counts.items()}


def select_alarm_keywords(texts: list[str], top_n: int = 5) -> list[str]:
    """알람용 핵심 키워드를 빈도 기반으로 추출한다."""
    bag = Counter()
    for text in texts:
        bag.update([t for t in _tokenize(text) if len(t) >= 4])
    return [w for w, _ in bag.most_common(top_n)]


def select_page1_content(texts: list[str], lambda_value: float = 0.7) -> list[str]:
    """1면에 노출할 후보 문장을 MMR로 선택한다."""
    idx = run_mmr_selection(texts, lambda_value=lambda_value, k=min(10, len(texts)))
    return [texts[i] for i in idx]
