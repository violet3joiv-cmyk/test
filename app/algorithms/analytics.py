from __future__ import annotations

from collections import Counter


def _tokenize(text: str) -> set[str]:
    return {x.strip(',.!?"\'').lower() for x in text.split() if x.strip()}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / max(len(a | b), 1)


def run_mmr_selection(texts: list[str], lambda_value: float = 0.7, k: int = 20) -> list[int]:
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
    positive = {"growth", "up", "rise", "gain", "improve", "optimistic"}
    negative = {"down", "fall", "risk", "decline", "conflict", "inflation"}
    tokens = _tokenize(text)
    return float(sum(1 for t in tokens if t in positive) - sum(1 for t in tokens if t in negative))


def gdp_weighted_country_score(country_counts: dict[str, int], gdp_ratio: dict[str, float]) -> dict[str, float]:
    return {country: count * gdp_ratio.get(country, 1.0) for country, count in country_counts.items()}


def select_alarm_keywords(texts: list[str], top_n: int = 5) -> list[str]:
    bag = Counter()
    for text in texts:
        bag.update([t for t in _tokenize(text) if len(t) >= 4])
    return [w for w, _ in bag.most_common(top_n)]


def select_page1_content(texts: list[str], lambda_value: float = 0.7) -> list[str]:
    idx = run_mmr_selection(texts, lambda_value=lambda_value, k=min(10, len(texts)))
    return [texts[i] for i in idx]
