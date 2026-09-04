from __future__ import annotations

import os
import time
from dataclasses import dataclass

from openai import OpenAI, RateLimitError, APIStatusError


@dataclass
class LLMConfig:
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 700


def detect_provider(explicit: str = "auto") -> str:
    if explicit and explicit != "auto":
        return explicit
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "dry"


def default_model(provider: str) -> str:
    if provider == "gemini":
        return os.getenv("MAS_MODEL") or "gemini-3.6-flash"
    if provider == "openai":
        return os.getenv("MAS_MODEL") or "gpt-4o-mini"
    if provider == "anthropic":
        return os.getenv("MAS_MODEL") or "claude-fable-5"
    return "dry-mock"


def make_client(provider: str) -> OpenAI | None:
    if provider == "openai":
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if provider == "gemini":
        return OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
    if provider == "anthropic":
        # Anthropic OpenAI 호환 엔드포인트. 키는 ANTHROPIC_API_KEY.
        return OpenAI(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            base_url="https://api.anthropic.com/v1/",
        )
    return None


class ChatModel:
    def __init__(self, cfg: LLMConfig):
        self.cfg = cfg
        self.client = make_client(cfg.provider)

    def complete(self, system: str, user: str) -> str:
        if self.cfg.provider == "dry" or self.client is None:
            return _dry_reply(system, user)
        kwargs = {
            "model": self.cfg.model,
            "temperature": self.cfg.temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        # Gemini 호환 엔드포인트는 max_tokens를 입력+출력로 세는 경우가 있다.
        if self.cfg.max_tokens:
            kwargs["max_tokens"] = self.cfg.max_tokens
        last_err: Exception | None = None
        if self.cfg.provider != "dry":
            time.sleep(1.2)
        for attempt in range(5):
            try:
                resp = self.client.chat.completions.create(**kwargs)
                choice = resp.choices[0]
                text = choice.message.content or ""
                reason = getattr(choice, "finish_reason", None)
                if reason and reason not in ("stop", "end_turn"):
                    text += f"\n\n[finish_reason={reason}]"
                return text.strip()
            except RateLimitError as exc:
                last_err = exc
                wait = 15 * (attempt + 1)
                print(f"할당량 대기 {wait}s ({attempt + 1}/5)")
                time.sleep(wait)
            except APIStatusError as exc:
                last_err = exc
                if exc.status_code in {429, 503, 500}:
                    wait = 10 * (attempt + 1)
                    print(f"API {exc.status_code}, {wait}s 후 재시도")
                    time.sleep(wait)
                    continue
                raise
        raise RuntimeError("모델 호출이 반복 실패했습니다.") from last_err


def _dry_reply(system: str, user: str) -> str:
    if "JSON만" in user or "합의문" in user or "정책보좌관" in system:
        return (
            "{\n"
            '  "outcome_type": "PARTIAL",\n'
            '  "stop_work": true,\n'
            '  "survey_months": 8,\n'
            '  "preservation_share_percent": 30,\n'
            '  "developer_pays_excavation": true,\n'
            '  "delay_months": 10,\n'
            '  "resident_compensation": "입주 지연 시 주거비 지원 협의",\n'
            '  "illegal_actions": [],\n'
            '  "unresolved": ["추가 국비 지원 여부"],\n'
            '  "summary": "[드라이런] B-3 유구 범위는 정밀조사 후 확정하고, '
            "조사 기간 8개월 동안 공사를 중지한다. 상업 기능은 우회 배치를 검토한다. "
            '문화재 절차를 지키며 주민 보상과 정밀조사를 병행한다."\n'
            "}"
        )
    if "조정관" in system:
        return (
            "쟁점은 세 가지다. 정밀조사 기간을 8개월로 둘지, "
            "B-3를 우회할지 공원화할지, 입주 지연 보상을 누가 얼마나 할지."
        )
    if "시행사" in system:
        return (
            "즉시 중지는 받겠습니다. 다만 전면 공원화는 분양 구조를 무너뜨립니다. "
            "B-3 상업 기능을 우회로 살릴 안을 먼저 검토합시다. "
            "공기가 장기 지연되면 시공 위약과 입주 지연이 겹칩니다."
        )
    if "문화재청" in system:
        return (
            "발견 즉시 중지·신고가 맞습니다. 가치 확인 전에 기록 후 개발을 "
            "오늘 합의할 수는 없습니다. 건물지 이전 보존은 내부적으로 부적합입니다."
        )
    if "조사단" in system:
        return (
            "지금 30%는 추정입니다. 인접 녹지로 이어질 수 있어 정밀조사가 필요합니다. "
            "최소 8개월입니다. 두세 달로 줄이면 보고서 서명에 반대합니다."
        )
    if "주민" in system:
        return (
            "입주가 1년 이상 밀리면 전세와 학교가 한꺼번에 무너집니다. "
            "보상 없는 지연은 받을 수 없습니다. 남는다면 울타리가 아니라 "
            "주민이 쓰는 학습 공간이어야 합니다."
        )
    if "정책보좌관" in system:
        return (
            "{\n"
            '  "outcome_type": "PARTIAL",\n'
            '  "stop_work": true,\n'
            '  "survey_months": 8,\n'
            '  "preservation_share_percent": 30,\n'
            '  "developer_pays_excavation": true,\n'
            '  "delay_months": 10,\n'
            '  "resident_compensation": "지연 시 주거 지원",\n'
            '  "illegal_actions": [],\n'
            '  "unresolved": [],\n'
            '  "summary": "[드라이런 단일] 즉시 중지 후 정밀조사, 일부 보존·우회 개발."\n'
            "}"
        )
    return "[드라이런] 입장을 유지합니다. 오늘 합의문에 숫자 근거를 남깁시다."
