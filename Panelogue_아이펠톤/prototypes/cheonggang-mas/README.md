# 청강 신도시 — 역할 시나리오 멀티에이전트

신도시 공사 중 유물이 나왔을 때, 시행사·문화재청·조사단·주민·조정관이 각자 입장과 비밀 정보를 들고 대응안을 만든다. 학교 과제용으로 **단일 모델 대책**과 **역할 분리 토론**을 같은 채점표로 비교한다.

가상 사례다. 하남 교산 같은 실제 충돌을 모티브로 했지만 특정 지구를 재연하지 않는다.

## 준비

Python 3.10+ 가 있으면 된다. 이 컴퓨터에는 이미 `openai`, `yaml`이 있다.

```text
cd C:\Users\Admin\Documents\cheonggang-mas
copy .env.example .env
```

`.env`에 `OPENAI_API_KEY` 또는 `GEMINI_API_KEY` 중 하나만 넣는다. 이 컴퓨터의 OpenAI 키는 거절되므로 Gemini를 기본으로 두었다. 1주 판은 토론 1라운드라 멀티 1회가 호출 5번, 전체 6회가 약 18번이다. 한도가 끊기면 끝난 회차만 남기고 다음 날 같은 명령을 다시 치면 된다.

## 실행

1주 최소실험(단일 3 + 멀티 3, 토론 1라운드):

```text
py -3.12 run.py --mode week
```

파이프라인만 확인:

```text
py -3.12 run.py --dry-run --mode week
```

역할극만 1회:

```text
py -3.12 run.py --mode multi --rounds 1
```

결과는 `outputs/<시간>_<mode>/` 아래 `transcript.md`, `run.json`, `score.txt`로 저장된다. 모아 보려면:

```text
py -3.12 score.py outputs
```

Gemini를 쓰려면:

```text
py -3.12 run.py --provider gemini --mode multi
```

## 역할

| 역할 | 이름 | 남에게 안 주는 정보 |
| --- | --- | --- |
| 시행사 본부장 | 박도윤 | 월 45억 시공 위약, 이사회 은폐 압박 |
| 문화재청 사무관 | 이수현 | 유사 사례 고발, 이전 보존 반려 방침 |
| 조사단장 | 최민재 | 정밀조사 최소 8개월, 녹지 쪽 연장 가능 |
| 주민대표 | 한소영 | 지연 반대 62% / 공원 찬성 41%, 초등 교육 수요 |
| 조정관 | 정하린 | 없음. 말한 것만 합의문에 적는다 |

공개 브리핑은 `scenario/briefing.md`, 페르소나는 `scenario/agents.yaml`, 채점 규칙은 `scenario/constraints.yaml`이다.

## 채점이 보는 것

정답 유형은 없다. 전면 보존, 일부 보존, 기록 후 개발, 교착 모두 가능하다. 감점하는 것은 은폐·강행, 8개월보다 짧은 정밀조사, 국비 전액 확정, 지연 없는 척, 이해당사자 누락이다.

자동 점수는 키워드 보조다. 발표용 표는 `templates/human_scorecard.csv`를 사람이 채운다.

1주 일정은 `과제_가이드.md`, 보고서 빈칸은 `보고서_초안.md`에 있다.
