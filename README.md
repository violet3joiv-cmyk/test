# 자동 예약형 전세계 통합 뉴스&경제 리포트 알림 프로그램

아래는 요청하신 **1~9번 형식**으로 구현된 현재 코드 범위입니다.

## 1) 데이터 호출
- 데이터베이스 저장 데이터 조회 기능
  - 뉴스 이력 조회: `GET /db/news/history`
  - 트렌드 이력 조회: `GET /db/trends/history`
  - 리포트 이력 조회: `GET /db/reports/history`
- 사용자 설정 Read 작업
  - `GET /settings/{user_id}`
- 과거 기록 조회(히스토리)
  - `news_raw`, `trends`, `reports` 테이블 기반 조회

## 2) 데이터 크롤링
- 현재는 API 호출 중심 구조로 구현
- 추후 확장 가능 지점
  - `app/api_clients/providers.py`에 크롤러 함수 추가 가능

## 3) 데이터 처리
- 인기검색어 하이퍼링크(URL) 추가
  - `add_hyperlinks_to_trends()`
- 수집 뉴스 라벨 매핑(국가코드/카테고리/페이지크기)
  - `map_news_labels()`
- Gemini API 입력 포맷 변환
  - `to_gemini_payload()`
- 시장 동향 1줄 요약 가공
  - `build_market_one_line()`

## 4) API 호출 작동 (api별)
- Pytrends API 호출 함수
  - `fetch_pytrends()`
- NewsAPI 호출 함수
  - `fetch_newsapi()`
- Gemini API(번역/요약) 호출 함수
  - `call_gemini_translate()`, `call_gemini_summary()`
- Imagen3 API(이미지 생성) 호출 함수
  - `call_imagen3()`
- 공통 API 함수 관리
  - `APIProviderManager`

## 5) 통계학 (분석 및 알고리즘)
- MMR(Maximal Marginal Relevance) 중복 제거
  - `run_mmr_selection()`
- MMR 람다(lambda)값 조정
  - `MMR_LAMBDA` 환경변수 사용
- 감성 분석 (영문 텍스트)
  - `sentiment_score_en()`
- GDP 비율 가산 알고리즘
  - `gdp_weighted_country_score()`
- 알람용 키워드 선정
  - `select_alarm_keywords()`
- 1면 콘텐츠 구성
  - `select_page1_content()`

## 6) 기타 (UI/UX 및 설정)
- 프론트엔드 출력 기능
  - `GET /frontend/report?date=YYYY-MM-DD&page=1..3`
- 저장된 문장/이미지 URL 화면 표시
  - 리포트 HTML + image URL 포함
- 라이트/다크모드
  - `theme=light|dark` 쿼리 파라미터
- 앱 아이콘/디자인 요소
  - 현재 기본 HTML/CSS 수준 (추후 강화 가능)

## 7) 시간 알람 (스케줄링 및 알림)
- 하루 1회 자동 실행
  - APScheduler 크론 잡
- 사용자 알람 시간 지정/저장
  - `POST /settings/{user_id}` (시간, 테마, 푸시 on/off)
- 푸시 알림
  - Linux `notify-send` 또는 콘솔 fallback
- 딥링크
  - 저장 시 `app://report/{date}/{page}` 형식 저장

## 8) 데이터 저장
- 1면 포함 최종 텍스트/이미지 저장
  - `reports` 테이블: markdown/html/image_prompt/image_url
- 사용자 설정 저장
  - `user_settings` 테이블

## 9) 데이터 베이스 구축
- SQLite 스키마 자동 생성
  - `app/core/database.py:init_db()`
- 원문 뉴스 저장
  - `news_raw` 테이블
- 트렌드/리포트/설정 저장
  - `trends`, `reports`, `user_settings`

## 실행
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
