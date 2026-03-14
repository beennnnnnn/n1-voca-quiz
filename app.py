import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime
from supabase import create_client, Client

# 1. 앱 설정 및 디자인
st.set_page_config(page_title="N1 합격 챌린지", page_icon="🌸", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #FFF9F2; }
    .word-card {
        background-color: #FFFFFF; padding: 40px; border-radius: 25px;
        box-shadow: 0 10px 25px rgba(255, 154, 158, 0.2);
        text-align: center; margin-bottom: 20px; border: 3px solid #FFD1D1;
    }
    .japanese-word { font-size: 80px !important; color: #FF6B6B; font-weight: bold; }
    .timer-box { background-color: #FFEEBB; padding: 10px; border-radius: 12px; text-align: center; font-weight: bold; color: #B8860B; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# 2. 서비스 연결 (Secrets)
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    SHEET_URL = st.secrets["SHEET_URL"]
except Exception as e:
    st.error("⚠️ Streamlit Secrets 설정을 확인해주세요!")
    st.stop()

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# 3. 데이터 로드 함수
@st.cache_data(ttl=60)
def load_vocab():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame(columns=['단어', '히라가나', '한국어발음', '뜻'])

# --- 4. 로그인 처리 핵심 로직 (매우 중요 ⭐) ---

# URL에 포함된 로그인 열쇠(code)를 세션으로 교환합니다.
if "code" in st.query_params:
    try:
        auth_code = st.query_params.get("code")
        supabase.auth.exchange_code_for_session({"auth_code": auth_code})
        # 처리가 끝나면 주소창을 비우고 앱을 새로고침합니다.
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        # 이미 처리된 코드일 경우 에러가 날 수 있으므로 무시하거나 로그아웃 처리
        st.query_params.clear()
        st.rerun()

def get_user():
    try:
        res = supabase.auth.get_session()
        return res.user if res else None
    except:
        return None

# 세션 상태 초기화
if 'vocab_data' not in st.session_state: st.session_state.vocab_data = load_vocab()
if 'mastered_words' not in st.session_state: st.session_state.mastered_words = []
if 'total_seconds' not in st.session_state: st.session_state.total_seconds = 0
if 'start_time' not in st.session_state: st.session_state.start_time = time.time()
if 'show_answer' not in st.session_state: st.session_state.show_answer = False

user = get_user()

if len(st.session_state.vocab_data) > 0:
    if 'current_idx' not in st.session_state:
        st.session_state.current_idx = random.randint(0, len(st.session_state.vocab_data)-1)

# --- 5. 사이드바 (로그인 관리) ---
with st.sidebar:
    if not user:
        st.header("🔐 로그인")
        
        # ⭐ [수정 필요] 본인의 실제 스트림릿 앱 주소를 입력하세요.
        MY_APP_URL = "https://n1-voca-quiz-3uapphy3u4brvdpfsgl5snw.streamlit.app" 
        
        # 보안 키 불일치(code challenge) 방지를 위해 URL을 세션에 고정
        if 'google_login_url' not in st.session_state:
            res = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {"redirect_to": MY_APP_URL}
            })
            st.session_state.google_login_url = res.url
            
        st.link_button("🚀 구글 로그인 시작하기", st.session_state.google_login_url, use_container_width=True)
        st.info("로그인 후 자동으로 단어장이 나타납니다.")
    else:
        st.header(f"👋 {user.email.split('@')[0]}님")
        
        # Supabase 데이터 동기화
        try:
            res = supabase.table("study_progress").select("*").eq("username", user.email).execute()
            if res.data:
                st.session_state.mastered_words = res.data[0].get('mastered_words', [])
                st.session_state.total_seconds = res.data[0].get('total_seconds', 0)
        except: pass

        if st.button("로그아웃"):
            supabase.auth.sign_out()
            if 'google_login_url' in st.session_state: del st.session_state.google_login_url
            st.rerun()

        st.write("---")
        if st.checkbox("🏆 공부왕 랭킹 보기"):
            try:
                rank_res = supabase.table("study_progress").select("username", "total_seconds").order("total_seconds", desc=True).limit(5).execute()
                for i, r in enumerate(rank_res.data):
                    st.write(f"**{i+1}위** {r['username'].split('@')[0]} ({int(r['total_seconds']//60)}분)")
            except: st.write("아직 랭킹 데이터가 없습니다.")

# --- 6. 메인 화면 ---
if user:
    session_duration = time.time() - st.session_state.start_time
    current_total_time = st.session_state.total_seconds + session_duration
    
    st.markdown("<h3 style='text-align: center; color: #FF8E8E;'>🌸 N1 합격 챌린지 🌸</h3>", unsafe_allow_html=True)
    st.markdown(f"<div class='timer-box'>⏰ 누적 공부 시간: {int(current_total_time // 60)}분 {int(current_total_time % 60)}초</div>", unsafe_allow_html=True)

    total_count = len(st.session_state.vocab_data)
    mastered_count = len(set(st.session_state.mastered_words))
    st.progress(mastered_count / total_count if total_count > 0 else 0)
    st.write(f"🍎 정복한 단어: {mastered_count} / {total_count}")

    word = st.session_state.vocab_data.iloc[st.session_state.current_idx]
    st.markdown(f"<div class='word-card'><p style='color:#FFA4A4;'>이 단어는?</p><div class='japanese-word'>{word['단어']}</div></div>", unsafe_allow_html=True)

    if not st.session_state.show_answer:
        if st.button("💝 정답 확인하기", use_container_width=True):
            st.session_state.show_answer = True
            st.rerun()
    else:
        st.success(f"📍 {word['히라가나']} ({word['한국어발음']}) : {word['뜻']}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌈 완벽해! (저장)", use_container_width=True):
                if st.session_state.current_idx not in st.session_state.mastered_words:
                    st.session_state.mastered_words.append(int(st.session_state.current_idx))
                try:
                    supabase.table("study_progress").upsert({
                        "username": user.email,
                        "mastered_words": list(set(st.session_state.mastered_words)),
                        "total_seconds": current_total_time,
                        "last_seen": datetime.now().isoformat()
                    }).execute()
                except: pass
                st.session_state.current_idx = random.randint(0, total_count-1)
                st.session_state.show_answer = False
                st.rerun()
        with col2:
            if st.button("🐥 다시 한 번", use_container_width=True):
                st.session_state.current_idx = random.randint(0, total_count-1)
                st.session_state.show_answer = False
                st.rerun()
else:
    st.image("https://images.unsplash.com/photo-1528459801416-a9e53bbf4e17?auto=format&fit=crop&q=80&w=800")
    st.markdown("<h2 style='text-align: center;'>함께 공부하고 인증하는<br>N1 단어 챌린지 🌸</h2>", unsafe_allow_html=True)
    st.info("왼쪽 사이드바에서 구글 로그인을 완료하면 단어장이 나타납니다!")
