// ===== 설정 =====
// 배포 시에는 이 값을 Render에서 발급받은 실제 백엔드 주소로 바꿔주세요.
const API_BASE = "https://codyssey-m1-2-92sp.onrender.com";

let currentConversationId = null;

// ===== 탭 전환 =====
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");

    // 탭을 열 때마다 최신 데이터를 다시 불러온다
    if (btn.dataset.tab === "data") loadDataList();
    if (btn.dataset.tab === "history") loadConversationList();
  });
});

// ===== 탭1: 채팅 =====
async function loadSummary() {
  const box = document.getElementById("summary-box");
  try {
    const res = await fetch(`${API_BASE}/api/data/summary`);
    const s = await res.json();
    if (s.count === 0) {
      box.textContent = "아직 저장된 데이터가 없습니다. '데이터 관리' 탭에서 먼저 추가해보세요.";
      return;
    }
    box.textContent =
      `기간 ${s.period.start}~${s.period.end} · 개수 ${s.count} · ` +
      `평균 ${s.average} · 최근 추세 ${s.recent_trend}`;
  } catch (err) {
    box.textContent = "요약 정보를 불러오지 못했습니다.";
  }
}

function appendMessage(role, content) {
  const log = document.getElementById("chat-log");
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = content;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

document.getElementById("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (!message) return;

  appendMessage("user", message);
  input.value = "";
  document.getElementById("chat-loading").classList.remove("hidden");

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, conversation_id: currentConversationId }),
    });
    const data = await res.json();
    currentConversationId = data.conversation_id;
    appendMessage("assistant", data.reply);
  } catch (err) {
    appendMessage("assistant", "오류가 발생했습니다. 서버 상태를 확인해주세요. (무료 서버는 첫 요청 시 최대 1분 정도 걸릴 수 있습니다)");
  } finally {
    document.getElementById("chat-loading").classList.add("hidden");
  }
});

// ===== 탭2: 데이터 관리 (CRUD) =====
async function loadDataList() {
  const tbody = document.querySelector("#data-table tbody");
  tbody.innerHTML = "";
  const res = await fetch(`${API_BASE}/api/data`);
  const items = await res.json();
  items.forEach((item) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.date}</td>
      <td>${item.value}</td>
      <td>${item.memo || ""}</td>
      <td><button data-id="${item.id}" class="delete-btn">삭제</button></td>
    `;
    tbody.appendChild(tr);
  });

  document.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      await fetch(`${API_BASE}/api/data/${btn.dataset.id}`, { method: "DELETE" });
      loadDataList();
      loadSummary(); // 데이터가 바뀌었으니 요약도 새로고침
    });
  });
}

document.getElementById("data-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const date = document.getElementById("data-date").value;
  const value = parseFloat(document.getElementById("data-value").value);
  const memo = document.getElementById("data-memo").value;

  await fetch(`${API_BASE}/api/data`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date, value, memo }),
  });

  e.target.reset();
  loadDataList();
  loadSummary();
});

// ===== 탭3: 대화 기록 =====
async function loadConversationList() {
  const list = document.getElementById("conversation-list");
  list.innerHTML = "";
  const res = await fetch(`${API_BASE}/api/conversations`);
  const conversations = await res.json();

  conversations.forEach((conv) => {
    const li = document.createElement("li");
    li.textContent = `${conv.title} (${conv.created_at?.slice(0, 10) || ""})`;
    li.addEventListener("click", () => loadConversationDetail(conv.id));
    list.appendChild(li);
  });
}

async function loadConversationDetail(id) {
  const detail = document.getElementById("conversation-detail");
  const res = await fetch(`${API_BASE}/api/conversations/${id}`);
  const conv = await res.json();

  detail.innerHTML = `<h3>${conv.title}</h3>`;
  (conv.messages || []).forEach((m) => {
    const p = document.createElement("p");
    p.textContent = `[${m.role}] ${m.content}`;
    detail.appendChild(p);
  });

  // 이 대화를 이어서 채팅하고 싶을 때를 위해 현재 대화로 지정
  currentConversationId = id;
}

// ===== 다크 모드 토글 =====
const themeToggleBtn = document.getElementById("theme-toggle");

function applyTheme(isDark) {
  document.body.classList.toggle("dark", isDark);
  themeToggleBtn.textContent = isDark ? "☀️ 라이트 모드" : "🌙 다크 모드";
}

// 이전에 선택해둔 테마가 있으면 그대로 복원, 없으면 라이트 모드로 시작
const savedTheme = localStorage.getItem("theme");
applyTheme(savedTheme === "dark");

themeToggleBtn.addEventListener("click", () => {
  const isDark = !document.body.classList.contains("dark");
  applyTheme(isDark);
  localStorage.setItem("theme", isDark ? "dark" : "light");
});

// ===== 초기 로딩 =====
loadSummary();
