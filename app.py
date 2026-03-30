import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 초기 설정
st.set_page_config(page_title="출석알리미", layout="centered")

# 2. 데이터 초기화
if 'schools' not in st.session_state:
    st.session_state['schools'] = ["우리 학교"]
if 'students' not in st.session_state:
    st.session_state['students'] = []
if 'att_status' not in st.session_state:
    st.session_state['att_status'] = {}

# --- 상단 학교 관리 ---
st.title("📱 출결 알리미")

col_sch_1, col_sch_2 = st.columns([4, 1])
with col_sch_1:
    selected_school = st.selectbox("학교", st.session_state['schools'], label_visibility="collapsed")
with col_sch_2:
    if st.button("➕"):
        st.session_state['show_add_school'] = True

if st.session_state.get('show_add_school'):
    with st.form("new_sch"):
        n_name = st.text_input("새 학교명")
        if st.form_submit_button("확인"):
            if n_name:
                st.session_state['schools'].append(n_name)
                st.session_state['show_add_school'] = False
                st.rerun()

# 학생 추가 버튼
if st.button("👤 학생 추가", type="primary", use_container_width=True):
    st.session_state['show_add_std'] = True

if st.session_state.get('show_add_std'):
    with st.form("add_std"):
        c1, c2, c3 = st.columns(3)
        with c1: f_cls = st.selectbox("반", ["A반", "B반"])
        with c2: f_name = st.text_input("이름")
        with c3: f_phone = st.text_input("연락처")
        if st.form_submit_button("저장"):
            s_id = datetime.now().strftime("%H%M%S%f")
            st.session_state['students'].append({"id": s_id, "school": selected_school, "class": f_cls, "name": f_name, "phone": f_phone})
            st.session_state['show_add_std'] = False
            st.rerun()

st.divider()

# --- 명단 및 문자 버튼 ---
sel_cls = st.radio("반 선택", ["A반", "B반"], horizontal=True)
curr_stds = [s for s in st.session_state['students'] if s['school'] == selected_school and s['class'] == sel_cls]

if curr_stds:
    col_b1, col_b2 = st.columns(2)
    with col_b1: b_start = st.button("🚀 수업시작 문자", use_container_width=True)
    with col_b2: b_end = st.button("🔔 수업종료 문자", use_container_width=True)

    if b_start or b_end:
        mode = "시작" if b_start else "종료"
        st.info(f"[{mode}] 문자 전송창이 아래에 열립니다.")
        for s in curr_stds:
            stat = st.session_state['att_status'].get(s['id'], {"status": "출석", "reason": ""})
            if mode == "시작":
                msg = f"[{selected_school}] {s['name']} 학생 출석하였습니다." if stat['status'] == "출석" else f"[{selected_school}] {s['name']} 학생 결석하였습니다. 확인부탁드립니다.({stat['reason']})"
            else:
                if stat['status'] == "결석": continue
                msg = f"[{selected_school}] {s['name']} 학생 수업이 종료되었습니다."
            
            final_msg = st.text_area(f"To: {s['name']}", value=msg, key=f"m_{mode}_{s['id']}", height=100)
            st.markdown(f'<a href="sms:{s["phone"]}?body={final_msg}" style="display:inline-block; background-color:#007bff; color:white; padding:10px; border-radius:5px; text-decoration:none; width:100%; text-align:center;">전송하기</a>', unsafe_allow_html=True)
        st.divider()

# --- 학생 리스트 ---
for s in curr_stds:
    c1, c2, c3, c4 = st.columns([0.8, 1.2, 2.5, 0.8])
    with c1: st.markdown(f'<a href="tel:{s["phone"]}" style="font-size:20px; text-decoration:none;">📞</a>', unsafe_allow_html=True)
    with c2: st.write(f"**{s['name']}**")
    with c3:
        cur_at = st.session_state['att_status'].get(s['id'], {"status": "출석", "reason": ""})
        new_s = st.radio(f"s_{s['id']}", ["출석", "결석"], index=0 if cur_at['status']=="출석" else 1, key=f"r_{s['id']}", horizontal=True, label_visibility="collapsed")
        st.session_state['att_status'][s['id']] = {"status": new_s, "reason": cur_at['reason']}
    with c4:
        if st.button("✏️", key=f"e_{s['id']}"): st.session_state['edit_id'] = s['id']

    if new_s == "결석":
        res = st.text_input(f"사유({s['name']})", value=cur_at['reason'], key=f"res_{s['id']}")
        st.session_state['att_status'][s['id']]['reason'] = res

    if st.session_state.get('edit_id') == s['id']:
        with st.form(f"f_{s['id']}"):
            u_n = st.text_input("이름", value=s['name'])
            u_p = st.text_input("연락처", value=s['phone'])
            cc1, cc2 = st.columns(2)
            if cc1.form_submit_button("수정"):
                s['name'], s['phone'] = u_n, u_p
                st.session_state['edit_id'] = None
                st.rerun()
            if cc2.form_submit_button("❌ 삭제"):
                st.session_state['students'] = [std for std in st.session_state['students'] if std['id'] != s['id']]
                st.session_state['edit_id'] = None
                st.rerun()
