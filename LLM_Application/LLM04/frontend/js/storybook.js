// ── 상태 ─────────────────────────────────────────────
let storybookData = null;
let currentPage = 0;

const DEMO_STORYBOOK = {
  title: '나의 소중한 인생 이야기',
  pages: [
    { page: 1, title: '인생의 시작', theme: '태어난 곳', body: '산과 들이 어우러진 고향 마을에서, 어머니의 따뜻한 품에 안겨 세상과 첫 인사를 나눴습니다. 그 시절 돌담길과 마당의 감나무는 지금도 눈에 선합니다.' },
    { page: 2, title: '꿈과 희망', theme: '어린 시절 꿈', body: '비록 가난했지만 꿈만큼은 하늘처럼 높았습니다. 언젠가는 도시에 나가 공부를 하고 싶었고, 부모님을 행복하게 해드리고 싶은 마음이 가슴 한켠에 늘 가득했습니다.' },
    { page: 3, title: '첫 번째 도전', theme: '학교와 시작', body: '처음 학교에 입학하던 날의 설렘은 지금도 잊히지 않습니다. 새 책가방을 메고 이슬 맺힌 오솔길을 걸어가던 그 아침이, 긴 인생의 첫 발걸음이었습니다.' },
    { page: 4, title: '사랑과 가족', theme: '결혼과 가정', body: '봄날 벚꽃이 흩날리던 날, 평생의 반려자를 만났습니다. 아이들이 태어나고 자라는 것을 바라보며, 삶의 진정한 의미를 하나씩 배워나갔습니다.' },
    { page: 5, title: '기쁨의 순간들', theme: '행복한 기억', body: '딸이 시집가던 날 흘린 눈물은 슬픔이 아니라 축복이었습니다. 그리고 그 눈물 속에서 삶이 얼마나 아름다운지를 다시 한번 깨달았습니다.' },
    { page: 6, title: '고난과 극복', theme: '힘든 시절', body: '어렵고 힘든 시절도 있었지만, 가족이 있었기에 버틸 수 있었습니다. 넘어질 때마다 다시 일어서게 해준 것은 사랑하는 사람들의 웃음이었습니다.' },
    { page: 7, title: '소중한 인연들', theme: '잊지 못할 사람들', body: '살면서 만난 수많은 인연들이 저의 인생을 풍성하게 만들어 주었습니다. 특히 어린 시절 함께 뛰어놀던 동무들과 처음 가르침을 주신 선생님은 평생 잊을 수 없습니다.' },
    { page: 8, title: '고향과 추억', theme: '고향 풍경', body: '비록 지금은 멀리 떨어져 있지만, 고향의 산과 냇가는 꿈속에서도 또렷합니다. 황금빛 논밭과 시골길의 흙냄새가 그리울 때면, 마음은 저절로 그곳으로 달려갑니다.' },
    { page: 9, title: '인생의 지혜', theme: '삶의 깨달음', body: '긴 인생을 살아오면서 깨달은 것은 단 하나입니다. 소박하게, 감사하게, 그리고 사랑하는 사람들과 함께 살아가는 것이 가장 큰 행복이라는 것을요.' },
    { page: 10, title: '미래 세대에게', theme: '자손들에게', body: '사랑하는 자손들에게 전하고 싶습니다. 평범한 하루하루가 얼마나 소중한지를, 그리고 서로를 아끼고 사랑하는 것이 얼마나 값진 일인지를 잊지 말아달라고요.' },
  ],
};

// ── 스토리북 생성 ──────────────────────────────────────
async function generateStorybook() {
  if (memories.length === 0 && !storybookData) {
    // 데모 데이터로 표시
    storybookData = DEMO_STORYBOOK;
    renderBook();
    return;
  }

  showBookLoading(true);
  try {
    const data = await apiPost('/storybook', { memories });
    storybookData = data;
    showToast('📖 스토리북이 완성되었습니다!');
  } catch {
    storybookData = DEMO_STORYBOOK;
    showToast('오프라인 모드: 데모 스토리북을 표시합니다.');
  } finally {
    showBookLoading(false);
    currentPage = 0;
    renderBook();
  }
}

function showBookLoading(show) {
  document.getElementById('book-loading').classList.toggle('show', show);
  document.getElementById('book-spread').style.display = show ? 'none' : '';
}

// ── 페이지 렌더링 ─────────────────────────────────────
function renderBook() {
  if (!storybookData) return;
  const page = storybookData.pages[currentPage];
  if (!page) return;

  document.getElementById('book-chapter-badge').textContent = `제 ${page.page} 장`;
  document.getElementById('book-theme').textContent = page.theme;
  document.getElementById('book-title').textContent = page.title;
  document.getElementById('book-body').textContent = page.body;
  document.getElementById('book-page-num').textContent = `${currentPage + 1} / ${storybookData.pages.length} 쪽`;
  document.getElementById('book-storybook-title').textContent = storybookData.title;

  // 이미지: output 폴더 또는 placeholder
  const imgEl = document.getElementById('book-art-img');
  const num = String(currentPage + 1).padStart(2, '0');
  imgEl.src = `images/output/${num}_watercolor_16x9.png`;
  imgEl.onerror = () => {
    imgEl.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='500' height='500'%3E%3Crect width='500' height='500' fill='%23FBF8F3'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='serif' font-size='28' fill='%23D97B3F'%3E${page.page}%EC%9E%A5%3C/text%3E%3C/svg%3E`;
  };
}

function turnPage(dir) {
  if (!storybookData) return;
  currentPage = (currentPage + dir + storybookData.pages.length) % storybookData.pages.length;
  renderBook();
}

// ── 영상 대본으로 이동 ────────────────────────────────
function goToVideoScript() {
  if (!storybookData) {
    showToast('먼저 스토리북을 생성해주세요.');
    return;
  }
  switchTab('video');
  generateVideoScript();
}
