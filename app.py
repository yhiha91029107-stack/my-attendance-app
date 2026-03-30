import streamlit as st
import pandas as pd
from datetime import datetime
import io

# --- 1. 초기 설정 및 데이터 관리 ---
st.set_page_config(page_title="출석알리미 Pro", layout="centered")

# 데이터 유지를 위한 세션 상태 초기화
if 'schools' not in st.session_state:
    st.session_state['schools'] = ["우리 학교"]
if 'students' not in st.session_state:
    # 컬럼: 학교명, 반, 이름, 연락처
    st.session_state['students'] = pd.DataFrame(columns=['학교명', '반', '이름', '연락처'])
if 'history' not in st.session_state:
    # 컬럼: 날짜, 학교명, 반, 이름, 상태, 사유
    st.session_state['history'] = pd.DataFrame(columns=['날짜', '학교명', '반', '이름', '상태', '사유'])

# --- 2. 사이드바: 학교 관리 (여러 학교 추가/삭제) ---
st.sidebar.header("🏫 학교 관리")
new_school = st.sidebar.text_input("새 학교 추가")
if st.sidebar.button("학교 추가"):
    if i_school := new_school.strip():
        st.session_state['schools'].append(i_school)
        st.rerun()

selected_school = st.sidebar.selectbox("학교 선택", st.session_state['schools'])
st.sidebar.write("---")

# --- 3. 메인 화면 구성 (탭) ---
tab1, tab2, tab3, tab4 = st.tabs(["✅ 출결체크", "📝 명단관리", "💬 문자발송", "📊 기록조회"])

# --- [Tab 1] 출결체크 화면 ---
with tab1:
    st.subheader(f"📍 {selected_school}")
    sel_class = st.selectbox("반 선택", ["A반", "B반", "C반", "D반"])
    
    # 해당 학교/반 학생 필터링
    df_std = st.session_state['students']
    curr_std = df_std[(df_std['학교명'] == selected_school) & (df_std['반'] == sel_class)]
    
    if curr_std.empty:
        st.info("학생이 없습니다. '명단관리' 탭에서 학생을 등록해 주세요.")
    else:
        st.write("---")
        attendance_data = []
        for i, row in curr_std.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    st.write(f"**{row['이름']}**")
                    # 통화 버튼 (HTML tel 링크)
                    st.markdown(f'<a href="tel:{row["연락처"]}" style="text-decoration:none;">📞 통화하기</a>', unsafe_allow_html=True)
                with c2:
                    status = st.radio(f"{row['이름']} 상태", ["출석", "결석"], key=f"status_{i}", horizontal=True, label_visibility="collapsed")
                with c3:
                    # 삭제 버튼
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state['students'] = st.session_state['students'].drop(i)
                        st.rerun()
                
                reason = ""
                if status == "결석":
                    reason = st.text_input(f"결석 사유 ({row['이름']})", key=f"reason_{i}", placeholder="사유 입력")
                
                attendance_data.append({
                    '날짜': datetime.now().strftime("%Y-%m-%d"),
                    '학교명': selected_school,
                    '반': sel_class,
                    '이름': row['이름'],
                    '연락처': row['연락처'],
                    '상태': status,
                    '사유': reason
                })
                st.write("---")
        
        if st.button("📁 오늘의 출결 저장하기", use_container_width=True):
            new_history = pd.DataFrame(attendance_data)
            st.session_state['history'] = pd.concat([st.session_state['history'], new_history], ignore_index=True)
            st.session_state['today_check'] = attendance_data # 문자 발송용 임시 저장
            st.success("데이터가 히스토리에 저장되었습니다!")

# --- [Tab 2] 명단 관리 (직접 입력 & 엑셀) ---
with tab2:
    st.subheader("학생 명단 관리")
    with st.expander("➕ 학생 직접 추가"):
        with st.form("add_std_form", clear_on_submit=True):
            f_class = st.selectbox("반", ["A반", "B반", "C반", "D반"])
            f_name = st.text_input("이름")
            f_phone = st.text_input("연락처 (숫자만)")
            if st.form_submit_button("등록", use_container_width=True):
                new_row = pd.DataFrame({'학교명': [selected_school], '반': [f_class], '이름': [f_name], '연락처': [f_phone]})
                st.session_state['students'] = pd.concat([st.session_state['students'], new_row], ignore_index=True)
                st.rerun()

    with st.expander("📥 엑셀 파일로 명단 올리기"):
        up_file = st.file_uploader("엑셀 파일 선택 (.xlsx)", type=["xlsx"])
        if up_file:
            up_df = pd.read_excel(up_file)
            # 엑셀 컬럼이 '반', '이름', '연락처'라고 가정
            up_df['학교명'] = selected_school
            st.session_state['students'] = pd.concat([st.session_state['students'], up_df], ignore_index=True)
            st.success("엑셀 명단 등록 성공!")

    st.write("### 전체 학생 명단")
    st.dataframe(st.session_state['students'], use_container_width=True)

# --- [Tab 3] 문자 발송 (수업 시작/종료) ---
with tab3:
    if 'today_check' not in st.session_state:
        st.warning("먼저 '출결체크' 탭에서 저장하기 버튼을 눌러주세요.")
    else:
        st.subheader("📢 단체 문자 발송 미리보기")
        mode = st.radio("발송 시점", ["수업 시작", "수업 종료"], horizontal=True)
        
        for data in st.session_state['today_check']:
            if mode == "수업 시작":
                if data['상태'] == "출석":
                    msg = f"[{selected_school}] {data['이름']} 학생 수업에 출석하였습니다."
                else:
                    msg = f"[{selected_school}] {data['이름']} 학생 수업에 결석하였습니다. 확인 부탁드립니다. (사유: {data['사유']})"
            else: # 수업 종료
                if data['상태'] == "출석":
                    msg = f"[{selected_school}] {data['이름']} 학생 수업이 끝났습니다. 귀가 지도 부탁드립니다."
                else:
                    continue # 결석생은 종료 문자 생략
            
            # 개별 수정 가능한 텍스트 상자
            final_msg = st.text_area(f"To: {data['이름']} ({data['연락처']})", value=msg, height=100)
            # 모바일용 문자 발송 버튼
            sms_link = f"sms:{data['연락처']}?body={final_msg}"
            st.markdown(f'<a href="{sms_link}" style="background-color:#4CAF50; color:white; padding:10px; text-decoration:none; border-radius:5px;">📲 문자 전송 창 열기</a>', unsafe_allow_html=True)
            st.write("---")

# --- [Tab 4] 기록 조회 및 엑셀 다운로드 ---
with tab4:
    st.subheader("📊 출결 기록 히스토리")
    date_list = st.session_state['history']['날짜'].unique()
    sel_date = st.selectbox("날짜 선택", date_list if len(date_list)>0 else [datetime.now().strftime("%Y-%m-%d")])
    
    hist_df = st.session_state['history'][st.session_state['history']['날짜'] == sel_date]
    st.dataframe(hist_df, use_container_width=True)
    
    if not hist_df.empty:
        # 엑셀 다운로드 기능
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            hist_df.to_excel(writer, index=False, sheet_name='출석부')
        processed_data = output.getvalue()
        st.download_button(
            label="📥 이 날짜 기록 엑셀로 받기",
            data=processed_data,
            file_name=f"출석부_{sel_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
