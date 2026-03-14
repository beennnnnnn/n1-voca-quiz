import streamlit as st
import pandas as pd
import random

# 1. 앱 설정 및 귀여운 폰트/디자인 적용
st.set_page_config(page_title="N1 단어 박살내기", page_icon="⭐", layout="centered")

# --- 커스텀 CSS (귀여운 테마) ---
st.markdown("""
    <style>
    /* 전체 배경색 */
    .stApp {
        background-color: #FFF9F2;
    }
    /* 카드 디자인 */
    .word-card {
        background-color: #FFFFFF;
        padding: 40px;
        border-radius: 25px;
        box-shadow: 0 10px 25px rgba(255, 154, 158, 0.2);
        text-align: center;
        margin-bottom: 20px;
        border: 3px solid #FFD1D1;
    }
    /* 단어 폰트 */
    .japanese-word {
        font-size: 85px !important;
        color: #FF6B6B;
        font-weight: bold;
        margin-bottom: 10px;
    }
    /* 버튼 스타일 커스텀 */
    div.stButton > button {
        border-radius: 15px;
        height: 3em;
        font-weight: bold;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        border-color: #FF6B6B;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (URL을 본인의 구글 시트 주소로 꼭 바꿔주세요!)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1g6ww8VWi7PytD5oH6iGMcUfGc0P-0uGeC4CKGEEGbU0/export?format=csv"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except:
        st.error("앗! 시트 연결에 문제가 생겼어요 😭")
        st.stop()

# 데이터 초기화
if 'vocab_data' not in st.session_state:
    st.session_state.vocab_data = load_data(SHEET_URL)

if 'current_idx' not in st.session_state:
    if not st.session_state.vocab_data.empty:
        st.session_state.current_idx = random.randint(0, len(st.session_state.vocab_data) - 1)
    st.session_state.show_answer = False

def next_word():
    st.session_state.current_idx = random.randint(0, len(st.session_state.vocab_data) - 1)
    st.session_state.show_answer = False

# 3. 메인 UI 구성
st.markdown("<h3 style='text-align: center; color: #FF8E8E;'>✨ 합격을 부르는 마법 단어장 ✨</h3>", unsafe_allow_html=True)

if not st.session_state.vocab_data.empty:
    current_word = st.session_state.vocab_data.iloc[st.session_state.current_idx]

    # --- 단어 카드 섹션 ---
    st.markdown(f"""
        <div class='word-card'>
            <p style='color: #FFA4A4; font-size: 18px; margin-bottom: 0;'>이 단어는 뭘까요? 🤔</p>
            <div class='japanese-word'>{current_word['단어']}</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.show_answer:
        if st.button("💝 정답 확인하기", use_container_width=True):
            st.session_state.show_answer = True
            st.rerun()
    else:
        # --- 정답 노출 섹션 (귀여운 박스 형태) ---
        st.markdown(f"""
            <div style='background-color: #F0FFF0; padding: 20px; border-radius: 15px; border-left: 10px solid #77DD77; margin-bottom: 10px;'>
                <p style='margin:0; font-size:14px; color: #666;'>히라가나</p>
                <h2 style='margin:0; color: #2D5A27;'>{current_word['히라가나']}</h2>
            </div>
            <div style='background-color: #FFF5E6; padding: 20px; border-radius: 15px; border-left: 10px solid #FFB347; margin-bottom: 10px;'>
                <p style='margin:0; font-size:14px; color: #666;'>한국어 발음</p>
                <h2 style='margin:0; color: #A0522D;'>{current_word['한국어발음']}</h2>
            </div>
            <div style='background-color: #E6F3FF; padding: 20px; border-radius: 15px; border-left: 10px solid #779ECB; margin-bottom: 20px;'>
                <p style='margin:0; font-size:14px; color: #666;'>뜻</p>
                <h2 style='margin:0; color: #1F3A5F;'>{current_word['뜻']}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌈 완벽해! 다음으로", use_container_width=True):
                next_word()
                st.rerun()
        with col2:
            if st.button("🐥 다시 한 번 볼래", type="primary", use_container_width=True):
                next_word()
                st.rerun()
else:
    st.warning("시트에 공부할 단어를 채워주세요! 📝")
