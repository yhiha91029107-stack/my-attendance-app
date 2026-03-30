import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 페이지 설정 및 디자인 (어제의 깔끔한 스타일 재현) ---
st.set_page_config(page_title="출석알리미", layout="centered")

st.markdown("""
    <style>
    /* 전체 배경 및 폰트 설정 */
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    
    /* 학교 선택 버튼 스타일 */
    .school-tag { display: inline-block; padding: 5px 15px; margin: 5px; border-radius: 20px; background-color: #e9ecef; cursor: pointer; border: 1px solid #dee2e6; }
    .active-tag { background-color: #007bff; color: white; border-color: #007bff; }
    
    /* 학생 리스트 한 줄 디자인 */
    .student-card { background: white; padding: 10px; border-radius: 10px; margin-bottom: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .tel-icon { font-size: 20px; text-decoration: none; margin-right: 10px; }
    
    /* 버튼 간격 조정 */
    .stHorizontalBlock { gap: 0.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 초기화
if 'schools' not in st.session_state: st.session_state['schools'] = ["우리 학교"]
if 'sel_sch' not in st.session_state: st.session_state['sel_sch'] = "우리 학교"
if 'students' not in st.session_state: st.session_state['students'] = []
if 'att_status' not in st.session_state: st.session_state['att_status'] = {}

# --- 2. 상단 학교 관리 (버튼형 선택창) ---
st.title("📱 스마트 출석부")

# 학교 추가
with st.expander("🏫 학교 추가/관리"):
    c1, c2 = st.columns([3,1])
    with c1: new_sch = st.text_input("새 학교명", label_visibility="collapsed")
    with c2: 
        if st.button("추가"):
            if new_sch and new_sch not in st.session_state['schools']:
                st.session_state['schools'].append(new_sch)
                st.session_state['sel_sch'] = new_sch
                st.rerun()

# 학교 선택 버튼 리스트
st.write("📍 **학교 선택**")
sch_cols = st.columns(4) # 한 줄에 4개씩 배치
for i, sch in enumerate(st.session_state['schools']):
    with sch_cols[i % 4]:
        # 선택된 학교는 파란색 버튼(primary), 나머지는 일반 버튼
        if st.button(sch, key=f"sch_{i}", type="primary" if st.session_state['sel_sch'] == sch else "secondary"):
            st.session_state['sel_sch'] = sch
            st.rerun()

st.divider()

# --- 3. 컨트롤 버튼 (학생추가 / 시작 / 종료) ---
c_act1, c_act2, c_act3 = st.columns(3)
with c_act1:
    if st.button("👤 학생추가", use_container_width=True): st.session_state['show_add'] = True
with c_act2:
    btn_start = st.button("🚀 수업시작", use_container_width=True)
with c_act3:
    btn_end = st.button("🔔 수업종료", use_container_width=True)

# 학생 추가 팝업
if st.session_state.get('show_add'):
    with st.form("add_std"):
        st.write("🆕 새로운 학생 등록")
        col1, col2, col3 = st.columns(3)
        with col1: f_cls = st.selectbox("반", ["A반", "B반"])
        with col2: f_name = st.text_input("이름")
        with col3: f_phone = st.text_input("연락처")
        if st.form_submit_button("저장"):
            s_id = datetime.now().strftime("%H%M%S%f")
            st.session_state['students'].append({"id": s_id, "school": st.session_state['sel_sch'], "class": f_cls, "name": f_name, "phone": f_phone})
            st.session_state['show_add'] = False
            st.rerun()

# --- 4. 출석 체크 리스트 ---
sel_cls = st.radio("반 선택", ["A반", "B반"], horizontal=True, label_visibility="collapsed")
curr_stds = [s for s in st.session_state['students'] if s['school'] == st.session_state['sel_sch'] and s['class'] == sel_cls]

# 단체 문자 발송 미리보기
if btn_start or btn_end:
    mode = "시작" if btn_start else "종료"
    st.subheader(f"💬 {mode} 문자 발송")
    for s in curr_stds:
        stat = st.session_state['att_status'].get(s['id'], {"status": "출석", "reason": ""})
        if mode == "시작":
            msg = f"[{st.session_state['sel_sch']}] {s['name']} 학생 출석하였습니다." if stat['status'] == "출석" else f"[{st.session_state['sel_sch']}] {s['name']} 학생 결석하였습니다.({stat['reason']})"
        else:
            if stat['status'] == "결석": continue
            msg = f"[{st.session_state['sel_sch']}] {s['name']} 학생 수업이 끝났습니다."
        
        final_msg = st.text_area(f"To: {s['name']}", value=msg, key=f"sms_{mode}_{s['id']}")
        st.markdown(f'<a href="sms:{s["phone"]}?body={final_msg}" style="display:block; background-color:#007bff; color:white; padding:8px; border-radius:5px; text-decoration:none; text-align:center; font-size:14px;">메시지 전송</a>', unsafe_allow_html=True)
    if st.button("닫기"): st.rerun()
    st.divider()

# --- 학생 명단 루프 (어제처럼 깔끔한 한 줄 구성) ---
for s in curr_stds:
    # 한 줄 컬럼 배치
    col_call, col_info, col_att, col_edit = st.columns([0.4, 1.2, 2.3, 0.4])
    
    with col_call: # 통화 아이콘
        st.markdown(f'<a href="tel:{s["phone"]}" class="tel-icon">📞</a>', unsafe_allow_html=True)
    
    with col_info: # 이름 (연락처 제외하고 이름만 강조)
        st.write(f"**{s['name']}**")
    
    with col_att: # 출석/결석 (가로형 라디오)
        cur_val = st.session_state['att_status'].get(s['id'], {"status": "출석", "reason": ""})
        new_val = st.radio(f"r_{s['id']}", ["출석", "결석"], 
                           index=0 if cur_val['status']=="출석" else 1, 
                           key=f"radio_{s['id']}", horizontal=True, label_visibility="collapsed")
        st.session_state['att_status'][s['id']] = {"status": new_val, "reason": cur_val['reason']}
    
    with col_edit: # 수정 아이콘
        if st.button("✏️", key=f"ed_{s['id']}"):
            st.session_state['edit_id'] = s['id']

    # 결석 사유창 (결석 시에만 바로 아래 깔끔하게 표시)
    if new_val == "결석":
        res = st.text_input(f"사유({s['name']})", value=cur_val['reason'], key=f"res_{s['id']}", placeholder="결석 사유를 입력하세요", label_visibility="collapsed")
        st.session_state['att_status'][s['id']]['reason'] = res

    # 수정/삭제 모달
    if st.session_state.get('edit_id') == s['id']:
        with st.form(f"edit_f_{s['id']}"):
            st.write(f"📝 {s['name']} 학생 정보 수정")
            u_n = st.text_input("이름", value=s['name'])
            u_p = st.text_input("연락처", value=s['phone'])
            c1, c2 = st.columns(2)
            if c1.form_submit_button("수정 완료"):
                s['name'], s['phone'] = u_n, u_p
                st.session_state['edit_id'] = None
                st.rerun()
            if c2.form_submit_button("🗑️ 학생 삭제"):
                st.session_state['students'] = [std for std in st.session_state['students'] if std['id'] != s['id']]
                st.session_state['edit_id'] = None
                st.rerun()
    st.markdown('<div style="height:1px; background-color:#eee; margin:5px 0;"></div>', unsafe_allow_html=True)
