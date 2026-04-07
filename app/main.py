from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

from app.services.data_sources import GlobalDataCollector
from app.services.notifier import send_notification
from app.services.report_builder import BuiltReport, ReportBuilder

app = FastAPI(title="Global News & Economy Reporter")

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

collector = GlobalDataCollector()
latest_report_path = REPORT_DIR / "latest.html"
latest_md_path = REPORT_DIR / "latest.md"


def generate_daily_report() -> BuiltReport:
    now = datetime.now(timezone.utc)
    news = collector.fetch_news(now.date())
    markets = collector.fetch_market_data(now.date())
    built = ReportBuilder.build(news, markets, now)

    dated_slug = now.strftime("%Y%m%d")
    (REPORT_DIR / f"report_{dated_slug}.html").write_text(built.html, encoding="utf-8")
    (REPORT_DIR / f"report_{dated_slug}.md").write_text(built.markdown, encoding="utf-8")

    latest_report_path.write_text(built.html, encoding="utf-8")
    latest_md_path.write_text(built.markdown, encoding="utf-8")
    return built


def scheduled_job() -> None:
    built = generate_daily_report()
    report_url = os.getenv("REPORT_URL", "http://127.0.0.1:8000/report/latest")
    send_notification(
        title="통합 뉴스·경제 리포트 생성 완료",
        message=f"{built.title}\n알림 클릭 후 리포트를 확인하세요.",
        url=report_url,
    )


@app.on_event("startup")
def on_startup() -> None:
    hour = int(os.getenv("SCHEDULE_HOUR_UTC", "7"))
    minute = int(os.getenv("SCHEDULE_MINUTE_UTC", "0"))

    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(scheduled_job, "cron", hour=hour, minute=minute, id="daily_report")
    scheduler.start()


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.post("/report/generate")
def generate_now() -> JSONResponse:
    built = generate_daily_report()
    return JSONResponse({"title": built.title, "path": str(latest_report_path)})


@app.get("/report/latest", response_class=HTMLResponse)
def read_latest_html() -> HTMLResponse:
    if not latest_report_path.exists():
        raise HTTPException(status_code=404, detail="리포트가 아직 생성되지 않았습니다.")
    return HTMLResponse(latest_report_path.read_text(encoding="utf-8"))


@app.get("/report/latest.md", response_class=PlainTextResponse)
def read_latest_markdown() -> PlainTextResponse:
    if not latest_md_path.exists():
        raise HTTPException(status_code=404, detail="리포트가 아직 생성되지 않았습니다.")
    return PlainTextResponse(latest_md_path.read_text(encoding="utf-8"))
