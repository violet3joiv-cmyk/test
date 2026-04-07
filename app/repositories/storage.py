from __future__ import annotations

"""DB Read/Write 레이어.

비즈니스 로직과 SQL을 분리해 유지보수성을 높인다.
"""

from datetime import datetime, timezone
from typing import Any

from app.core.database import get_connection


def upsert_user_setting(user_id: str, alarm_hour_utc: int, alarm_minute_utc: int, theme: str, push_enabled: bool) -> None:
    """사용자 설정을 저장하거나 갱신한다."""
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO user_settings (user_id, alarm_hour_utc, alarm_minute_utc, theme, push_enabled, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                alarm_hour_utc=excluded.alarm_hour_utc,
                alarm_minute_utc=excluded.alarm_minute_utc,
                theme=excluded.theme,
                push_enabled=excluded.push_enabled,
                updated_at=excluded.updated_at
            """,
            (user_id, alarm_hour_utc, alarm_minute_utc, theme, int(push_enabled), now),
        )


def read_user_setting(user_id: str) -> dict[str, Any] | None:
    """단일 사용자 설정 조회."""
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def save_news(items: list[dict[str, Any]]) -> None:
    """수집/가공된 뉴스 리스트 저장."""
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO news_raw (
                published_date, country_code, category, page_size,
                title, summary_en, summary_ko, url, sentiment, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    x["published_date"],
                    x["country_code"],
                    x["category"],
                    x["page_size"],
                    x["title"],
                    x["summary_en"],
                    x["summary_ko"],
                    x["url"],
                    x["sentiment"],
                    now,
                )
                for x in items
            ],
        )


def read_news_history(limit: int = 100) -> list[dict[str, Any]]:
    """뉴스 히스토리 조회."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM news_raw ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def save_trends(items: list[dict[str, Any]]) -> None:
    """인기검색어(트렌드) 저장."""
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.executemany(
            "INSERT INTO trends (trend_date, keyword, country_code, url, created_at) VALUES (?, ?, ?, ?, ?)",
            [(x["trend_date"], x["keyword"], x["country_code"], x["url"], now) for x in items],
        )


def read_trends_history(limit: int = 50) -> list[dict[str, Any]]:
    """트렌드 히스토리 조회."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM trends ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def save_report_pages(report_date: str, pages: list[dict[str, Any]]) -> None:
    """리포트 페이지(1~3면) 저장."""
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO reports (
                report_date, page_no, markdown, html, image_prompt, image_url,
                market_one_line, deep_link, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    report_date,
                    p["page_no"],
                    p["markdown"],
                    p["html"],
                    p.get("image_prompt"),
                    p.get("image_url"),
                    p["market_one_line"],
                    p["deep_link"],
                    now,
                )
                for p in pages
            ],
        )


def read_report_history(limit: int = 30) -> list[dict[str, Any]]:
    """리포트 히스토리 조회."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM reports ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]
