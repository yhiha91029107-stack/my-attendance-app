import streamlit as st
import pandas as pd
import json
from datetime import datetime
import urllib.parse

# 페이지 설정
st.set_page_config(page_title="출석체크 매니저", page_icon="✅", layout="centered")

# CSS 커스텀 스타일 (모바일 최적화 느낌)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; font-weight: bold; }
    .student-card { padding: 15px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; background: white; }
    </style>
    """, unsafe_allow_html=True)

# 세션 상태 초기화 (데이터 저장)
if 'students' not in st.session_state:
    st.session_state.students = []
if 'attendance' not in st.session_state:
    st.session_state.attendance = {}

# 사이드바: 설정 및 관리
with st.sidebar:
    st.title("⚙️ 설정")
    school_name = st.text_input("학교/학원 이름", "우리 학교")
    
    st.divider()
    st.subheader("📥 데이터 관리")
    uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx", "csv"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
        # 간단한 컬럼 매핑 로직 필요
        st.success("파일을 불러왔습니다!")

# 메인 화면
st.title("📱 출석체크 매니저")
date_str = st.date_input("날짜 선택", datetime.now()).strftime("%Y-%m-%d")

# 학생 추가 폼
with st.expander("➕ 학생 추가"):
    with st.form("add_student"):
        name = st.text_input("이름")
        phone = st.text_input("전화번호 (숫자만)")
        if st.form_submit_button("저장"):
            if name and phone:
                st.session_state.students.append({"name": name, "phone": phone})
                st.success(f"{name} 학생 추가 완료")
            else:
                st.error("정보를 입력해주세요.")

# 학생 명단 및 출석 체크
st.subheader(f"👥 학생 명단 ({len(st.session_state.students)}명)")

if not st.session_state.students:
    st.info("등록된 학생이 없습니다. 위에서 학생을 추가해주세요.")
else:
    for i, student in enumerate(st.session_state.students):
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{student['name']}**")
                # 전화 걸기 링크
                tel_link = f"tel:{student['phone']}"
                st.markdown(f"[📞 {student['phone']}]({tel_link})")
            
            with col2:
                if st.button("✅ 출석", key=f"pres_{i}"):
                    st.session_state.attendance[student['name']] = "출석"
            
            with col3:
                if st.button("❌ 결석", key=f"abs_{i}"):
                    st.session_state.attendance[student['name']] = "결석"
            
            status = st.session_state.attendance.get(student['name'], "미체크")
            color = "green" if status == "출석" else "red" if status == "결석" else "gray"
            st.markdown(f"<span style='color:{color}; font-size:12px;'>상태: {status}</span>", unsafe_allow_html=True)
            st.divider()

# 문자 발송 기능 (URL Scheme 이용)
st.subheader("💬 알림 보내기")
msg_type = st.radio("메시지 종류", ["출석 알림", "결석 알림", "종료 알림"], horizontal=True)

if st.button("📱 문자 앱 열기 (대상자 포함)"):
    target_phones = []
    if msg_type == "출석 알림":
        target_phones = [s['phone'] for s in st.session_state.students if st.session_state.attendance.get(s['name']) == "출석"]
        message = f"[{school_name}] 학생이 무사히 도착하여 수업을 시작합니다."
    elif msg_type == "결석 알림":
        target_phones = [s['phone'] for s in st.session_state.students if st.session_state.attendance.get(s['name']) == "결석"]
        message = f"[{school_name}] 학생이 아직 도착하지 않았습니다. 확인 부탁드립니다."
    else:
        target_phones = [s['phone'] for s in st.session_state.students if st.session_state.attendance.get(s['name']) == "출석"]
        message = f"[{school_name}] 오늘 수업을 마쳤습니다. 귀가 지도 부탁드립니다."

    if target_phones:
        phone_str = ",".join(target_phones)
        sms_url = f"sms:{phone_str}?body={urllib.parse.quote(message)}"
        st.markdown(f'<a href="{sms_url}" target="_blank">클릭하여 문자 보내기</a>', unsafe_allow_html=True)
    else:
        st.warning("대상 학생이 없습니다.")
