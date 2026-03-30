import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 초기 설정 및 CSS (모바일 최적화) ---
st.set_page_config(page_title="출석체크 스마트 알리미", layout="centered")

st.markdown("""
    <style>
    .stButton > button { width: 100%; border-radius: 5px; margin-bottom: 5px; }
    .student-row { padding: 10px; border-bottom: 1px solid #eee; align-items: center; }
    div[data-testid="column"] { display: flex; align-items: center; justify-content: center; }
    .tel-link { text-decoration: none; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 초기화
if 'schools' not in st.session_state:
    st.session_state['schools'] = ["우리 학교"]
if 'students' not in st.session_state:
    st.session_state['students'] = [] # 리스트 형태 저장
if 'att_status' not in st.session_state:
    st.session_state['att_status'] = {} # {학생id: {"status": "출석", "reason": ""}}

# --- 2. 상단 학교 관리 (학교명 + 추가버튼) ---
st.title("📱 출결 알리미")

col_sch_1, col_sch_2 = st.columns([4, 1])
with col_sch_1:
    selected_school = st.selectbox("학교 선택", st.session_state['schools'], label_visibility="collapsed")
with col_sch_2:
    if st.button("➕"):
        st.session_state['show_add_school'] = True

if st.session_state.get('show_add_school'):
    with st.form("new_school_form"):
        new_name = st.text_input("새 학교명 입력")
        if st.form_submit_button("확인"):
            if new_name:
                st.session_state['schools'].append(new_name)
                st.session_state['show_add_school'] = False
                st.rerun()

# --- 3. 학생 추가 섹션 ---
if st.button("👤 학생 추가", type="primary"):
    st.session_state['show_add_std'] = True

if st.session_state.get('show_add_std'):
    with 
# 명단 필터링
curr_stds = [s for s in st.session_state['students'] if s['school'] == selected_school and s['class'] == sel_cls]

# --- 5. 단체 문자 발송 버튼 (명단 바로 위에 배치) ---
if curr_stds:
    col_msg_1, col_msg_2 = st.columns(2)
    with col_msg_1:
        btn_start = st.button("🚀 수업시작 문자")
    with col_msg_2:
        btn_end = st.button("🔔 수업종료 문자")

    # 문자 발송 로직 (미리보기 창)
    if btn_start or btn_end:
        mode = "시작" if btn_start else "종료"
        st.subheader(f"💬 {mode} 문자 미리보기")
        for s in curr_stds:
            stat = st.session_state['att_status'].get(s['id'], {"status": "출석", "reason": ""})
            
            if mode == "시작":
                if stat['status'] == "출석":
                    msg = f"[{selected_school}] {s['name']} 학생 수업에 출석하였습니다."
                else:
                    msg = f"[{selected_school}] {s['name']} 학생 결석하였습니다. 확인부탁드립니다.({stat['reason']})"
            else: # 종료
                if stat['status'] == "출석":
                    msg = f"[{selected_school}] {s['name']} 수업이 끝났습니다."
                else: continue
            
            final_msg = st.text_area(f"To: {s['name']}", value=msg, key=f"sms_{mode}_{s['id']}")
            st.markdown(f'<a href="sms:{s["phone"]}?body={final_msg}" style="background-color:#007bff; color:white; padding:8px; border-radius:5px; text-decoration:none;">전송하기</a>', unsafe_allow_html=True)
        st.divider()

# --- 6. 학생 명단 루프 ---
for s in curr_stds:
    # 한 줄 구성을 위한 컬럼 배치
    # 통화 | 이름 | 상태선택 | 수정/삭제
    row_c1, row_c2, row_c3, row_c4 = st.columns([0.8, 1.2, 2.5, 0.8])
    
    with row_c1:
        st.markdown(f'<a href="tel:{s["phone"]}" class="tel-link">📞</a>', unsafe_allow_html=True)
    
    with row_c2:
        st.write(f"**{s['name']}**")
    
    with row_c3:
        current_att = st.session_state['att_status'].get(s['id'], {"status": "출석", "reason": ""})
        new_stat = st.radio(f"stat_{s['id']}", ["출석", "결석"], 
                            index=0 if current_att['status'] == "출석" else 1,
                            key=f"radio_{s['id']}", horizontal=True, label_visibility="collapsed")
        st.session_state['att_status'][s['id']] = {"status": new_stat, "reason": current_att['reason']}
        
    with row_c4:
        if st.button("✏️", key=f"edit_{s['id']}"):
            st.session_state['edit_target'] = s['id']

    # 결석 시 사유 입력창 (해당 학생 바로 아래)
    if new_stat == "결석":
        reason = st.text_input(f"사유 ({s['name']})", value=current_att['reason'], key=f"res_in_{s['id']}")
        st.session_state['att_status'][s['id']]['reason'] = reason

    # 수정 및 삭제 폼
    if st.session_state.get('edit_target') == s['id']:
        with st.form(f"edit_form_{s['id']}"):
            u_name = st.text_input("이름 수정", value=s['name'])
            u_phone = st.text_input("연락처 수정", value=s['phone'])
            c_col1, c_col2 = st.columns(2)
            if c_col1.form_submit_button("저장"):
                s['name'] = u_name
                s['phone'] = u_phone
                st.session_state['edit_target'] = None
                st.rerun()
            if c_col2.form_submit_button("❌ 학생삭제"):
                st.session_state['students'] = [std for std in st.session_state['students'] if std['id'] != s['id']]
                st.session_state['edit_target'] = None
                st.rerun()

st.divider()

# --- 7. 엑셀 업로드/다운로드 ---
with st.expander("📊 엑셀 데이터 관리"):
    up_file = st.file_uploader("명단 업로드 (엑셀)", type=["xlsx"])
    if up_file:
        up_df = pd.read_excel(up_file)
        # 엑셀은 '반', '이름', '연락처' 컬럼 필요
        for _, row in up_df.iterrows():
            std_id = datetime.now().strftime("%H%M%S%f")
            st.session_state['students'].append({
                "id": std_id, "school": selected_school, "class": str(row['반']), 
                "name": str(row['이름']), "phone": str(row['연락처'])
            })
        st.success("업로드 완료!")
