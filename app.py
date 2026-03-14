import streamlit as st
import pandas as pd
import random

# 1. 앱 기본 설정
st.set_page_config(page_title="세법 & N1 단어장", page_icon="🔥")
st.title("🔥 나만의 세법 & N1 단어 박살내기")

# ---------------------------------------------------------
# 본인의 구글 시트 URL을 확인하세요! (캡처해주신 시트 기준)
# ---------------------------------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1g6ww8VWi7PytD5oH6iGMcUfGc0P-0uGeC4CKGEEGbU0/export?format=csv"

# 2. 구글 시트 데이터 로드
@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        # 열 이름 앞뒤 공백 제거 (이미지상의 '단어', '히라가나' 등에 대응)
        df.columns = df.columns.str.strip() 
        return df
    except Exception as e:
        st.error("구글 시트를 불러오지 못했습니다. URL 공유 설정을 확인해주세요.")
        st.stop()

# 3. 데이터 로드
if 'vocab_data' not in st.session_state:
    st.session_state.vocab_data = load_data(SHEET_URL)

# 4. 상태 초기화
if 'current_idx' not in st.session_state:
    if not st.session_state.vocab_data.empty:
        st.session_state.current_idx = random.randint(0, len(st.session_state.vocab_data) - 1)
    st.session_state.show_answer = False

def next_word():
    st.session_state.current_idx = random.randint(0, len(st.session_state.vocab_data) - 1)
    st.session_state.show_answer = False

# 5. 메인 UI (시트의 헤더 명칭인 '단어', '히라가나', '뜻' 사용)
if not st.session_state.vocab_data.empty:
    current_word = st.session_state.vocab_data.iloc[st.session_state.current_idx]

    # 큰 글씨로 문제(단어) 표시
    st.markdown(f"<h1 style='text-align: center; font-size: 100px;'>{current_word['단어']}</h1>", unsafe_allow_html=True)
    st.write("---")

    if not st.session_state.show_answer:
        if st.button("👀 정답 보기", use_container_width=True):
            st.session_state.show_answer = True
            st.rerun()
    else:
        # 시트의 '히라가나'와 '뜻' 열을 출력
        st.success(f"**🗣️ 발음:** {current_word['히라가나']}")
        st.info(f"**💡 뜻:** {current_word['뜻']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⭕ 외웠다!", use_container_width=True):
                next_word()
                st.rerun()
        with col2:
            if st.button("❌ 다시!", type="primary", use_container_width=True):
                next_word()
                st.rerun()
else:
    st.warning("시트에 데이터가 없습니다.")
