# prototypes — 실행 코드

아이펠톤 기간에 만든 실행 가능한 프로토타입입니다.
논문의 분석 대상인 Panelogue 토론 로그는 `analysis/` 와 `experiments/` 에 있고,
여기는 그 앞뒤로 만든 코드들입니다.

| 폴더 | 내용 |
|---|---|
| `cheonggang-mas/` | 청강 멀티에이전트 시스템. 시나리오 · 템플릿 · 출력 샘플 포함 |
| `omnivoice/` | OmniVoice 라이브러리 — 문서, 예제, 테스트 |
| `omnivoice-app/` | OmniVoice 응용 앱 |
| `persona-meeting/` | 페르소나 회의 배포판 — 로그 포함 |
| `API_설치안내.md` | 팀원용 API 키 설정 안내 |

## 비밀값 처리

- **`.env` 파일은 넣지 않았습니다.** 실제 키가 들어 있었습니다.
- `persona-meeting/.env.example` 에는 실제 키가 들어가 있어서 `[REDACTED]` 로 지우고 넣었습니다.
  원래 `.env.example` 은 자리표시자만 있어야 하는 파일입니다.
- 각 프로토타입을 돌리려면 `.env` 를 직접 만들어야 합니다.

```
OPENROUTER_API_KEY=발급받은_키
```

## 가상환경

`cheonggang-mas/.venv` (4,700여 개 파일 · 57MB)는 넣지 않았습니다.
`requirements.txt` 로 다시 만드세요.

```bash
cd prototypes/cheonggang-mas
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```
