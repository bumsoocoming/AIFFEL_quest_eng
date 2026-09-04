# 옴니보이스 한국어 TTS 스튜디오

OmniVoice(600+ 언어 제로샷 TTS)를 한국어 UI로 감싼 로컬 웹 앱.

## 실행 (VS Code)

1. 이 폴더를 VS Code로 연다
2. `Ctrl + Shift + B` → 터미널에 진행 상황이 뜨고 브라우저가 자동으로 열린다
3. 첫 실행은 모델 다운로드 때문에 몇 분 걸린다 (D:\Dev\omnivoice\hf-cache 에 저장)

터미널에서 직접 실행하려면:

    D:\Dev\omnivoice\.venv\Scripts\python.exe app.py

## 기능

| 탭 | 하는 일 | 입력 |
| --- | --- | --- |
| ① 자동 음성 | 모델이 목소리를 알아서 고름 | 문장 |
| ② 목소리 디자인 | 성별·나이·음높이·속삭임으로 목소리 설계 | 문장 + 속성 |
| ③ 목소리 복제 | 참조 음성의 목소리로 읽음 | 문장 + 참조 음성(3~10초) |

- 생성된 wav는 `outputs/` 폴더에 자동 저장
- 마이크 녹음으로도 참조 음성을 넣을 수 있음

## 환경

- 가상환경: `D:\Dev\omnivoice\.venv` (Python 3.14, PyTorch CUDA)
- 모델 캐시: `D:\Dev\omnivoice\hf-cache`
- GPU: GTX 1660 (6GB) — float16 추론
- 원본 라이브러리: `../OmniVoice-master` (Apache-2.0)
