import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 페이지 설정 및 고급 디자인 (이미지 스타일 CSS) ---
st.set_page_config(page_title="출석체크 매니저", layout="centered")

st.markdown("""
    <style>
    /* 전체 배경색 */
    .main { background-color: #F8F9FF; }
    
    /* 카드 공통 스타일 */
    .stHeader { color: #5D5FEF; font-weight: 700; }
    .custom-card {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    
    /* 학교/반 버튼 (칩 스타일) */
    .stButton > button {
        border-radius: 20px;
        border: 1px solid #E0E0E0;
        background-color: white;
        color: #666;
        transition: 0.3s;
    }
    /* 활성화된 버튼 스타일 (임시) */
    .active-btn { background-color: #6366F1 !important; color: white !important; }

    /* 팁 박스 */
    .tip-box {
        background-color: #FFF9EB;
        padding: 10px;
        border-radius: 10px;
        border-left: 5px solid #FFBB33;
        font-size: 13px;
        margin-bottom: 15px;
    }

    /* 학생 명단 카드 UI */
    .student-card {
        display: flex;
        align-items: center;
        background-color: #F0FFF4; /* 출석 시 연초록 */
        padding: 10px 15px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .avatar {
        width: 45px; height: 45px;
        background-color: #10B981;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 15px;
    }
    .student-info { flex-grow: 1; }
    .student-name { font-weight: bold; font-size: 16px; margin-bottom: 0; }
    .student-phone { font-size: 12px; color: #888; margin: 0; }

    /* 출석/결석 버튼 그룹 */
    .att-group { display: flex; gap: 5px; }
    .btn-present { background-color: #10B981 !important; color: white !important; border: none !important; }
    .btn-absent { background-color: #F3F4F6 !important; color: #999 !important; border: none !important; }
    
    /* 수업 시작/종료 큰 버튼 */
    .big-btn-start { background-color: #6366F1 !important; color: white !important; height: 60px !important; font-size: 18px !important; border-radius: 15px !important; }
    .big-btn-end { background-color: #1F2937 !important; color: white !important; height: 60px !important; font-size: 18px !important; border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 초기화
if 'schools' not in st.session_state: st.session_state['schools'] = ["황곡초 로봇반", "초당초 로봇반", "상록초 로봇반"]
if 'sel_sch' not in st.session_state: st.session_state['sel_sch'] = "상록초 로봇반"
if 'sel_class' not in st.session_state: st.session_state['sel_class'] = "B반"
if 'students' not in st.session_state: 
    st.session_state['students'] = [
        {"id": 1, "name": "김민재", "phone": "010-6379-7766", "school": "상록초 로봇반", "class": "B반", "status": "출석"},
        {"id": 2, "name": "양진호", "phone": "010-5451-3646", "school": "상록초 로봇반", "class": "B반", "status": "출석"},
        {"id": 3, "name": "이은율", "phone": "010-7728-4413", "school": "상록초 로봇반", "class": "B반", "status": "미체크"},
    ]

# --- 2. 상단 네비게이션 (학교/반 선택) ---
st.markdown("<h2 style='color:#6366F1;'>👤 출석체크 매니저</h2>", unsafe_allow_html=True)

# 학교 선택 (가로 칩 스타일)
st.write("학교 선택")
cols_sch = st.columns(len(st.session_state['schools']))
for i, sch in enumerate(st.session_state['schools']):
    with cols_sch[i]:
        is_active = "active-btn" if st.session_state['sel_sch'] == sch else ""
        if st.button(sch, key=f"sch_{i}"):
            st.session_state['sel_sch'] = sch
            st.rerun()

# 반 선택 (A/B/반추가)
st.write("반 선택")
c1, c2, c3, _ = st.columns([1, 1, 1.5, 2])
with c1:
    if st.button("A반", key="btn_a"): st.session_state['sel_class'] = "A반"
with c2:
    if st.button("B반", key="btn_b"): st.session_state['sel_class'] = "B반"
with c3:
    st.button("반 추가 +", key="btn_add_cls")

# --- 3. 날짜 및 팁 ---
col_date, col_today = st.columns([3, 1])
with col_date:
    st.date_input("조회 날짜", label_visibility="collapsed")
with col_today:
    st.button("오늘로 이동", key="go_today")

st.markdown("""
    <div class="tip-box">
        💡 팁: 문자 앱이 열리지 않는다면 우측 상단의 '새 탭에서 열기' 아이콘을 눌러주세요.
    </div>
    """, unsafe_allow_html=True)

# --- 4. 학생 추가 섹션 (카드 UI) ---
with st.container():
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.write("➕ **학생 추가**")
    ca1, ca2 = st.columns(2)
    with ca1: n_name = st.text_input("이름", placeholder="홍길동", label_visibility="collapsed")
    with ca2: n_phone = st.text_input("전화번호", placeholder="01012345678", label_visibility="collapsed")
    
    cb1, cb2 = st.columns([3, 1])
    with cb1: st.write(f"소속: <span style='color:blue;'>{st.session_state['sel_sch']} / {st.session_state['sel_class']}</span>", unsafe_allow_html=True)
    with cb2: 
        if st.button("저장", type="primary", use_container_width=True):
            st.success("저장됨")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. 시작/종료 큰 버튼 ---
st.write("")
col_start, col_end = st.columns(2)
with col_start:
    st.button(f"{st.session_state['sel_class']} 수업 시작", key="big_start", use_container_width=True)
with col_end:
    st.button(f"{st.session_state['sel_class']} 수업 끝남", key="big_end", use_container_width=True)

# --- 6. 학생 명단 리스트 ---
st.write("")
st.markdown(f"### 👥 학생 명단 <small style='font-size:12px; color:gray;'>오늘 출석 현황</small>", unsafe_allow_html=True)

# 통계 정보
stat_c1, stat_c2, stat_c3 = st.columns([1,1,1])
stat_c1.metric("출석", "16")
stat_c2.metric("결석", "0")
stat_c3.metric("미체크", "-7")

st.write("---")

# 필터링된 학생 출력
for s in st.session_state['students']:
    # 카드 컨테이너 시작
    with st.container():
        # 열 구성: 아바타 | 이름/번호 | 수정버튼 | 출석버튼 | 결석버튼 | 삭제버튼
        c_ava, c_info, c_edit, c_att, c_abs, c_del = st.columns([0.6, 1.5, 0.4, 0.8, 0.8, 0.4])
        
        with c_ava:
            st.markdown(f"<div class='avatar'>{s['name'][0]}</div>", unsafe_allow_html=True)
        
        with c_info:
            st.markdown(f"**{s['name']}**<br><small>{s['phone']}</small>", unsafe_allow_html=True)
        
        with c_edit:
            st.button("✏️", key=f"edit_{s['id']}", help="수정")
        
        with c_att:
            is_att = s['status'] == "출석"
            if st.button("출석", key=f"att_b_{s['id']}", type="primary" if is_att else "secondary"):
                s['status'] = "출석"
                st.rerun()
                
        with c_abs:
            is_abs = s['status'] == "결석"
            if st.button("결석", key=f"abs_b_{s['id']}", type="primary" if is_abs else "secondary"):
                s['status'] = "결석"
                st.rerun()
        
        with c_del:
            st.button("🗑️", key=f"del_{s['id']}", help="삭제")
        
        st.write("") # 간격
