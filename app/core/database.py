from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path("reports/app.db")
DB_PATH.parent.mkdir(exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id TEXT PRIMARY KEY,
                alarm_hour_utc INTEGER NOT NULL,
                alarm_minute_utc INTEGER NOT NULL,
                theme TEXT NOT NULL DEFAULT 'light',
                push_enabled INTEGER NOT NULL DEFAULT 1,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS news_raw (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                published_date TEXT NOT NULL,
                country_code TEXT NOT NULL,
                category TEXT NOT NULL,
                page_size INTEGER NOT NULL,
                title TEXT NOT NULL,
                summary_en TEXT NOT NULL,
                summary_ko TEXT NOT NULL,
                url TEXT NOT NULL,
                sentiment REAL NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trend_date TEXT NOT NULL,
                keyword TEXT NOT NULL,
                country_code TEXT NOT NULL,
                url TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT NOT NULL,
                page_no INTEGER NOT NULL,
                markdown TEXT NOT NULL,
                html TEXT NOT NULL,
                image_prompt TEXT,
                image_url TEXT,
                market_one_line TEXT NOT NULL,
                deep_link TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
