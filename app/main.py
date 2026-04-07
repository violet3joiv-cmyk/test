from __future__ import annotations

import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from app.algorithms.analytics import (
    gdp_weighted_country_score,
    select_alarm_keywords,
    select_page1_content,
    sentiment_score_en,
)
from app.api_clients.providers import APIProviderManager
from app.core.database import init_db
from app.repositories.storage import (
    read_news_history,
    read_report_history,
    read_trends_history,
    read_user_setting,
    save_news,
    save_report_pages,
    save_trends,
    upsert_user_setting,
)
from app.services.data_sources import get_market_snapshot
from app.services.notifier import send_notification
from app.services.processing import add_hyperlinks_to_trends, build_market_one_line, map_news_labels, to_gemini_payload
from app.services.report_builder import ReportComposer

app = FastAPI(title="Global Integrated Report")
provider = APIProviderManager()
composer = ReportComposer()
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


def run_pipeline(user_id: str = "default") -> dict:
    now = datetime.now(timezone.utc)
    setting = read_user_setting(user_id) or {
        "alarm_hour_utc": int(os.getenv("SCHEDULE_HOUR_UTC", "7")),
        "alarm_minute_utc": int(os.getenv("SCHEDULE_MINUTE_UTC", "0")),
        "theme": "light",
        "push_enabled": 1,
    }

    countries = ["us", "gb", "jp"]
    all_news: list[dict] = []
    all_texts: list[str] = []

    for country in countries:
        news = provider.fetch_newsapi(country, page_size=30)
        translated = []
        for n in news:
            ko = provider.call_gemini_translate(n["summary_en"], "ko")
            translated.append({**n, "summary_ko": ko})
        labeled = map_news_labels(translated, country.upper(), "general", 30)
        for item in labeled:
            sentiment = sentiment_score_en(item.summary_en)
            all_news.append(
                {
                    "published_date": now.date().isoformat(),
                    "country_code": item.country_code,
                    "category": item.category,
                    "page_size": item.page_size,
                    "title": item.title,
                    "summary_en": item.summary_en,
                    "summary_ko": item.summary_ko,
                    "url": item.url,
                    "sentiment": sentiment,
                }
            )
            all_texts.append(f"{item.title} {item.summary_en}")

    trends = []
    for country in countries:
        trends.extend(provider.fetch_pytrends(country.upper()))
    trends = add_hyperlinks_to_trends(
        [{"trend_date": now.date().isoformat(), **x} for x in trends]
    )

    save_news(all_news)
    save_trends(trends)

    dedup_top = select_page1_content(all_texts[:450], lambda_value=float(os.getenv("MMR_LAMBDA", "0.7")))
    alarm_keywords = select_alarm_keywords(dedup_top, top_n=5)
    country_weight = gdp_weighted_country_score(Counter([x["country_code"] for x in all_news]), {"US": 1.0, "GB": 0.6, "JP": 0.7})

    top_news = all_news[:20]
    gemini_payload = to_gemini_payload(
        map_news_labels(top_news, "US", "general", 30), trends[:20]
    )

    market_line = build_market_one_line(get_market_snapshot(now.date()))
    image_prompt = provider.call_gemini_summary("; ".join(dedup_top[:5]))
    image_url = provider.call_imagen3(image_prompt)

    pages = composer.build_pages(now, trends, top_news, market_line, image_url, setting["theme"])
    report_date = now.date().isoformat()
    save_report_pages(
        report_date,
        [
            {
                "page_no": p.page_no,
                "markdown": p.markdown,
                "html": p.html,
                "image_prompt": image_prompt,
                "image_url": image_url,
                "market_one_line": market_line,
                "deep_link": f"app://report/{report_date}/{p.page_no}",
            }
            for p in pages
        ],
    )

    (REPORT_DIR / "latest.html").write_text(pages[0].html, encoding="utf-8")

    if setting["push_enabled"]:
        send_notification(
            "통합 리포트 생성 완료",
            f"키워드: {', '.join(alarm_keywords)}",
            f"http://127.0.0.1:8000/frontend/report?date={report_date}&page=1",
        )

    return {
        "generated_at": now.isoformat(),
        "alarm_keywords": alarm_keywords,
        "country_weight": country_weight,
        "gemini_payload_size": len(gemini_payload["input_news"]),
        "image_url": image_url,
    }


@app.on_event("startup")
def startup() -> None:
    init_db()

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(lambda: run_pipeline("default"), "cron", hour=7, minute=0, id="daily_pipeline")
    scheduler.start()


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.post("/pipeline/run")
def pipeline_run() -> JSONResponse:
    return JSONResponse(run_pipeline("default"))


@app.get("/db/news/history")
def db_news_history(limit: int = 100) -> JSONResponse:
    return JSONResponse({"items": read_news_history(limit)})


@app.get("/db/trends/history")
def db_trends_history(limit: int = 50) -> JSONResponse:
    return JSONResponse({"items": read_trends_history(limit)})


@app.get("/db/reports/history")
def db_reports_history(limit: int = 30) -> JSONResponse:
    return JSONResponse({"items": read_report_history(limit)})


@app.get("/settings/{user_id}")
def get_user_setting(user_id: str) -> JSONResponse:
    return JSONResponse({"setting": read_user_setting(user_id)})


@app.post("/settings/{user_id}")
def set_user_setting(user_id: str, alarm_hour_utc: int, alarm_minute_utc: int, theme: str = "light", push_enabled: bool = True) -> JSONResponse:
    upsert_user_setting(user_id, alarm_hour_utc, alarm_minute_utc, theme, push_enabled)
    return JSONResponse({"saved": True, "user_id": user_id})


@app.get("/frontend/report", response_class=HTMLResponse)
def frontend_report(date: str, page: int = 1, theme: str = "light") -> HTMLResponse:
    report_rows = [x for x in read_report_history(100) if x["report_date"] == date and x["page_no"] == page]
    if not report_rows:
        return HTMLResponse("<h1>리포트가 없습니다.</h1>", status_code=404)

    data = report_rows[0]
    toggle_theme = "dark" if theme == "light" else "light"
    wrapper = (
        "<html><head><style>"
        "body.light{background:#fff;color:#111;} body.dark{background:#121212;color:#eee;}"
        "a{margin-right:12px;} .nav{margin-bottom:10px;}"
        "</style></head>"
        f"<body class='{theme}'>"
        f"<div class='nav'><a href='/frontend/report?date={date}&page=1&theme={theme}'>1면</a>"
        f"<a href='/frontend/report?date={date}&page=2&theme={theme}'>2면</a>"
        f"<a href='/frontend/report?date={date}&page=3&theme={theme}'>3면</a>"
        f"<a href='/frontend/report?date={date}&page={page}&theme={toggle_theme}'>테마전환</a></div>"
        f"{data['html']}"
        "</body></html>"
    )
    return HTMLResponse(wrapper)
