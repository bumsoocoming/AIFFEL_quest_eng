#!/usr/bin/env python3
"""옴니보이스 한국어 TTS 스튜디오.

OmniVoice(600+ 언어 제로샷 TTS)를 한국어 UI로 감싼 로컬 웹 앱.
- 자동 음성: 텍스트만 넣으면 모델이 목소리를 고른다
- 목소리 디자인: 성별·나이·음높이 등 속성으로 목소리를 만든다
- 목소리 복제: 3~10초 참조 음성을 올리면 그 목소리로 읽는다

실행:  python app.py   (첫 실행 시 모델을 내려받아 몇 분 걸린다)
"""

from __future__ import annotations

import os
from pathlib import Path

# 모델 캐시는 D 드라이브에 둔다. OneDrive 동기화와 C 드라이브 용량을 피한다.
CACHE_DIR = Path("D:/Dev/omnivoice/hf-cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HOME", str(CACHE_DIR))

OUT_DIR = Path(__file__).resolve().parent / "outputs"
OUT_DIR.mkdir(exist_ok=True)

import datetime

import gradio as gr
import numpy as np

MODEL_ID = "k2-fsa/OmniVoice"

# 지연 로딩: 앱은 바로 뜨고, 모델은 첫 생성 때 올린다.
_model = None


def _load_model():
    global _model
    if _model is None:
        import torch
        from omnivoice import OmniVoice

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device.startswith("cuda") else torch.float32
        _model = OmniVoice.from_pretrained(MODEL_ID, device_map=device, dtype=dtype)
    return _model


def _save_wav(waveform: np.ndarray, sr: int, mode: str) -> str:
    import soundfile as sf

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUT_DIR / f"{stamp}_{mode}.wav"
    sf.write(str(path), waveform, sr)
    return str(path)


def _generate(mode: str, text: str, instruct: str | None = None,
              ref_audio: str | None = None, ref_text: str | None = None,
              speed: float = 1.0):
    if not text or not text.strip():
        return None, "읽을 문장을 입력해 주세요."
    try:
        model = _load_model()
    except Exception as e:
        return None, f"모델 로딩 실패: {type(e).__name__}: {e}"

    kw = {"text": text.strip()}
    if speed and float(speed) != 1.0:
        kw["speed"] = float(speed)
    if instruct and instruct.strip():
        kw["instruct"] = instruct.strip()
    if mode == "복제":
        if not ref_audio:
            return None, "참조 음성을 올려 주세요 (3~10초 권장)."
        try:
            kw["voice_clone_prompt"] = model.create_voice_clone_prompt(
                ref_audio=ref_audio,
                ref_text=ref_text.strip() if ref_text and ref_text.strip() else None,
            )
        except Exception as e:
            return None, f"참조 음성 처리 실패: {type(e).__name__}: {e}"

    try:
        audio = model.generate(**kw)
    except Exception as e:
        return None, f"생성 실패: {type(e).__name__}: {e}"

    wav = (audio[0] * 32767).astype(np.int16)
    sr = model.sampling_rate
    saved = _save_wav(wav, sr, mode)
    return (sr, wav), f"완료. 저장: {saved}"


# ---- 목소리 디자인 속성 → instruct 문자열 ----

GENDER = {"선택 안 함": "", "여성": "female", "남성": "male"}
AGE = {"선택 안 함": "", "어린이": "child", "청년": "young adult",
       "중년": "middle-aged", "노년": "elderly"}
PITCH = {"선택 안 함": "", "매우 낮게": "very low pitch", "낮게": "low pitch",
         "보통": "", "높게": "high pitch", "매우 높게": "very high pitch"}
STYLE = {"선택 안 함": "", "속삭임": "whisper"}


def _design_instruct(gender, age, pitch, style, extra):
    parts = [GENDER[gender], AGE[age], PITCH[pitch], STYLE[style]]
    if extra and extra.strip():
        parts.append(extra.strip())
    return ", ".join(p for p in parts if p)


def gen_auto(text, speed):
    return _generate("자동", text, speed=speed)


def gen_design(text, gender, age, pitch, style, extra, speed):
    instruct = _design_instruct(gender, age, pitch, style, extra)
    if not instruct:
        return None, "속성을 하나 이상 골라 주세요. (모두 '선택 안 함'이면 자동 음성 탭과 같습니다)"
    return _generate("디자인", text, instruct=instruct, speed=speed)


def gen_clone(text, ref_audio, ref_text, speed):
    return _generate("복제", text, ref_audio=ref_audio, ref_text=ref_text, speed=speed)


def build_app() -> gr.Blocks:
    with gr.Blocks(title="옴니보이스 한국어 TTS 스튜디오",
                   theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "# 🎙️ 옴니보이스 한국어 TTS 스튜디오\n"
            "600개 이상 언어를 지원하는 제로샷 TTS. "
            "첫 생성 시 모델을 내려받아 몇 분 걸릴 수 있습니다. "
            "생성한 음성은 `outputs/` 폴더에 자동 저장됩니다."
        )
        speed = gr.Slider(0.5, 2.0, value=1.0, step=0.1,
                          label="말하기 속도 (1.0 = 보통)")

        with gr.Tabs():
            with gr.TabItem("① 자동 음성"):
                a_text = gr.Textbox(label="읽을 문장", lines=4,
                                    placeholder="안녕하세요. 옴니보이스 테스트입니다.")
                a_btn = gr.Button("음성 생성", variant="primary")
                a_audio = gr.Audio(label="결과", type="numpy")
                a_status = gr.Textbox(label="상태", interactive=False)
                a_btn.click(gen_auto, [a_text, speed], [a_audio, a_status])

            with gr.TabItem("② 목소리 디자인"):
                d_text = gr.Textbox(label="읽을 문장", lines=4)
                with gr.Row():
                    d_gender = gr.Dropdown(list(GENDER), value="선택 안 함", label="성별")
                    d_age = gr.Dropdown(list(AGE), value="선택 안 함", label="나이대")
                    d_pitch = gr.Dropdown(list(PITCH), value="선택 안 함", label="음높이")
                    d_style = gr.Dropdown(list(STYLE), value="선택 안 함", label="스타일")
                d_extra = gr.Textbox(
                    label="추가 지시 (영어, 선택)",
                    placeholder="예: british accent / 四川话")
                d_btn = gr.Button("음성 생성", variant="primary")
                d_audio = gr.Audio(label="결과", type="numpy")
                d_status = gr.Textbox(label="상태", interactive=False)
                d_btn.click(gen_design,
                            [d_text, d_gender, d_age, d_pitch, d_style, d_extra, speed],
                            [d_audio, d_status])
                gr.Markdown("> 디자인 모드는 중국어·영어 데이터로 학습되어 "
                            "한국어에서는 결과가 다소 불안정할 수 있습니다.")

            with gr.TabItem("③ 목소리 복제"):
                c_text = gr.Textbox(label="읽을 문장", lines=4)
                c_ref = gr.Audio(label="참조 음성 (3~10초 권장)",
                                 type="filepath", sources=["upload", "microphone"])
                c_ref_text = gr.Textbox(
                    label="참조 음성의 대사 (비우면 자동 인식)",
                    placeholder="참조 음성에서 말한 내용을 그대로 적으면 품질이 좋아집니다.")
                c_btn = gr.Button("음성 생성", variant="primary")
                c_audio = gr.Audio(label="결과", type="numpy")
                c_status = gr.Textbox(label="상태", interactive=False)
                c_btn.click(gen_clone, [c_text, c_ref, c_ref_text, speed],
                            [c_audio, c_status])
                gr.Markdown("> 참조 음성과 읽을 문장의 언어가 같을 때 발음이 가장 자연스럽습니다. "
                            "다른 언어면 참조 음성 언어의 억양이 섞입니다.")

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="127.0.0.1", server_port=7861, inbrowser=True)
