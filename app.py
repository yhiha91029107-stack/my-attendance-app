import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="출석알리미 Pro", layout="centered")

# 모바일 한 줄 구성을 위한 커스텀 스타일
st.markdown("""
    <style>
    [data-testid="column"] { display: flex; align-items: center; justify-content: center; padding: 0 !important; }
    .stRadio > div { flex-direction: row !important; }
    .stButton > button { width: 100%; padding: 5px 0; font-size: 14px; }
    .school-btn-active { background-color: #FF4B4B !important; color: white !important; }
    .tel-btn { text-decoration: none; font-size: 18px; }
    div.stText { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 초기화
if 'schools' not in st.session_state:
    st.session_state['schools'] = ["우리 학교"]
if 'active_school' not in st.session_state:
    st.session_state['active_school'] = "우리 학교"
if 'students' not in st.session_state:
    st.session_state['students'] = []
if 'att_status' not in st.session_state:
    st.session_state['att_status'] = {}

# --- 2. 상단 학교 추가 및 학교 버튼 목록 ---
st.title("📱 출결 관리 시스템")

# 학교 추가 입력창 + 버튼 한 줄
col_add_1, col_add_2 = st.columns([4, 1])
with col_add_1:
    new_sch_name = st.text_input("새 학교 추가", placeholder="학교명을 입력하세요", label_visibility="collapsed")
with col_add_2:
    if st.button("➕"):
        if new_sch_name and new_sch_name not in st.session_state['schools']:
            st.session_state['schools'].append(new_sch_name)
            st.session_state['active_school'] = new_sch_name
            st.rerun()

# 생성된 학교 버튼들을 가로로 나열
st.write("🏫 **학교 선택**")
sch_cols = st.columns(len(st.session_state['schools']) if len(st.session_state['schools']) > 0 else 1)
for idx, sch in enumerate(st.session_state['schools']):
    with sch_cols[idx % len(sch_cols)]:
        # 현재 선택된 학교는 강조색 표시
        if st.button(sch, key=f"sch_btn_{sch}"):
            st.session_state['active_school'] = sch
            st.rerun()

st.info(f"현재 선택된 학교: **{st.session_state['active_school']}**")

# --- 3. 학생 추가 및 수업 시작/종료 버튼 ---
col_act_1, col_act_2, col_act_3 = st.columns([1, 1, 1])
with col_act_1:
    if st.button("👤 학생추가"): st.session_state['show_add_std'] = True
with col_act_2:
    btn_start = st.button("🚀 수업시작")
with col_act_3:
    btn_end = st.button("🔔 수업종료")

# 학생 추가 폼
if st.session_state.get('show_add_std'):
    with st.form("add_std_form"):
        c1, c2, c3 = st.columns(3)
        with c1: f_cls = st.selectbox("반", ["A반", "B반"])
        with c2: f_name = st.text_input("이름")
        with c3: f_phone = st.text_input("연락처")
        if st.form_submit_button("저장"):
            s_id = datetime.now().strftime("%H%M%S%f")
            st.session_state['students'].append({"id": s_id, "school": st.session_state['active_school'], "class": f_cls, "name": f_name, "phone": f_phone})
            st.session_state['show_add_std'] = False
            st.rerun()

# --- 4. 명단 및 출결 체크 리스트 ---
st.divider()
sel_cls = st.radio("반 선택", ["A반", "B반"], horizontal=True, label_visibility="collapsed")
curr_stds = [s for s in st.session_state['students'] if s['school'] == st.session_state['active_school'] and s['class'] == sel_cls]

# 단체 문자 미리보기 로직
if btn_start or btn_end:
    mode = "시작" if btn_start else "종료"
    st.subheader(f"💬 {mode} 문자 발송")
    for s in curr_stds:
        stat = st.session_state['att_status'].get(s['id'], {"status": "출석", "reason": ""})
        if mode == "시작":
            msg = f"[{st.session_state['active_school']}] {s['name']} 학생 출석하였습니다." if stat['status'] == "출석" else f"[{st.session_state['active_school']}] {s['name']} 학생 결석하였습니다.({stat['reason']})"
        else:
            if stat['status'] == "결석": continue
            msg = f"[{st.session_state['active_school']}] {s['name']} 학생 수업이 끝났습니다."
        
        final_msg = st.text_area(f"To: {s['name']}", value=msg, key=f"sms_{mode}_{s['id']}")
        st.markdown(f'<a href="sms:{s["phone"]}?body={final_msg}" style="display:block; background-color:#007bff; color:white; padding:10px; border-radius:5px; text-decoration:none; text-align:center;">전송하기</a>', unsafe_allow_html=True)
    st.divider()

# --- 학생 리스트 (한 줄 구성) ---
# 구성: 통화 | 이름 | 출석/결석 | 수정/삭제
for s in curr_stds:
    with st.container():
        c1, c2, c3, c4 = st.columns([0.5, 1, 2.5, 0.5])
        with c1: # 통화
            st.markdown(f'<a href="tel:{s["phone"]}" class="tel-link">📞</a>', unsafe_allow_html=True)
        with c2: # 이름
            st.write(f"**{s['name']}**")
        with c3: # 출석/결석 라디오
            cur_at = st.session_state['att_status'].get(s['id'], {"status": "출석", "reason": ""})
            new_s = st.radio(f"r_{s['id']}", ["출석", "결석"], 
                             index=0 if cur_at['status']=="출석" else 1, 
                             key=f"radio_{s['id']}", horizontal=True, label_visibility="collapsed")
            st.session_state['att_status'][s['id']] = {"status": new_s, "reason": cur_at['reason']}
        with c4: # 수정 버튼
            if st.button("✏️", key=f"ed_{s['id']}"): st.session_state['edit_id'] = s['id']

        # 결석 사유 입력 (결석 시 바로 아래 한 줄 추가)
        if new_s == "결석":
            res = st.text_input(f"사유({s['name']})", value=cur_at['reason'], key=f"res_{s['id']}", label_visibility="collapsed", placeholder="결석 사유 입력")
            st.session_state['att_status'][s['id']]['reason'] = res

        # 수정/삭제 폼
        if st.session_state.get('edit_id') == s['id']:
            with st.form(f"edit_f_{s['id']}"):
                u_n = st.text_input("이름", value=s['name'])
                u_p = st.text_input("연락처", value=s['phone'])
                cc1, cc2 = st.columns(2)
                if cc1.form_submit_button("✅ 완료"):
                    s['name'], s['phone'] = u_n, u_p
                    st.session_state['edit_id'] = None
                    st.rerun()
                if cc2.form_submit_button("🗑️ 삭제"):
                    st.session_state['students'] = [std for std in st.session_state['students'] if std['id'] != s['id']]
                    st.session_state['edit_id'] = None
                    st.rerun()
        st.write("---") # 구분선
