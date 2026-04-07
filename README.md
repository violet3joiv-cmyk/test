# 자동 예약형 전세계 통합 뉴스 & 경제 리포트 알림 프로그램

매일 정해진 시각(UTC)에 글로벌 뉴스/경제 데이터를 API로 수집하고,
2~3면 분량의 통합 리포트를 자동 생성한 뒤 알림을 보내는 백엔드 예시입니다.

## 주요 기능
- 글로벌 뉴스 API + 시장 데이터 API 수집 (키 없을 때 fallback 데이터 사용)
- Markdown/HTML 동시 리포트 생성 (`reports/` 저장)
- APScheduler 기반 일일 자동 생성
- 알림 발송 (Linux `notify-send` 우선, 불가 시 콘솔 출력)
- FastAPI로 최신 리포트 조회

## 프로젝트 구조
```
app/
  main.py
  services/
    data_sources.py
    report_builder.py
    notifier.py
reports/
tests/
```

## 실행 방법
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 환경 변수
- `NEWSAPI_KEY`: newsapi.org 키 (선택)
- `ALPHAVANTAGE_KEY`: Alpha Vantage 키 (선택)
- `SCHEDULE_HOUR_UTC`: 자동 생성 시각(시, 기본 7)
- `SCHEDULE_MINUTE_UTC`: 자동 생성 시각(분, 기본 0)
- `REPORT_URL`: 알림에 표시할 리포트 URL (기본 `http://127.0.0.1:8000/report/latest`)

## API 엔드포인트
- `GET /health`
- `POST /report/generate`: 즉시 리포트 생성
- `GET /report/latest`: 최신 HTML 리포트 조회
- `GET /report/latest.md`: 최신 Markdown 리포트 조회

## 기대 동작
1. 서버가 시작되면 스케줄러가 등록됩니다.
2. 매일 지정 시각에 리포트 생성 + 알림을 전송합니다.
3. 사용자는 알림의 URL(또는 직접 URL 접속)을 통해 2~3면 통합 리포트를 확인합니다.

> 참고: 운영 환경에서 알림 클릭 이벤트를 완전히 제어하려면
> OS 알림센터 연동 또는 모바일 푸시(FCM/APNs) 방식으로 확장하는 것이 좋습니다.
