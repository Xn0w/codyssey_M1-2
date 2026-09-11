# 나만의 AI 비서

## 서비스 소개
내 시계열 데이터(주식/운동 기록/학습 시간 등)를 저장하면, AI가 그 데이터의
요약 정보(기간/평균/최근 추세)를 참고해서 맞춤형으로 대답해주는 개인 비서 웹 서비스.

## 기술 스택
- 백엔드: FastAPI, Pydantic, Firebase Admin SDK
- DB: Firebase Firestore
- AI: OpenAI GPT API
- 프론트엔드: HTML / CSS / Vanilla JavaScript
- 배포: 백엔드 Render, 프론트엔드 Vercel

## 배포 URL
- 프론트엔드: (배포 후 작성)
- 백엔드 API: (배포 후 작성)
- Swagger UI: (백엔드 주소)/docs

## 로컬 실행 방법

### 백엔드
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows는 venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # 이후 .env를 실제 값으로 채우기
uvicorn main:app --reload
```
http://127.0.0.1:8000/docs 에서 Swagger UI 확인 가능.

### 프론트엔드
`frontend/index.html`을 VSCode Live Server 등으로 열기.
`frontend/script.js`의 `API_BASE` 값이 백엔드 주소와 일치하는지 확인.

## 환경 변수 (최소 세트)
| 변수명 | 설명 |
|---|---|
| `OPENAI_API_KEY` | OpenAI API 키 |
| `FIREBASE_CREDENTIALS_PATH` | Firebase 서비스 계정 키 JSON 경로 |
| `ALLOWED_ORIGINS` | CORS 허용 프론트엔드 주소 (쉼표 구분) |

## 컬렉션 구조
- `data`: 시계열 데이터 (date, value, memo, created_at)
- `conversations`: 대화 기록 (title, created_at, messages[])

## 설계 결정: 대화 불러오기 UX
`GET /api/conversations` 목록 조회에서는 messages를 제외하고,
`GET /api/conversations/{id}` 단건 조회에서만 전체 messages를 포함하도록 구현
(과제 요구사항 6번의 옵션 A 채택).

## 주의사항
- 백엔드는 Render 무료 티어 특성상 일정 시간 요청이 없으면 슬립 모드로
  전환됩니다. 슬립 이후 첫 요청은 응답까지 최대 1분 정도 걸릴 수 있습니다.

## 제출 스크린샷
(채팅 화면 / 데이터 관리 화면 / 대화 기록 화면 캡처를 여기에 첨부)
