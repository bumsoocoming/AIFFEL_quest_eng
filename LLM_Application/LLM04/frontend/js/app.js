const API_BASE = 'http://localhost:8000/api';

// ── 탭 전환 ──────────────────────────────────────────
function switchTab(id) {
  document.querySelectorAll('.tab-view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.tab-nav-btn').forEach(b => {
    b.classList.remove('active-tab');
    b.classList.add('inactive-tab');
  });
  document.getElementById(`view-${id}`)?.classList.add('active');
  document.getElementById(`nav-${id}`)?.classList.add('active-tab');
  document.getElementById(`nav-${id}`)?.classList.remove('inactive-tab');
}

// ── 토스트 ────────────────────────────────────────────
function showToast(msg, duration = 2800) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), duration);
}

// ── API 호출 ─────────────────────────────────────────
async function apiPost(path, body) {
  const res = await fetch(API_BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── 초기화 ────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  switchTab('interview');
  checkModelStatus();
});

async function checkModelStatus() {
  try {
    const res = await fetch(API_BASE + '/model/status');
    const data = await res.json();
    if (!data.loaded) {
      showToast('⚠️ 모델 미로드 상태. train_5cat.csv를 data/ 폴더에 넣고 /api/train을 호출하세요.', 5000);
    }
  } catch {
    // 서버 미실행 시 조용히 무시
  }
}
