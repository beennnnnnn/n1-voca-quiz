import streamlit as st
import pandas as pd
import random

# 1. 앱 기본 설정
st.set_page_config(page_title="세법 & N1 단어장", page_icon="🔥")
st.title("🔥 나만의 세법 & N1 단어 박살내기")

# ---------------------------------------------------------
# 🚨 [중요] 여기에 본인의 구글 시트 URL을 넣으세요!
# 반드시 링크 끝부분이 export?format=csv 로 끝나야 합니다.
# ---------------------------------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1g6ww8VWi7PytD5oH6iGMcUfGc0P-0uGeC4CKGEEGbU0/export?format=csv"

# 2. 구글 시트 데이터 로드 (캐싱을 통해 속도 향상)
@st.cache_data(ttl=60) # 60초마다 구글 시트 최신화 (단어 추가 후 1분 뒤 반영됨)
def load_data(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error("구글 시트를 불러오지 못했습니다. URL과 공유 설정을 다시 확인해 주세요!")
        st.stop()

# 3. 데이터 및 상태 초기화
if 'vocab_data' not in st.session_state:
    st.session_state.vocab_data = load_data(SHEET_URL)

if 'current_idx' not in st.session_state:
    # 데이터가 정상적으로 로드되었을 때만 인덱스 설정
    if not st.session_state.vocab_data.empty:
        st.session_state.current_idx = random.randint(0, len(st.session_state.vocab_data) - 1)
    st.session_state.show_answer = False

# 4. 다음 단어로 넘어가는 함수
def next_word():
    st.session_state.current_idx = random.randint(0, len(st.session_state.vocab_data) - 1)
    st.session_state.show_answer = False

# 5. 메인 화면 UI (단어 표시)
if not st.session_state.vocab_data.empty:
    current_word = st.session_state.vocab_data.iloc[st.session_state.current_idx]

    # 한자를 아주 크게 화면 중앙에 표시
    st.markdown(f"<h1 style='text-align: center; font-size: 100px;'>{current_word['한자']}</h1>", unsafe_allow_html=True)
    st.write("---")

    # 6. 정답 확인 및 채점 버튼
    if not st.session_state.show_answer:
        # 정답 보기 버튼 (클릭 시 세션 상태를 True로 변경하고 새로고침)
        if st.button("👀 정답 보기", use_container_width=True):
            st.session_state.show_answer = True
            st.rerun()
    else:
        # 정답을 펼쳤을 때 나오는 화면
        st.success(f"**🗣️ 발음:** {current_word['발음']}")
        st.info(f"**💡 뜻:** {current_word['뜻']}")
        
        # 맞혔는지 틀렸는지 선택하는 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⭕ 완벽히 외웠다! (다음)", use_container_width=True):
                next_word()
                st.rerun()
        with col2:
            if st.button("❌ 아차! (다시 외우기)", type="primary", use_container_width=True):
                # 나중에 이 부분에 틀린 단어만 구글 시트의 다른 탭으로 보내는 기능을 추가할 수 있습니다!
                next_word()
                st.rerun()
else:
    st.warning("단어장에 단어가 없습니다. 구글 시트에 단어를 추가해 주세요!")
