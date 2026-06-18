"""
Day 8 자율 프로젝트 - 한국어 감정 분석 Streamlit 프론트엔드
사용자 입력 → API 호출 → 결과 표시
"""
import streamlit as st
import requests

st.set_page_config(page_title="한국어 감정 분석", page_icon="🎭", layout="centered")

API_BASE = "http://localhost:8000"

# ===== 사이드바: 설정 =====
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("API Key", value="test-key-001", type="password")

    # 서버 상태
    try:
        health = requests.get(f"{API_BASE}/health", timeout=3).json()
        if health.get("status") == "healthy":
            st.success("🟢 서버 연결됨")
            st.caption(f"모델: {health.get('model')}")
        else:
            st.warning("🟡 모델 로딩 중...")
    except Exception:
        st.error("🔴 서버 연결 실패")
    st.caption("Korean Sentiment Analysis v1.0")


# ===== 메인 =====
st.title("🎭 한국어 감정 분석")
st.write("한국어 문장을 입력하면 **긍정 / 부정 / 중립**을 분석합니다.")

text = st.text_area(
    "분석할 문장:",
    placeholder="예: 오늘 주가가 크게 올랐습니다",
    height=120,
)

if st.button("🔍 감정 분석", type="primary", use_container_width=True):
    if not text.strip():
        st.warning("문장을 입력하세요.")
    else:
        with st.spinner("분석 중..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/predict",
                    json={"text": text},
                    headers={"X-API-Key": api_key},
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                st.session_state["last_result"] = result
            except requests.exceptions.HTTPError as e:
                code = e.response.status_code
                if code == 401:
                    st.error("🔑 인증 실패 — API Key를 확인하세요.")
                elif code == 422:
                    st.error("⚠️ 입력이 올바르지 않습니다 (1~2000자).")
                else:
                    st.error(f"❌ 서버 에러 (HTTP {code})")
            except requests.exceptions.ConnectionError:
                st.error("🔌 서버에 연결할 수 없습니다. 백엔드 실행을 확인하세요.")
            except Exception as e:
                st.error(f"❌ 오류: {type(e).__name__}")

# ===== 결과 표시 =====
if "last_result" in st.session_state:
    r = st.session_state["last_result"]
    label = r["label"]
    emoji = {"positive": "😀", "negative": "😡", "neutral": "😐"}.get(label, "🤔")
    color = {"positive": "green", "negative": "red", "neutral": "gray"}.get(label, "blue")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.metric("예측 감정", f"{emoji} {label}")
    with c2:
        st.metric("확신도", f"{r['confidence']:.1%}")

    if r.get("scores"):
        st.subheader("📊 감정별 점수")
        for lbl, score in sorted(r["scores"].items(), key=lambda x: -x[1]):
            st.progress(float(score), text=f"{lbl}: {score:.1%}")

    st.caption(f"인증 사용자: {r.get('user', '?')}")
