import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import requests
import tempfile
import html
import base64
import os
from speech_recognition import Recognizer, AudioData
import streamlit.components.v1 as components


VOICE_RECORDER = components.declare_component(
    "life_talk_voice_recorder",
    path=os.path.join(os.path.dirname(__file__), "components", "voice_recorder"),
)


def pretty_speech_to_text(language="ko", key=None):
    """Record browser audio with the custom button, then transcribe it."""
    recording = VOICE_RECORDER(key=key, default=None)
    if not recording:
        return None

    recording_id = recording.get("id")
    last_id_key = f"_{key}_transcript_id"
    if st.session_state.get(last_id_key) == recording_id:
        return None

    st.session_state[last_id_key] = recording_id
    audio = AudioData(
        base64.b64decode(recording["audio_base64"]),
        recording["sample_rate"],
        recording["sample_width"],
    )
    try:
        return Recognizer().recognize_google(audio, language=language)
    except Exception:
        return None


# =========================================================
# 1. Streamlit 기본 설정
# =========================================================
st.set_page_config(
    page_title="Life Talk",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# 2. 전체 디자인
# =========================================================
st.markdown(
    """
    <style>

    /* 전체 배경 */
    .stApp {
        background:
            linear-gradient(
                180deg,
                #FFF8D8 0%,
                #FFFDF1 50%,
                #FFF7CF 100%
            );
    }

    /* 본문 폭 */
    .block-container {
        max-width: 900px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }

    /* 기본 폰트 */
    html, body, [class*="css"] {
        font-family: "Malgun Gothic", "Arial", sans-serif;
    }

    /* 일반 문장 */
    p {
        font-size: 20px !important;
        line-height: 1.75 !important;
    }

    /* 입력 라벨 */
    label {
        font-size: 20px !important;
        font-weight: 800 !important;
        color: #47391F !important;
    }

    /* 텍스트 입력창 */
    textarea {
        font-size: 21px !important;
        line-height: 1.65 !important;
        border-radius: 18px !important;
        padding: 16px !important;
        background-color: #FFFDF8 !important;
        border: 1px solid #E8DEC8 !important;
    }

    /* 일반 Streamlit 버튼 */
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

        box-shadow:
            0 5px 14px rgba(120, 100, 40, 0.12);

        transition: 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        color: white !important;
        border: none;
    }

    /* 오디오 */
    audio {
        width: 100%;
        margin-top: 8px;
    }

    /* 구분선 */
    hr {
        margin-top: 28px;
        margin-bottom: 28px;
    }

    /* Streamlit 메뉴 숨김 */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 3. 상단 HERO
# =========================================================
st.markdown(
    '<div style="'
    'background:linear-gradient(135deg,#FFF0A6,#FFFBE7);'
    'border:1px solid #F1D36D;'
    'border-radius:30px;'
    'padding:38px 28px;'
    'text-align:center;'
    'margin-bottom:38px;'
    'box-shadow:0 8px 22px rgba(120,100,40,0.08);'
    '">'
    '<div style="font-size:62px;margin-bottom:6px;">🎤 💬 🎧</div>'
    '<div style="font-size:46px;font-weight:900;color:#183852;">'
    'Life Talk'
    '</div>'
    '<div style="font-size:23px;font-weight:900;color:#3482A1;'
    'margin-top:8px;">'
    'Speak Korean. Practice English.'
    '</div>'
    '<div style="font-size:23px;font-weight:800;color:#6B4A18;'
    'margin-top:16px;">'
    '한국어로 편하게 말하고 영어로 대화해 보세요.'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


#======================================
# --------------------------------------------------
# OpenAI 설정
# --------------------------------------------------

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# --------------------------------------------------
# OpenAI 호출
# --------------------------------------------------

def ask_ollama(prompt):

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
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

    return ask_ollama(prompt)


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

    return ask_ollama(prompt)


# =========================================================
# 8. 영어 음성
# =========================================================
def make_audio(text):

    tts = gTTS(
        text=text,
        lang="en",
        slow=True
    )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    ) as fp:
        audio_path = fp.name

    tts.save(audio_path)

    with open(audio_path, "rb") as audio_file:
        return audio_file.read()


# =========================================================
# 9. 한국어 말하기 제목
# =========================================================
st.markdown(
    '<div style="'
    'font-size:31px;'
    'font-weight:900;'
    'color:#263B45;'
    'margin-bottom:8px;'
    '">'
    '🎙️ 한국어로 말해 보세요'
    '</div>',
    unsafe_allow_html=True
)




# =========================================================
# 10. 말하기 안내 영역
# =========================================================
st.markdown(
    '<div style="'
    'background:linear-gradient(90deg,#FFF2B5,#FFE89A);'
    'border:2px solid #F1C34A;'
    'border-radius:24px 24px 0 0;'
    'padding:24px 20px 18px 20px;'
    'text-align:center;'
    'font-size:24px;'
    'font-weight:900;'
    'color:#5B4216;'
    '">'
    '마이크 버튼을 누르고 편하게 이야기 하세요.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 11. 실제 마이크 버튼
# =========================================================
voice_text = pretty_speech_to_text(language="ko", key="KOREAN_STT")


# =========================================================
# 11-1. 마이크 영역 아래쪽 마감
# =========================================================
st.markdown(
    '<div style="'
    'height:10px;'
    'background:linear-gradient(90deg,#FFF2B5,#FFE89A);'
    'border-left:2px solid #F1C34A;'
    'border-right:2px solid #F1C34A;'
    'border-bottom:2px solid #F1C34A;'
    'border-radius:0 0 24px 24px;'
    'margin-top:-10px;'
    'margin-bottom:24px;'
    '">'
    '</div>',
    unsafe_allow_html=True
)



# =========================================================
# 12. 음성인식 결과 저장
# =========================================================
if voice_text:
    st.session_state.korean_text = voice_text

if "korean_text" not in st.session_state:
    st.session_state.korean_text = ""


# =========================================================
# 13. 말한 내용
# =========================================================
korean_text = st.text_area(
    "말한 내용",
    value=st.session_state.korean_text,
    placeholder="예: 오늘 회사에서 회의가 있어서 조금 늦게 퇴근했어.",
    height=125
)


st.write("")


# =========================================================
# 14. 영어 변환 버튼
# =========================================================
if st.button(
    "✨ 영어로 바꾸고 대화하기",
    use_container_width=True
):

    if not korean_text.strip():

        st.warning(
            "먼저 한국어로 말하거나 문장을 입력해 주세요."
        )

    else:

        try:

            with st.spinner(
                "영어 문장을 만들고 있어요..."
            ):

                english_sentence = make_easy_english(
                    korean_text
                )

            with st.spinner(
                "영어 대답을 만들고 있어요..."
            ):

                ai_answer = make_english_answer(
                    english_sentence
                )

            st.session_state.english_sentence = (
                english_sentence
            )

            st.session_state.ai_answer = (
                ai_answer
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "Ollama에 연결할 수 없습니다. "
                "Ollama가 실행 중인지 확인해 주세요."
            )

        except requests.exceptions.Timeout:

            st.error(
                "AI가 답변을 만드는 데 시간이 너무 오래 걸리고 있습니다."
            )

        except Exception as e:

            st.error(
                f"처리 중 문제가 발생했습니다: {e}"
            )


# =========================================================
# 15. 영어 문장 결과
# =========================================================
if "english_sentence" in st.session_state:

    english_sentence = (
        st.session_state.english_sentence
    )

    safe_english = html.escape(
        english_sentence
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div style="'
        'font-size:30px;'
        'font-weight:900;'
        'color:#243B45;'
        'margin-bottom:15px;'
        '">'
        '💬 이렇게 영어로 말해 보세요'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
    '<div style="'
    'background:linear-gradient(135deg,#E9FFF4,#F6FFF9);'
    'border:1px solid #C4EBD8;'
    'border-radius:23px;'
    'padding:27px;'
    'margin-bottom:15px;'
    'font-size:24px;'
    'font-weight:900;'
    'line-height:1.6;'
    'color:#17664B;'
    '">'
    + safe_english +
    '</div>',
    unsafe_allow_html=True
)

    try:

        english_audio = make_audio(
            english_sentence
        )

        st.audio(
            english_audio,
            format="audio/mp3"
        )

    except Exception as e:

        st.warning(
            f"영어 음성을 만들 수 없습니다: {e}"
        )


    # =====================================================
    # 16. 영어 대답
    # =====================================================
    ai_answer = (
        st.session_state.ai_answer
    )

    safe_answer = html.escape(
        ai_answer
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div style="'
        'font-size:30px;'
        'font-weight:900;'
        'color:#243B45;'
        'margin-bottom:15px;'
        '">'
        '😊 영어 대답'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div style="'
        'background:linear-gradient(135deg,#EAF4FF,#F7FBFF);'
        'border:1px solid #CBE1F5;'
        'border-radius:23px;'
        'padding:27px;'
        'margin-bottom:15px;'
        'font-size:24px;'
        'font-weight:900;'
        'line-height:1.6;'
        'color:#285D87;'
        '">'
        '🤖 &nbsp;' + safe_answer +
        '</div>',
        unsafe_allow_html=True
    )

    try:

        answer_audio = make_audio(
            ai_answer
        )

        st.audio(
            answer_audio,
            format="audio/mp3"
        )

    except Exception as e:

        st.warning(
            f"영어 대답 음성을 만들 수 없습니다: {e}"
        )


# =========================================================
# 17. 하단
# =========================================================
st.markdown(
    '<div style="'
    'text-align:center;'
    'color:#92A3A8;'
    'font-size:15px;'
    'margin-top:55px;'
    'padding-top:20px;'
    '">'
    '🎤 Life Talk &nbsp;·&nbsp; Enjoy your English conversation'
    '</div>',
    unsafe_allow_html=True
)
