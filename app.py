import streamlit as st
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError, APITimeoutError
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import tempfile
import html
import json
import base64
import os
import streamlit.components.v1 as components
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import time

load_dotenv()


# =========================================================
# 1. Streamlit 기본 설정
# =========================================================
st.set_page_config(
    page_title="Life Talk",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# 2. 전체 디자인 + 모바일 반응형
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background:
            linear-gradient(
                180deg,
                #FFF8D8 0%,
                #FFFDF1 50%,
                #FFF7CF 100%
            );
    }

    .block-container {
        max-width: 900px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    html, body, [class*="css"] {
        font-family: "Malgun Gothic", "Arial", sans-serif;
    }

    p {
        font-size: 20px !important;
        line-height: 1.75 !important;
    }

    label {
        font-size: 20px !important;
        font-weight: 800 !important;
        color: #47391F !important;
    }

    textarea {
        font-size: 21px !important;
        line-height: 1.65 !important;
        border-radius: 18px !important;
        padding: 16px !important;
        background-color: #FFFDF8 !important;
        border: 1px solid #E8DEC8 !important;
    }

    .stButton > button {
        width: 100%;
        min-height: 64px;
        border-radius: 20px;
        border: none;
        font-size: 21px !important;
        font-weight: 900 !important;
        color: white !important;
        background:
            linear-gradient(
                90deg,
                #FFAE42 0%,
                #F5C35B 50%,
                #4EC9B0 100%
            );
        box-shadow: 0 5px 14px rgba(120, 100, 40, 0.12);
        transition: 0.2s;
        white-space: normal !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        color: white !important;
        border: none;
    }

    audio {
        width: 100%;
        margin-top: 8px;
    }

    hr {
        margin-top: 28px;
        margin-bottom: 28px;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .hero-card {
        width: 100%;
        box-sizing: border-box;
        background: linear-gradient(135deg, #FFF0A6, #FFFBE7);
        border: 1px solid #F1D36D;
        border-radius: 30px;
        padding: 38px 28px;
        text-align: center;
        margin-bottom: 38px;
        box-shadow: 0 8px 22px rgba(120, 100, 40, 0.08);
        overflow: hidden;
    }

    .hero-icons {
        font-size: 62px;
        margin-bottom: 6px;
        line-height: 1.2;
    }

    .hero-title {
        font-size: 46px;
        font-weight: 900;
        color: #183852;
        line-height: 1.2;
    }

    .hero-subtitle {
        font-size: 23px;
        font-weight: 900;
        color: #3482A1;
        margin-top: 8px;
        line-height: 1.45;
    }

    .hero-ko {
        font-size: 23px;
        font-weight: 800;
        color: #6B4A18;
        margin-top: 16px;
        line-height: 1.55;
        word-break: keep-all;
        overflow-wrap: break-word;
    }

    .section-title {
        font-size: 31px;
        font-weight: 900;
        color: #263B45;
        margin-bottom: 8px;
        line-height: 1.35;
        word-break: keep-all;
    }

    .mic-guide {
        width: 100%;
        box-sizing: border-box;
        background: linear-gradient(90deg, #FFF2B5, #FFE89A);
        border: 2px solid #F1C34A;
        border-radius: 24px 24px 0 0;
        padding: 24px 20px 18px 20px;
        text-align: center;
        font-size: 24px;
        font-weight: 900;
        color: #5B4216;
        line-height: 1.5;
        word-break: keep-all;
        overflow-wrap: break-word;
    }

    .mic-bottom {
        height: 10px;
        background: linear-gradient(90deg, #FFF2B5, #FFE89A);
        border-left: 2px solid #F1C34A;
        border-right: 2px solid #F1C34A;
        border-bottom: 2px solid #F1C34A;
        border-radius: 0 0 24px 24px;
        margin-top: -10px;
        margin-bottom: 24px;
        box-sizing: border-box;
    }

    .result-title {
        font-size: 30px;
        font-weight: 900;
        color: #243B45;
        margin-bottom: 15px;
        line-height: 1.35;
        word-break: keep-all;
    }

    .result-card {
        width: 100%;
        box-sizing: border-box;
        border-radius: 23px;
        padding: 27px;
        margin-bottom: 15px;
        font-size: 24px;
        font-weight: 900;
        line-height: 1.6;
        word-break: keep-all;
        overflow-wrap: break-word;
    }

    .english-card {
        background: linear-gradient(135deg, #E9FFF4, #F6FFF9);
        border: 1px solid #C4EBD8;
        color: #17664B;
    }

    .answer-card {
        background: linear-gradient(135deg, #EAF4FF, #F7FBFF);
        border: 1px solid #CBE1F5;
        color: #285D87;
    }

    .footer-note {
        text-align: center;
        color: #92A3A8;
        font-size: 15px;
        margin-top: 55px;
        padding-top: 20px;
        line-height: 1.5;
    }

    iframe,
    img {
        max-width: 100% !important;
    }


    /* =====================================================
       노트북 / 태블릿 화면
       ===================================================== */
    @media (min-width: 769px) and (max-width: 1200px) {

        .block-container {
            max-width: 95% !important;
            padding-top: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-bottom: 3rem !important;
        }

        .hero-card {
            padding: 28px 20px !important;
            border-radius: 24px !important;
            margin-bottom: 28px !important;
        }

        .hero-icons {
            font-size: 46px !important;
        }

        .hero-title {
            font-size: 38px !important;
        }

        .hero-subtitle {
            font-size: 20px !important;
        }

        .hero-ko {
            font-size: 20px !important;
        }

        .section-title {
            font-size: 27px !important;
        }

        .mic-guide {
            font-size: 21px !important;
            padding: 20px 16px !important;
        }

        .stButton > button {
            min-height: 56px !important;
            font-size: 18px !important;
        }

        textarea {
            font-size: 18px !important;
        }

        .result-title {
            font-size: 26px !important;
        }

        .result-card {
            font-size: 21px !important;
            padding: 22px !important;
        }
    }

    /* =====================================================
       휴대폰 화면
       ===================================================== */
    @media (max-width: 768px) {

        .block-container {
            max-width: 100% !important;
            padding-top: 0.7rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 0.55rem !important;
            padding-right: 0.55rem !important;
        }

        .hero-card {
            border-radius: 22px;
            padding: 22px 14px;
            margin-bottom: 24px;
        }

        .hero-icons {
            font-size: 38px;
            margin-bottom: 5px;
        }

        .hero-title {
            font-size: 36px;
        }

        .hero-subtitle {
            font-size: 18px;
            margin-top: 7px;
        }

        .hero-ko {
            font-size: 18px;
            margin-top: 12px;
            line-height: 1.55;
        }

        .section-title {
            font-size: 25px;
            margin-bottom: 10px;
        }

        .mic-guide {
            border-radius: 18px 18px 0 0;
            padding: 18px 12px 15px 12px;
            font-size: 19px;
            line-height: 1.45;
        }

        .mic-bottom {
            border-radius: 0 0 18px 18px;
            margin-bottom: 18px;
        }

        p {
            font-size: 16px !important;
            line-height: 1.55 !important;
        }

        label {
            font-size: 17px !important;
        }

        textarea {
            width: 100% !important;
            font-size: 17px !important;
            line-height: 1.55 !important;
            min-height: 105px !important;
            padding: 12px !important;
            box-sizing: border-box !important;
        }

        .stButton > button {
            width: 100% !important;
            min-height: 54px !important;
            border-radius: 16px !important;
            font-size: 17px !important;
            padding: 0.65rem 0.75rem !important;
        }

        .result-title {
            font-size: 24px;
            margin-bottom: 10px;
        }

        .result-card {
            border-radius: 18px;
            padding: 18px 14px;
            font-size: 19px;
            line-height: 1.55;
        }

        .footer-note {
            font-size: 13px;
            margin-top: 34px;
        }

        audio {
            width: 100% !important;
        }

        iframe {
            width: 100% !important;
            max-width: 100% !important;
        }
    }

    /* 탭 메뉴 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(255, 255, 255, 0.7);
        padding: 8px 12px;
        border-radius: 18px;
        border: 1px solid #EFE4CE;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 20px !important;
        font-weight: 900 !important;
        border-radius: 14px !important;
        padding: 12px 20px !important;
        color: #7D6B4E !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #183852 !important;
        box-shadow: 0 4px 12px rgba(120, 100, 40, 0.1) !important;
    }

    /* 연속 대화 카드 스타일 */
    .chat-history-container {
        display: flex;
        flex-direction: column;
        gap: 16px;
        margin-top: 24px;
        margin-bottom: 24px;
    }

    .chat-bubble-card {
        width: 100%;
        box-sizing: border-box;
        border-radius: 24px;
        padding: 22px 24px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
    }

    .card-my-turn {
        background: linear-gradient(135deg, #FFF9E6, #FFFDF8);
        border: 2px solid #F9E29B;
    }

    .chat-my-kor {
        font-size: 19px;
        font-weight: 800;
        color: #795548;
        margin-bottom: 10px;
        line-height: 1.5;
    }

    .chat-my-eng {
        font-size: 26px;
        font-weight: 900;
        color: #0E6655;
        line-height: 1.45;
        background-color: #E8F8F5;
        padding: 14px 18px;
        border-radius: 16px;
        border: 1px solid #A3E4D7;
        word-break: keep-all;
    }

    .card-ai-turn {
        background: linear-gradient(135deg, #EBF5FB, #F7FAFC);
        border: 2px solid #AED6F1;
    }

    .chat-ai-eng-title {
        font-size: 26px;
        font-weight: 900;
        color: #1B4F72;
        line-height: 1.45;
        background-color: #FFFFFF;
        padding: 14px 18px;
        border-radius: 16px;
        border: 1px solid #D4E6F1;
        margin-bottom: 10px;
        word-break: keep-all;
    }

    .chat-ai-kor-desc {
        font-size: 18px;
        font-weight: 800;
        color: #5D6D7E;
        line-height: 1.5;
        padding-left: 4px;
    }

    .chat-badge {
        display: inline-block;
        font-size: 14px;
        font-weight: 800;
        padding: 3px 8px;
        border-radius: 8px;
        margin-bottom: 6px;
    }

    .badge-user {
        background-color: #F7DC6F;
        color: #5D4037;
    }

    .badge-ai {
        background-color: #AED6F1;
        color: #1B4F72;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 2-1. 연속 대화 커스텀 컴포넌트 선언
# =========================================================
_continuous_chat_dir = os.path.join(os.path.dirname(__file__), "components", "continuous_chat")
continuous_chat_component = components.declare_component("continuous_chat", path=_continuous_chat_dir)


# =========================================================
# 3. 마이크 음성인식 (기존 문장별 연습용)
# =========================================================
def pretty_speech_to_text(language="ko", key=None):
    text = speech_to_text(
        language=language,
        start_prompt="🎤 말하기 시작",
        stop_prompt="⏹️ 말하기 종료",
        just_once=True,
        use_container_width=True,
        key=key,
    )

    if text:
        return text

    return None


# =========================================================
# 4. 상단 HERO
# =========================================================
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-icons">🎤 💬 🎧</div>
        <div class="hero-title">Life Talk</div>
        <div class="hero-subtitle">Speak Korean. Practice English.</div>
        <div class="hero-ko">한국어로 편하게 말하고 영어로 대화해 보세요.</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 5. OpenAI 설정
# =========================================================
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        api_key = None

if not api_key:
    st.error("OPENAI_API_KEY가 설정되어 있지 않습니다. .env 파일 또는 Streamlit Secrets를 확인해 주세요.")
    st.stop()

client = OpenAI(api_key=api_key)


def ask_ai(prompt):
    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )
    return response.output_text.strip()


# =========================================================
# 6. 한국어 → 쉬운 영어
# =========================================================
def make_easy_english(korean_text):
    prompt = f"""
다음 한국어 문장을 쉽고 자연스러운 영어 회화 문장으로 바꿔 주세요.

조건:
- 한국 중학교 1~2학년 정도의 쉬운 영어를 사용하세요.
- 실제 일상생활에서 자연스럽게 사용하는 영어를 사용하세요.
- 어려운 단어나 복잡한 문법은 피하세요.
- 문장은 가능하면 짧고 자연스럽게 작성하세요.
- 설명하지 마세요.
- 영어 문장만 출력하세요.
- 따옴표는 사용하지 마세요.

한국어:
{korean_text}
"""
    return ask_ai(prompt)


# =========================================================
# 7. 영어 대답
# =========================================================
def make_english_answer(english_sentence):
    prompt = f"""
상대방이 다음 영어 문장을 말했다고 생각하고
자연스러운 영어 대답을 만들어 주세요.

조건:
- 한국 중학교 1~2학년 정도의 쉬운 영어를 사용하세요.
- 친근하고 자연스러운 일상 대화처럼 답하세요.
- 1~2개의 짧은 문장으로 답하세요.
- 어려운 단어는 사용하지 마세요.
- 설명하지 마세요.
- 영어 대답만 출력하세요.
- 따옴표는 사용하지 마세요.

상대방:
{english_sentence}
"""
    return ask_ai(prompt)


# =========================================================
# 8. 영어 음성
# =========================================================
def make_audio(text):
    tts = gTTS(
        text=text,
        lang="en",
        slow=True,
    )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3",
    ) as fp:
        audio_path = fp.name

    tts.save(audio_path)

    with open(audio_path, "rb") as audio_file:
        return audio_file.read()


# =========================================================
# 8-1. 초고속 통합 AI 응답 (한글/영어 입력 지원 + gpt-4o-mini)
# =========================================================
def ask_continuous_turn(user_text, input_lang="ko", conversation_history=None):
    context = ""
    if conversation_history:
        recent = conversation_history[-2:]
        context = "Context: " + " | ".join([f"U:{h.get('user_eng','')} A:{h.get('ai_eng','')}" for h in recent]) + "\n"

    if input_lang == "en":
        sys_msg = (
            "You are an encouraging English conversation friend for a 6th grader in Korea. "
            "The user typed or spoke in English. "
            "Output JSON only with keys: "
            "\"user_eng\" (a polished, natural, conversational English sentence based on user's input. If already natural, keep it simple), "
            "\"ai_eng\" (1 short, friendly sentence reply in 6th grade level English), "
            "\"ai_kor\" (natural Korean meaning of ai_eng)."
        )
        user_msg = f"{context}User English: \"{user_text}\""
    else:
        sys_msg = (
            "You are an encouraging English tutor for a 6th grader in Korea. "
            "The user typed or spoke in Korean. "
            "Output JSON only with keys: "
            "\"user_eng\" (natural, easy spoken English translation of user's Korean), "
            "\"ai_eng\" (1 short, friendly sentence reply in 6th grade level English), "
            "\"ai_kor\" (natural Korean meaning of ai_eng)."
        )
        user_msg = f"{context}User Korean: \"{user_text}\""

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg}
            ],
            response_format={"type": "json_object"},
            max_tokens=150,
            temperature=0.7,
        )
        data = json.loads(completion.choices[0].message.content)
        return {
            "user_eng": data.get("user_eng", "").strip(),
            "ai_eng": data.get("ai_eng", "").strip(),
            "ai_kor": data.get("ai_kor", "").strip(),
        }
    except Exception as e:
        st.error(f"AI 연속대화 오류: {type(e).__name__}: {e}")

        if input_lang == "en":
            return {
                "user_eng": user_text,
                "ai_eng": "That sounds great! Tell me more about it.",
                "ai_kor": "정말 멋지네요! 더 이야기해 주세요.",
            }
        else:
            user_eng = make_easy_english(user_text)
            ai_eng = make_english_answer(user_eng)
            return {
                "user_eng": user_eng,
                "ai_eng": ai_eng,
                "ai_kor": "해석을 준비하지 못했습니다.",
            }


# =========================================================
# 8-2. 종료 명령 감지 함수
# =========================================================
STOP_COMMANDS = ["종료하자", "대화 그만", "그만하자", "대화 종료", "그만", "종료", "끝내자", "그만할래"]

def is_stop_command(text):
    if not text:
        return False
    cleaned = "".join(text.split()).replace(".", "").replace("!", "").replace("?", "").replace("~", "")
    for cmd in STOP_COMMANDS:
        clean_cmd = "".join(cmd.split())
        if clean_cmd in cleaned:
            return True
    return False


# =========================================================
# 세션 상태 초기화
# =========================================================
if "continuous_history" not in st.session_state:
    st.session_state.continuous_history = []
if "latest_user_eng" not in st.session_state:
    st.session_state.latest_user_eng = ""
if "latest_ai_eng" not in st.session_state:
    st.session_state.latest_ai_eng = ""

if "latest_ai_kor" not in st.session_state:
    st.session_state.latest_ai_kor = ""

if "latest_turn_id" not in st.session_state:
    st.session_state.latest_turn_id = 0
if "last_processed_timestamp" not in st.session_state:
    st.session_state.last_processed_timestamp = 0
if "force_stop" not in st.session_state:
    st.session_state.force_stop = False
if "korean_text" not in st.session_state:
    st.session_state.korean_text = ""
if "direct_input_text" not in st.session_state:
    st.session_state.direct_input_text = ""
if "auto_listen_flag" not in st.session_state:
    st.session_state.auto_listen_flag = True


# =========================================================
# 9. 화면 모드 탭 (연속 대화 vs 문장별 연습)
# =========================================================
tab_continuous, tab_practice = st.tabs(["🎧 실전 연속 대화", "📝 문장별 표현 연습"])


# ---------------------------------------------------------
# [탭 1] 실전 대화 (🎤 말하기 & ⌨️ 직접 입력 지원)
# ---------------------------------------------------------
with tab_continuous:
    st.markdown(
        '<div class="section-title">🎙️ 실전 대화</div>',
        unsafe_allow_html=True,
    )

    top_c1, top_c2 = st.columns([3, 1])
    with top_c1:
        input_mode = st.radio(
            "입력 방식 선택",
            ["🎤 실시간 연속 음성 대화 (자동 순환)", "⌨️ 직접 텍스트 입력 / 음성인식 수정"],
            horizontal=True,
            key="continuous_input_mode_radio"
        )
    with top_c2:
        st.write("")
        if st.button("🗑️ 대화 기록 초기화", use_container_width=True, key="btn_reset_chat"):
            st.session_state.continuous_history = []
            st.session_state.latest_user_eng = ""
            st.session_state.latest_ai_eng = ""
            st.session_state.latest_turn_id = 0
            st.session_state.last_processed_timestamp = 0
            st.session_state.direct_input_text = ""
            st.session_state.force_stop = False
            st.rerun()

    # 오디오 재생 및 실시간 음성 컴포넌트 렌더링
    comp_result = continuous_chat_component(
        user_eng=st.session_state.get("latest_user_eng", ""),
        ai_eng=st.session_state.get("latest_ai_eng", ""),
        ai_kor=st.session_state.get("latest_ai_kor", ""),
        turn_id=st.session_state.get("latest_turn_id", 0),
        auto_listen=st.session_state.get("auto_listen_flag", True),
        force_stop=st.session_state.get("force_stop", False),
        key="continuous_chat_widget",
    )

    # -----------------------------------------------------
    # 1. 🎤 실시간 연속 음성 대화 모드
    # -----------------------------------------------------
    if "실시간 연속 음성 대화" in input_mode:
        st.markdown(
            '<div style="font-size: 15px; font-weight: 800; color: #5B4216; margin-bottom: 12px;">'
            '💬 한국어로 말하면 내 영어 표현과 AI 답변을 즉시 차례대로 들려드려요.<br>'
            '<span style="color: #A04000; font-size: 13px;">💡 대화를 끝내고 싶을 때는 <b>"종료하자"</b> 또는 <b>"대화 그만"</b>이라고 말씀하세요.</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        if comp_result and isinstance(comp_result, dict):
            action = comp_result.get("action")
            if action == "user_spoken":
                user_korean = comp_result.get("text", "").strip()
                timestamp = comp_result.get("timestamp", 0)

                if user_korean and timestamp != st.session_state.last_processed_timestamp:
                    st.session_state.last_processed_timestamp = timestamp

                    # 종료 명령 감지
                    if is_stop_command(user_korean):
                        st.session_state.force_stop = True
                        st.info("⏹️ '종료' 명령을 인식하여 대화를 종료했습니다.")
                        st.rerun()

                    st.session_state.force_stop = False

                    try:
                        with st.spinner("⚡ 영어 표현과 AI 답변을 준비하고 있어요..."):
                            turn_data = ask_continuous_turn(
                                user_korean,
                                input_lang="ko",
                                conversation_history=st.session_state.continuous_history,
                            )
                            u_eng = turn_data["user_eng"]
                            a_eng = turn_data["ai_eng"]
                            a_kor = turn_data["ai_kor"]

                        st.session_state.continuous_history.append({
                            "user_orig": user_korean,
                            "user_lang": "ko",
                            "user_eng": u_eng,
                            "ai_eng": a_eng,
                            "ai_kor": a_kor,
                        })

                        # 브라우저 컴포넌트로 전달 -> 브라우저 speechSynthesis로 즉시 발음 & 다음 턴 마이크 켜기!
                        st.session_state.latest_user_eng = u_eng
                        st.session_state.latest_ai_eng = a_eng
                        st.session_state.latest_ai_kor = a_kor
                        st.session_state.latest_turn_id = timestamp
                        st.session_state.auto_listen_flag = True
                        st.rerun()

                    except RateLimitError:
                        st.error("OpenAI API 잔액 또는 사용 한도를 확인해 주세요.")
                    except AuthenticationError:
                        st.error("OpenAI API 키가 올바른지 확인해 주세요.")
                    except APIConnectionError:
                        st.error("OpenAI 서버에 연결할 수 없습니다. 인터넷 연결을 확인해 주세요.")
                    except APITimeoutError:
                        st.error("AI 응답 시간이 오래 걸리고 있습니다. 잠시 후 다시 시도해 주세요.")
                    except Exception as e:
                        st.error(f"대화 처리 중 오류가 발생했습니다: {e}")

    # -----------------------------------------------------
    # 2. ⌨️ 직접 텍스트 입력 / 음성인식 수정 모드
    # -----------------------------------------------------
    else:
        st.markdown(
            '<div style="font-size: 15px; font-weight: 800; color: #5B4216; margin-bottom: 8px;">'
            '💬 직접 타이핑하거나, 마이크로 말한 뒤 문장을 원하는 대로 수정해서 전송해 보세요.'
            '</div>',
            unsafe_allow_html=True,
        )

        lang_select_col, mic_col = st.columns([2, 2])
        with lang_select_col:
            direct_lang = st.radio(
                "입력 언어 선택",
                ["🇰🇷 한글 입력", "🇺🇸 English 입력"],
                horizontal=True,
                key="direct_input_lang_choice",
            )
            is_en_input = "English" in direct_lang

        with mic_col:
            st.write("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            stt_lang = "en" if is_en_input else "ko"
            stt_btn_text = "🎤 영어로 말하고 텍스트 채우기" if is_en_input else "🎤 한국어로 말하고 텍스트 채우기"
            voice_stt = speech_to_text(
                language=stt_lang,
                start_prompt=stt_btn_text,
                stop_prompt="⏹️ 말하기 완료",
                just_once=True,
                use_container_width=True,
                key="direct_speech_to_text_widget",
            )
            if voice_stt:
                st.session_state.direct_input_text = voice_stt

        placeholder_msg = "예: I go to school yesterday. (자연스러운 문장으로 다듬어 드립니다)" if is_en_input else "예: 오늘 회사 끝나고 친구랑 맛있는 파스타 먹었어."
        send_btn_label = "✨ 다듬은 영어 & AI 대답 듣기" if is_en_input else "✨ 쉬운 영어로 바꾸고 AI 대답 듣기"

        with st.form(key="direct_input_form", clear_on_submit=True):
            direct_text = st.text_area(
                "내용 직접 입력 또는 수정",
                value=st.session_state.direct_input_text,
                placeholder=placeholder_msg,
                height=95,
                key="direct_text_area_form_input",
            )
            form_col1, form_col2 = st.columns([3, 1])
            with form_col1:
                submitted = st.form_submit_button(send_btn_label, use_container_width=True)
            with form_col2:
                clear_btn = st.form_submit_button("내용 지우기", use_container_width=True)

        if clear_btn:
            st.session_state.direct_input_text = ""
            st.rerun()

        if submitted:
            if not direct_text.strip():
                st.warning("먼저 내용을 입력하거나 마이크로 말씀해 주세요.")
            else:
                try:
                    with st.spinner("⚡ 영어 표현과 AI 답변을 준비하고 있어요..."):
                        turn_data = ask_continuous_turn(
                            direct_text.strip(),
                            input_lang="en" if is_en_input else "ko",
                            conversation_history=st.session_state.continuous_history,
                        )
                        u_eng = turn_data["user_eng"]
                        a_eng = turn_data["ai_eng"]
                        a_kor = turn_data["ai_kor"]

                    st.session_state.continuous_history.append({
                        "user_orig": direct_text.strip(),
                        "user_lang": "en" if is_en_input else "ko",
                        "user_eng": u_eng,
                        "ai_eng": a_eng,
                        "ai_kor": a_kor,
                    })

                    # 브라우저 컴포넌트로 소리 재생 (마이크는 자동 켜기 안 함)
                    st.session_state.latest_user_eng = u_eng
                    st.session_state.latest_ai_eng = a_eng
                    st.session_state.latest_turn_id = time.time()
                    st.session_state.auto_listen_flag = False
                    st.session_state.direct_input_text = ""
                    st.rerun()

                except RateLimitError:
                    st.error("OpenAI API 잔액 또는 사용 한도를 확인해 주세요.")
                except AuthenticationError:
                    st.error("OpenAI API 키가 올바른지 확인해 주세요.")
                except APIConnectionError:
                    st.error("OpenAI 서버에 연결할 수 없습니다. 인터넷 연결을 확인해 주세요.")
                except APITimeoutError:
                    st.error("AI 응답 시간이 오래 걸리고 있습니다. 잠시 후 다시 시도해 주세요.")
                except Exception as e:
                    st.error(f"대화 처리 중 오류가 발생했습니다: {e}")

    # -----------------------------------------------------
    # 대화 학습 기록 표시 (최신 대화가 위로)
    # -----------------------------------------------------
    if st.session_state.continuous_history:
        st.markdown('<div class="result-title" style="margin-top: 32px;">💬 실시간 대화 학습 내역</div>', unsafe_allow_html=True)
        for turn in reversed(st.session_state.continuous_history):
            safe_orig = html.escape(turn.get("user_orig", turn.get("user_kor", "")))
            safe_u_eng = html.escape(turn["user_eng"])
            safe_a_eng = html.escape(turn["ai_eng"])
            safe_a_kor = html.escape(turn["ai_kor"])
            is_english_user = turn.get("user_lang") == "en"

            badge_title = "✨ 자연스럽게 다듬은 영어 문장" if is_english_user else "🔤 이렇게 영어로 말해요"
            orig_title = f'🇺🇸 내가 쓴 영어: "{safe_orig}"' if is_english_user else f'🇰🇷 내가 한 말: "{safe_orig}"'

            # 1. 내 영어 표현 카드
            st.markdown(
                f"""
                <div class="chat-bubble-card card-my-turn">
                    <div class="chat-my-kor">{orig_title}</div>
                    <div class="chat-badge badge-user" style="font-size: 15px; margin-bottom: 8px;">{badge_title}</div>
                    <div class="chat-my-eng">{safe_u_eng}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # 2. AI의 영어 답변 카드
            st.markdown(
                f"""
                <div class="chat-bubble-card card-ai-turn">
                    <div class="chat-badge badge-ai" style="font-size: 15px; margin-bottom: 8px;">🤖 Life Talk AI 답변</div>
                    <div class="chat-ai-eng-title">{safe_a_eng}</div>
                    <div class="chat-ai-kor-desc">💡 {safe_a_kor}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<hr style='margin: 22px 0; border: none; border-top: 1px dashed #E0D7C5;'>", unsafe_allow_html=True)


# ---------------------------------------------------------
# [탭 2] 문장별 표현 연습 (기존 기능 100% 보존)
# ---------------------------------------------------------
with tab_practice:
    st.markdown(
        '<div class="section-title">🎙️ 한국어로 말해 보세요</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="mic-guide">마이크 버튼을 누르고 편하게 이야기 하세요.</div>',
        unsafe_allow_html=True,
    )

    voice_text = pretty_speech_to_text(language="ko", key="KOREAN_STT")

    st.markdown(
        '<div class="mic-bottom"></div>',
        unsafe_allow_html=True,
    )

    if voice_text:
        st.session_state.korean_text = voice_text

    korean_text = st.text_area(
        "말한 내용",
        value=st.session_state.korean_text,
        placeholder="예: 오늘 회사에서 회의가 있어서 조금 늦게 퇴근했어.",
        height=125,
        key="practice_korean_text_area",
    )

    st.write("")

    if st.button(
        "✨ 영어로 바꾸고 대화하기",
        use_container_width=True,
        key="btn_practice_convert",
    ):
        if not korean_text.strip():
            st.warning("먼저 한국어로 말하거나 문장을 입력해 주세요.")
        else:
            try:
                with st.spinner("영어 문장을 만들고 있어요..."):
                    english_sentence = make_easy_english(korean_text)

                with st.spinner("영어 대답을 만들고 있어요..."):
                    ai_answer = make_english_answer(english_sentence)

                st.session_state.english_sentence = english_sentence
                st.session_state.ai_answer = ai_answer

            except RateLimitError:
                st.error("OpenAI API 잔액 또는 사용 한도를 확인해 주세요.")
            except AuthenticationError:
                st.error("OpenAI API 키가 올바른지 확인해 주세요.")
            except APIConnectionError:
                st.error("OpenAI 서버에 연결할 수 없습니다. 인터넷 연결을 확인해 주세요.")
            except APITimeoutError:
                st.error("AI 응답 시간이 너무 오래 걸리고 있습니다. 잠시 후 다시 시도해 주세요.")
            except Exception as e:
                st.error(f"처리 중 문제가 발생했습니다: {e}")

    if "english_sentence" in st.session_state:
        english_sentence = st.session_state.english_sentence
        safe_english = html.escape(english_sentence)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            '<div class="result-title">💬 이렇게 영어로 말해 보세요</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="result-card english-card">{safe_english}</div>',
            unsafe_allow_html=True,
        )

        try:
            english_audio = make_audio(english_sentence)
            st.audio(english_audio, format="audio/mp3")
        except Exception as e:
            st.warning(f"영어 음성을 만들 수 없습니다: {e}")

        ai_answer = st.session_state.ai_answer
        safe_answer = html.escape(ai_answer)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            '<div class="result-title">😊 영어 대답</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="result-card answer-card">🤖 &nbsp;{safe_answer}</div>',
            unsafe_allow_html=True,
        )

        try:
            answer_audio = make_audio(ai_answer)
            st.audio(answer_audio, format="audio/mp3")
        except Exception as e:
            st.warning(f"영어 대답 음성을 만들 수 없습니다: {e}")


# =========================================================
# 14. 하단
# =========================================================
st.markdown(
    """
    <div class="footer-note">
        🎤 Life Talk &nbsp;·&nbsp; Enjoy your English conversation
    </div>
    """,
    unsafe_allow_html=True,
)
