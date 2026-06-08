// ── 상태 ─────────────────────────────────────────────
let videoScripts = [];
let currentScript = 0;

// ── 영상 대본 생성 ────────────────────────────────────
async function generateVideoScript() {
  if (!storybookData) {
    showToast('먼저 스토리북을 생성해주세요.');
    return;
  }
  showVideoLoading(true);
  try {
    const data = await apiPost('/video-script', { storybook: storybookData });
    videoScripts = data.scripts;
    showToast('🎬 영상 대본이 완성되었습니다!');
  } catch {
    // 데모 대본 생성
    videoScripts = storybookData.pages.map(p => ({
      page: p.page,
      title: p.title,
      narration: p.body,
      subtitle: p.title,
      image_prompt: `watercolor illustration, Korean traditional house, warm sunset, ${p.theme}`,
      scene_direction: '따뜻한 수채화 풍경 장면',
    }));
    showToast('오프라인 모드: 데모 영상 대본을 표시합니다.');
  } finally {
    showVideoLoading(false);
    currentScript = 0;
    renderScript();
    renderDots();
  }
}

function showVideoLoading(show) {
  document.getElementById('video-loading').style.display = show ? 'flex' : 'none';
  document.getElementById('video-main').style.display = show ? 'none' : '';
}

// ── 대본 렌더링 ───────────────────────────────────────
function renderScript() {
  if (!videoScripts.length) return;
  const s = videoScripts[currentScript];
  document.getElementById('video-thumb-img').src =
    `images/output/${String(s.page).padStart(2, '0')}_watercolor_16x9.png`;
  document.getElementById('video-thumb-img').onerror = function() {
    this.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='360'%3E%3Crect width='640' height='360' fill='%232d241d'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='serif' font-size='28' fill='%23f7dfb3'%3EHERO%3C/text%3E%3C/svg%3E`;
  };
  document.getElementById('narration-text').textContent = `"${s.narration}"`;
  document.getElementById('direction-text').textContent = s.scene_direction;
  document.getElementById('subtitle-text').textContent = s.subtitle;
  document.getElementById('script-page-info').textContent = `${currentScript + 1} / ${videoScripts.length}`;
}

function renderDots() {
  const wrap = document.getElementById('script-dots');
  wrap.innerHTML = videoScripts.map((_, i) => `
    <span class="script-dot${i === currentScript ? ' active' : ''}" onclick="goToScript(${i})"></span>
  `).join('');
}

function goToScript(idx) {
  currentScript = idx;
  renderScript();
  renderDots();
}
function prevScript() { goToScript((currentScript - 1 + videoScripts.length) % videoScripts.length); }
function nextScript() { goToScript((currentScript + 1) % videoScripts.length); }

// ── 낭독 모달 ─────────────────────────────────────────
function openNarrationModal() {
  if (!videoScripts.length) return;
  const s = videoScripts[currentScript];
  document.getElementById('modal-text').textContent = `"${s.narration}"`;
  document.getElementById('narration-modal').classList.add('open');

  // 브라우저 TTS
  if ('speechSynthesis' in window) {
    const utter = new SpeechSynthesisUtterance(s.narration);
    utter.lang = 'ko-KR';
    utter.rate = 0.88;
    utter.pitch = 1.0;
    window.speechSynthesis.speak(utter);
  }
}

function closeNarrationModal() {
  document.getElementById('narration-modal').classList.remove('open');
  window.speechSynthesis?.cancel();
}
