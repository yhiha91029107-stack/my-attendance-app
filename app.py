import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- 1. 페이지 설정 및 디자인 (이미지 스타일 재현) ---
st.set_page_config(page_title="스마트 출석부", layout="centered")

st.markdown("""
    <style>
    .main { background-color: white; }
    /* 학년/반 헤더 스타일 */
    .group-header {
        font-size: 20px; font-weight: bold; padding: 15px 0;
        border-bottom: 2px solid #333; margin-top: 20px;
    }
    /* 학생 이름 밑줄 스타일 */
    .student-name {
        font-size: 18px; text-decoration: underline; color: #333; font-weight: 500;
    }
    .student-id { color: #666; font-size: 16px; margin-right: 15px; }
    
    /* 버튼 스타일 커스텀 */
    div.stButton > button {
        border: 1px solid #ccc; background-color: white; color: #333;
        padding: 2px 10px; font-size: 14px; height: 32px;
    }
    /* 출석/결석 색상 적용 (선택 시) */
    .stButton button:active, .stButton button:focus { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 초기화
if 'schools' not in st.session_state: st.session_state['schools'] = ["우리 학교"]
if 'sel_sch' not in st.session_state: st.session_state['sel_sch'] = "우리 학교"
if 'students' not in st.session_state: st.session_state['students'] = pd.DataFrame(columns=['학교명', '그룹', '번호', '이름', '연락처'])
if 'att_data' not in st.session_state: st.session_state['att_data'] = {} # {학생이름: 상태}

# --- 2. 상단 학교 선택 및 학생 등록 (엑셀 포함) ---
st.title("📑 스마트 출석 시스템")

# 학교 추가/선택 (버튼형)
col_sch_add, _ = st.columns([2, 1])
with col_sch_add:
    with st.expander("🏫 학교 관리"):
        new_sch = st.text_input("새 학교명")
        if st.button("학교 추가"):
            if new_sch and new_sch not in st.session_state['schools']:
                st.session_state['schools'].append(new_sch)
                st.rerun()

# 학교 선택 버튼 가로 배치
sch_btns = st.columns(len(st.session_state['schools']))
for i, sch in enumerate(st.session_state['schools']):
    with sch_btns[i]:
        if st.button(sch, key=f"sch_{i}", type="primary" if st.session_state['sel_sch'] == sch else "secondary", use_container_width=True):
            st.session_state['sel_sch'] = sch
            st.rerun()

st.divider()

# 학생 등록 섹션 (직접 + 엑셀)
with st.expander("👤 학생 명단 등록 (직접 또는 엑셀)"):
    tab_manual, tab_excel = st.tabs(["직접 입력", "엑셀 업로드"])
    
    with tab_manual:
        with st.form("manual_reg", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns([1.5, 1, 1.5, 2])
            f_group = c1.text_input("그룹(예: 1학년)", placeholder="1학년")
            f_num = c2.text_input("번호")
            f_name = c3.text_input("이름")
            f_phone = c4.text_input("연락처")
            if st.form_submit_button("등록", use_container_width=True):
                new_row = pd.DataFrame({'학교명': [st.session_state['sel_sch']], '그룹': [f_group], '번호': [f_num], '이름': [f_name], '연락처': [f_phone]})
                st.session_state['students'] = pd.concat([st.session_state['students'], new_row], ignore_index=True)
                st.rerun()
                
    with tab_excel:
        st.write("엑셀 컬럼: 그룹, 번호, 이름, 연락처")
        up_file = st.file_uploader("엑셀 파일 선택 (.xlsx)", type=["xlsx"])
        if up_file:
            up_df = pd.read_excel(up_file)
            up_df['학교명'] = st.session_state['sel_sch']
            st.session_state['students'] = pd.concat([st.session_state['students'], up_df], ignore_index=True)
            st.success("엑셀 업로드 완료!")

# --- 3. 컨트롤 버튼 (시작/종료 문자) ---
st.write("")
col_msg1, col_msg2, col_msg3 = st.columns([1,1,1])
with col_msg1: btn_start = st.button("🚀 수업시작 문자", use_container_width=True)
with col_msg2: btn_end = st.button("🔔 수업종료 문자", use_container_width=True)
with col_msg3: 
    if st.button("🗑️ 명단 초기화", type="secondary"): 
        st.session_state['students'] = pd.DataFrame(columns=['학교명', '그룹', '번호', '이름', '연락처'])
        st.rerun()

# --- 4. 출석부 리스트 (이미지 스타일 적용) ---
df = st.session_state['students']
curr_school_stds = df[df['학교명'] == st.session_state['sel_sch']]

if curr_school_stds.empty:
    st.info("등록된 학생이 없습니다.")
else:
    # 학년/그룹별로 정렬 및 그룹화
    groups = curr_school_stds['그룹'].unique()
    
    for group_name in groups:
        group_df = curr_school_stds[curr_school_stds['그룹'] == group_name]
        st.markdown(f'<div class="group-header">{group_name} ({len(group_df)}명)</div>', unsafe_allow_html=True)
        
        for idx, row in group_df.iterrows():
            # 학생 한 줄 레이아웃
            st.write("") # 간격
            c_info, c_att, c_late, c_early, c_absent = st.columns([2.5, 1, 1, 1, 1])
            
            with c_info:
                # 번호 + 이름(밑줄) + 통화링크
                st.markdown(f'<span class="student-id">{row["번호"]}</span> <a href="tel:{row["연락처"]}" style="text-decoration:none;"><span class="student-name">{row["이름"]}</span></a>', unsafe_allow_html=True)
            
            # 현재 상태 가져오기
            s_key = f"{st.session_state['sel_sch']}_{group_name}_{row['이름']}"
            curr_stat = st.session_state['att_data'].get(s_key, "미체크")
            
            # 버튼 클릭 시 색상 변경 로직 (초록/빨강 등)
            with c_att:
                if st.button("출석", key=f"btn_a_{idx}", help="출석"):
                    st.session_state['att_data'][s_key] = "출석"
            with c_late:
                st.button("지각", key=f"btn_l_{idx}")
            with c_early:
                st.button("조퇴", key=f"btn_e_{idx}")
            with c_absent:
                if st.button("결석", key=f"btn_b_{idx}"):
                    st.session_state['att_data'][s_key] = "결석"
            
            # 상태 표시 (선택된 경우 강조)
            if curr_stat == "출석":
                st.markdown(f'<p style="color:green; font-weight:bold; font-size:12px; margin:0; text-align:right;">● 출석체크됨</p>', unsafe_allow_html=True)
            elif curr_stat == "결석":
                st.markdown(f'<p style="color:red; font-weight:bold; font-size:12px; margin:0; text-align:right;">● 결석체크됨</p>', unsafe_allow_html=True)

            st.markdown('<div style="border-bottom: 1px dashed #ddd; padding-top:5px;"></div>', unsafe_allow_html=True)

# --- 5. 문자 발송 미리보기 ---
if btn_start or btn_end:
    mode = "시작" if btn_start else "종료"
    st.divider()
    st.subheader(f"💬 {mode} 알림 문자")
    for idx, row in curr_school_stds.iterrows():
        s_key = f"{st.session_state['sel_sch']}_{row['그룹']}_{row['이름']}"
        stat = st.session_state['att_data'].get(s_key, "출석")
        
        if mode == "시작":
            msg = f"[{st.session_state['sel_sch']}] {row['이름']} 학생 안전하게 출석하였습니다." if stat == "출석" else f"[{st.session_state['sel_sch']}] {row['이름']} 학생 결석입니다. 확인 부탁드립니다."
        else:
            if stat == "결석": continue
            msg = f"[{st.session_state['sel_sch']}] {row['이름']} 학생 수업 종료 후 하가하였습니다."
            
        final_msg = st.text_area(f"To: {row['이름']}", value=msg, key=f"sms_{idx}")
        st.markdown(f'<a href="sms:{row["연락처"]}?body={final_msg}" style="display:block; text-align:center; background:#007bff; color:white; padding:10px; border-radius:5px; text-decoration:none;">문자 전송하기</a>', unsafe_allow_html=True)
