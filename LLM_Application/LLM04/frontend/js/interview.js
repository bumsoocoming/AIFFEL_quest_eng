// ── 상태 ─────────────────────────────────────────────
let memories = [];         // 수집된 기억 목록
let isRecording = false;
let recognition = null;

const PRESET_MEMORIES = [
  { text: '딸이 시집가던 날에 너무 기뻐서 그만 눈물이 왈칵 났었어요.', category: '감정긍정' },
  { text: '겨울이면 부엌 아궁이 앞에서 마시던 구수한 보리차가 생각납니다.', category: '장소' },
  { text: '비록 넉넉지 않았어도 온 동네 아이들이 오솔길 따라 웃으며 뛰어놀았지요.', category: '장소' },
  { text: '마당 큰 평상에서 온 가솔이 옹기종기 둘러앉아 밥을 나누어 먹었습니다.', category: '관계' },
];

// ── STT 초기화 ────────────────────────────────────────
function initSTT() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return null;
  const r = new SpeechRecognition();
  r.lang = 'ko-KR';
  r.interimResults = true;
  r.continuous = false;
  r.onresult = (e) => {
    const transcript = Array.from(e.results).map(r => r[0].transcript).join('');
    document.getElementById('stt-bubble-text').textContent = `"${transcript}"`;
    if (e.results[e.results.length - 1].isFinal) {
      sendUtterance(transcript);
    }
  };
  r.onerror = () => stopRecording();
  r.onend = () => stopRecording();
  return r;
}

// ── 마이크 토글 ───────────────────────────────────────
function toggleMic() {
  isRecording ? stopRecording() : startRecording();
}

function startRecording() {
  recognition = initSTT();
  if (!recognition) {
    showToast('⚠️ 이 브라우저는 음성 인식을 지원하지 않습니다. Chrome을 사용해주세요.');
    return;
  }
  isRecording = true;
  recognition.start();
  document.getElementById('mic-btn').classList.add('recording');
  document.getElementById('mic-status').textContent = '귀를 기울여 듣고 있습니다...';
  document.getElementById('mic-status').className = 'mic-status listening';
}

function stopRecording() {
  isRecording = false;
  recognition?.stop();
  document.getElementById('mic-btn').classList.remove('recording');
  document.getElementById('mic-status').textContent = '마이크를 터치하면 이야기가 시작됩니다';
  document.getElementById('mic-status').className = 'mic-status';
}

// ── 발화 처리 → API 호출 ──────────────────────────────
async function sendUtterance(text) {
  if (!text.trim()) return;
  document.getElementById('mic-status').textContent = 'AI가 이야기를 듣고 있습니다...';
  document.getElementById('mic-status').className = 'mic-status done';

  try {
    const data = await apiPost('/interview', { text });
    // 기억 저장
    memories.push({ text, category: data.category });
    renderMemoryList();
    // AI 질문 업데이트
    document.getElementById('ai-question-text').textContent = `"${data.question}"`;
    showToast(`✅ [${data.category}] 기억이 기록되었습니다`);
  } catch (e) {
    // API 미연결 시 프리셋 메시지로 fallback
    document.getElementById('ai-question-text').textContent =
      '"그때 어떤 느낌이셨나요? 조금 더 이야기해 주시겠어요?"';
    showToast('서버에 연결할 수 없어 오프라인 모드로 동작합니다.');
  }
}

// ── 프리셋 클릭 ───────────────────────────────────────
function selectPreset(idx) {
  const m = PRESET_MEMORIES[idx];
  document.getElementById('stt-bubble-text').textContent = `"${m.text}"`;
  document.querySelectorAll('.preset-btn').forEach((b, i) => {
    b.classList.toggle('active', i === idx);
  });
  sendUtterance(m.text);
}

// ── 기억 목록 렌더링 ──────────────────────────────────
function renderMemoryList() {
  const list = document.getElementById('memory-list');
  list.innerHTML = memories.map(m => `
    <div class="memory-item">
      <span class="memory-cat">${m.category}</span>
      <span style="font-size:14px;font-weight:700;flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis">${m.text}</span>
    </div>
  `).join('');
  document.getElementById('memory-count').textContent = memories.length;
}

// ── 스토리북 생성 이동 ────────────────────────────────
function goToStorybook() {
  if (memories.length === 0) {
    showToast('먼저 이야기를 들려주세요! 마이크를 눌러보세요.');
    return;
  }
  switchTab('storybook');
  generateStorybook();
}
