import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime
from supabase import create_client, Client

# 1. 앱 설정 및 테마
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

# 2. 서비스 연결 (Secrets 로드)
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    SHEET_URL = st.secrets["SHEET_URL"]
except Exception as e:
    st.error(f"⚠️ Streamlit Secrets 설정 오류: {e}")
    st.stop()

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# 3. 데이터 로드 및 세션 관리
@st.cache_data(ttl=60)
def load_vocab():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame(columns=['단어', '히라가나', '한국어발음', '뜻'])

def get_user():
    try:
        # 현재 세션 가져오기
        res = supabase.auth.get_session()
        return res.user if res else None
    except:
        return None

# 초기 데이터 로드
if 'vocab_data' not in st.session_state:
    st.session_state.vocab_data = load_vocab()

# 변수 초기화 (방어 로직 추가)
if 'mastered_words' not in st.session_state: st.session_state.mastered_words = []
if 'total_seconds' not in st.session_state: st.session_state.total_seconds = 0
if 'start_time' not in st.session_state: st.session_state.start_time = time.time()
if 'show_answer' not in st.session_state: st.session_state.show_answer = False

# 단어가 하나도 없을 경우 대비
if len(st.session_state.vocab_data) > 0:
    if 'current_idx' not in st.session_state:
        st.session_state.current_idx = random.randint(0, len(st.session_state.vocab_data)-1)
else:
    st.warning("구글 시트에서 데이터를 불러오지 못했습니다. CSV 주소를 확인해주세요!")
    st.stop()

user = get_user()

# --- 4. 사이드바 구성 (로그인 부분만 수정) ---
with st.sidebar:
    if not user:
        st.header("🔐 로그인")
        
        # 1. 수파베이스로부터 구글 로그인 주소를 먼저 받아옵니다.
        # [주의] MY_APP_URL은 반드시 본인의 실제 스트림릿 주소여야 합니다!
        MY_APP_URL = "https://본인의앱이름.streamlit.app" 
        
        try:
            res = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {"redirect_to": MY_APP_URL}
            })
            
            # 2. 메타 태그 대신, 사용자가 직접 클릭하는 '링크 버튼'을 만듭니다.
            # 이 버튼은 브라우저의 '전체 창'을 새 주소로 옮겨줍니다.
            st.link_button("🚀 구글 로그인 시작하기", res.url, use_container_width=True)
            st.info("위 버튼을 누르면 구글 로그인 화면으로 안전하게 이동합니다.")
            
        except Exception as e:
            st.error(f"로그인 주소를 가져오지 못했습니다: {e}")

        if st.button("로그아웃"):
            supabase.auth.sign_out()
            st.rerun()

        st.write("---")
        if st.checkbox("🏆 공부왕 랭킹 보기"):
            try:
                rank_res = supabase.table("study_progress").select("username", "total_seconds").order("total_seconds", desc=True).limit(5).execute()
                for i, r in enumerate(rank_res.data):
                    st.write(f"**{i+1}위** {r['username'].split('@')[0]} ({int(r['total_seconds']//60)}분)")
            except: st.write("랭킹을 불러올 수 없습니다.")

# 5. 메인 앱 화면
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
                
                # Supabase 저장 (오류 무시 로직 포함)
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
