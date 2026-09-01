import streamlit as st
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError, APITimeoutError
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import tempfile
import html


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
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. 마이크 음성인식
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
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("OPENAI_API_KEY가 설정되어 있지 않습니다. Streamlit Secrets를 확인해 주세요.")
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
# 9. 한국어 말하기
# =========================================================
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


# =========================================================
# 10. 음성인식 결과 저장
# =========================================================
if voice_text:
    st.session_state.korean_text = voice_text

if "korean_text" not in st.session_state:
    st.session_state.korean_text = ""


# =========================================================
# 11. 말한 내용
# =========================================================
korean_text = st.text_area(
    "말한 내용",
    value=st.session_state.korean_text,
    placeholder="예: 오늘 회사에서 회의가 있어서 조금 늦게 퇴근했어.",
    height=125,
)

st.write("")


# =========================================================
# 12. 영어 변환 버튼
# =========================================================
if st.button(
    "✨ 영어로 바꾸고 대화하기",
    use_container_width=True,
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


# =========================================================
# 13. 영어 문장 결과
# =========================================================
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
