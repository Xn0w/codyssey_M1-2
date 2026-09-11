# 다시 시작하기 가이드 (재설정 체크리스트)

`venv/`, `.env`, `firebase-key.json`은 전부 `.gitignore`에 들어있어서
**GitHub에는 올라가 있지 않습니다.** 새 컴퓨터에서 클론하거나, 시간이 지나서
다시 작업을 재개할 때는 이 파일들을 처음부터 다시 만들어야 합니다.
아래 순서대로 따라가면 됩니다.

---

## 0. 이미 다 되어 있어서 안 해도 되는 것

- **Render / Vercel 배포 자체는 그대로 살아있습니다.** 서비스를 지우지 않은 이상
  배포 URL도, 거기 등록해둔 환경변수도 그대로 남아있어요. 코드를 고쳐서
  `git push`만 하면 자동으로 재배포됩니다.
- **Firestore 데이터도 그대로 남아있습니다.** (Firebase는 로컬 컴퓨터가 아니라
  구글 서버에 있는 클라우드 DB라서요.)

즉 아래 작업은 **"이 컴퓨터에서 로컬로 다시 개발/테스트하기 위한" 준비**일 뿐,
이미 배포된 서비스는 아무 조치 없이 그대로 잘 돌아가고 있습니다.

---

## 1. 저장소 클론 (새 컴퓨터인 경우)
```bash
git clone https://github.com/Xn0w/codyssey_M1-2.git
cd codyssey_M1-2
```

## 2. 백엔드 가상환경(venv) 다시 만들기
```bash
cd backend
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```
(Homebrew 파이썬 환경에서 `pip install`이 `externally-managed-environment` 에러를
내면, `venv/bin/pip install ...` 처럼 venv 안의 pip을 직접 지정해서 실행하면 됩니다.)

## 3. `.env` 파일 다시 만들기
```bash
cp .env.example .env
```
그다음 아래 4개 값을 채워야 합니다. **어디서 다시 찾는지**는 4번 섹션 참고.
OPENAI_API_KEY=
OPENAI_BASE_URL=https://copa.codyssey.kr/v1
FIREBASE_CREDENTIALS_PATH=firebase-key.json
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500,https://codyssey-m1-2-alpha.vercel.app

## 4. 값/토큰을 다시 찾는 방법

### OPENAI_API_KEY, OPENAI_BASE_URL
1. https://usr.codyssey.kr/public-api-console 접속 (Codyssey 로그인 필요)
2. **API 키** 탭 → 기존 키가 남아있으면 그대로 쓰거나, **+ 키 발급**으로 새로 발급
   (발급 시 **API 호환 방식: OpenAI** 선택, Permissions: All)
3. **문서** 탭 → "코드 예제" 섹션에서 **Cursor/OpenAI Base URL** 값 확인
   (지금 기준 `https://copa.codyssey.kr/v1`, 바뀌었을 수도 있으니 매번 확인)

### FIREBASE_CREDENTIALS_PATH용 firebase-key.json 파일
원본 파일을 잃어버렸다면 새로 발급받아야 합니다 (기존 키를 다시 다운로드하는
기능은 없고, 새로 만드는 것만 가능합니다).
1. https://console.firebase.google.com 접속 → 기존 프로젝트(`M1-2` 등) 선택
2. 왼쪽 위 ⚙️ **프로젝트 설정** → **서비스 계정** 탭
3. **새 비공개 키 생성** → 다운로드된 JSON 파일을 `backend/firebase-key.json`으로
   이름 바꿔서 저장
   (기존 키가 폐기되는 게 아니라 키가 하나 더 늘어나는 것뿐이라 안전합니다)

### 배포된 백엔드에 등록된 환경변수 (참고 확인용, 보통 재입력 불필요)
Render 대시보드 → 서비스 선택 → **Environment** 탭에서 언제든 현재 값 확인 가능.
(단, 값 자체가 가려져 있는 항목은 **Reveal**을 눌러야 보입니다.)

## 5. 서버 실행 확인
```bash
venv/bin/uvicorn main:app --reload
```
브라우저에서 http://127.0.0.1:8000/docs 접속해서 Swagger가 뜨면 정상.

## 6. 프론트엔드 실행
`frontend/index.html`을 VSCode Live Server로 열기. (Live Server 확장이
설치 안 되어 있으면 VSCode 확장 마켓에서 "Live Server" 검색 후 설치)

`frontend/script.js`의 `API_BASE`가 지금 무엇을 가리키는지 항상 먼저 확인:
- 로컬 백엔드로 테스트하려면 → `http://127.0.0.1:8000`
- 실제 배포판을 그대로 쓰려면 → `https://codyssey-m1-2-92sp.onrender.com` (건드릴 필요 없음)

## 7. (보너스 기능) MCP 관련 재설정
MCP 클라이언트 테스트(`mcp_client_test.py`)를 다시 돌리려면 Node.js가 필요합니다.
새 컴퓨터라면 다시 설치해야 합니다.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.zshrc      # 또는 터미널 재시작
nvm install --lts
```

그다음:
```bash
venv/bin/python mcp_client_test.py
```

---

## 8. 자주 쓰는 주소 모음

| 용도 | 주소 |
|---|---|
| 프론트엔드 (배포) | https://codyssey-m1-2-alpha.vercel.app |
| 백엔드 API (배포) | https://codyssey-m1-2-92sp.onrender.com |
| Swagger UI (배포) | https://codyssey-m1-2-92sp.onrender.com/docs |
| Render 대시보드 | https://dashboard.render.com |
| Vercel 대시보드 | https://vercel.com/dashboard |
| Firebase 콘솔 | https://console.firebase.google.com |
| Codyssey API 콘솔 | https://usr.codyssey.kr/public-api-console |
| GitHub 저장소 | https://github.com/Xn0w/codyssey_M1-2 |

## 9. 코드를 고친 뒤 재배포하는 법
```bash
git add .
git commit -m "변경 내용 설명"
git push
```
- **Render**: push 감지 시 자동 재배포 (대시보드에서 진행 상황 확인 가능)
- **Vercel**: push 감지 시 자동 재배포
- 둘 다 몇 분 정도 걸리니, 배포 완료(Live 상태) 확인 후 테스트할 것