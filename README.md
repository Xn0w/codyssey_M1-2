# 나만의 AI 비서

## 서비스 소개
내 시계열 데이터(걸음 수/주식/운동 기록/학습 시간 등)를 저장하면, AI가 그 데이터의
요약 정보(기간/평균/최근 추세)를 참고하고 필요하면 상세 데이터까지 직접 조회해서
맞춤형으로 대답해주는 개인 비서 웹 서비스.

## 기술 스택
- 백엔드: FastAPI, Pydantic, Firebase Admin SDK
- DB: Firebase Firestore
- AI: OpenAI 호환 게이트웨이(Codyssey), Function Calling
- 외부 연동: MCP(Model Context Protocol) Server
- 프론트엔드: HTML / CSS / Vanilla JavaScript (다크 모드 지원)
- 배포: 백엔드 Render, 프론트엔드 Vercel

## 배포 URL
- 프론트엔드: https://codyssey-m1-2-alpha.vercel.app
- 백엔드 API: https://codyssey-m1-2-92sp.onrender.com
- Swagger UI: https://codyssey-m1-2-92sp.onrender.com/docs

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
| `OPENAI_API_KEY` | AI 게이트웨이 API 키 |
| `OPENAI_BASE_URL` | OpenAI 호환 게이트웨이 주소 (예: Codyssey 게이트웨이). 공식 OpenAI 사용 시 비워둠 |
| `FIREBASE_CREDENTIALS_PATH` | (로컬용) Firebase 서비스 계정 키 JSON 경로 |
| `FIREBASE_CREDENTIALS_JSON` | (배포용) Firebase 서비스 계정 키 JSON 내용 전체를 문자열로 |
| `ALLOWED_ORIGINS` | CORS 허용 프론트엔드 주소 (쉼표 구분) |

## 컬렉션 구조
- `data`: 시계열 데이터 (date, value, memo, created_at)
- `conversations`: 대화 기록 (title, created_at, messages[])

## 설계 결정: 대화 불러오기 UX
`GET /api/conversations` 목록 조회에서는 messages를 제외하고,
`GET /api/conversations/{id}` 단건 조회에서만 전체 messages를 포함하도록 구현
(과제 요구사항 6번의 옵션 A 채택).

## 보너스 과제 1: AI 도구 호출(Function Calling) + 멀티채널 연동

### 어떤 근거로 어떤 도구를 호출하는가
`/api/chat`이 매 요청마다 데이터 요약을 시스템 프롬프트에 미리 넣어주지만,
"7월 15일부터 20일까지 값 알려줘" 처럼 **요약만으로 답할 수 없는 상세 질문**에는
AI가 스스로 판단해서 `get_data_in_range(start_date, end_date)` 도구를 호출하도록
설계했다. 시스템 프롬프트에 "요약에 없는 세부 수치는 지어내지 말고 도구를 호출해서
확인하라"는 지침을 명시해, AI가 임의로 숫자를 지어내지 않고 실제 Firestore 데이터를
근거로만 답하게 했다.

### 호출 흐름