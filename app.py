import streamlit as st

import pandas as pd
# 1. 페이지 설정
st.set_page_config(page_title="출석알리미", layout="centered")

# 2. 데이터 초기화
if 'students' not in st.session_state:
    st.session_state['students'] = pd.DataFrame(columns=['반', '이름', '연락처'])
if 'classes' not in st.session_state:
    st.session_state['classes'] = ['A반', 'B반']
if 'school_name' not in st.session_state:
    st.session_state['school_name'] = "우리 학교"

# --- 앱 타이틀 ---
st.title(f"🔔 {st.session_state['school_name']}")

# --- 메뉴 구성 ---
tab1, tab2, tab3 = st.tabs(["✅ 출석체크", "📝 명단관리", "⚙️ 설정"])

with tab1:
    sel_class = st.selectbox("반 선택", st.session_state['classes'])
    df = st.session_state['students']
    class_students = df[df['반'] == sel_class]

    if class_students.empty:
        st.info("학생을 먼저 등록해 주세요.")
    else:
        results = []
        for i, row in class_students.iterrows():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**{row['이름']}** ({row['연락처'][-4:]})")
            with c2:
                is_present = st.checkbox("출석", value=True, key=f"att_{i}")
            results.append({"이름": row['이름'], "연락처": row['연락처'], "상태": "출석" if is_present else "결석"})

        if st.button("🚀 문자 미리보기 생성", use_container_width=True):
            st.divider()
            for res in results:
                txt = "도착했습니다" if res['상태'] == "출석" else "미도착(결석)입니다"
                msg = f"[{st.session_state['school_name']}] {res['이름']} 학생이 안전하게 {txt}."
                st.text_area(f"To: {res['연락처']}", msg, height=100)

with tab2:
    st.subheader("학생 추가")
    with st.form("add_form", clear_on_submit=True):
        f_class = st.selectbox("등록할 반", st.session_state['classes'])
        f_name = st.text_input("이름")
        f_phone = st.text_input("연락처(숫자만)")
        if st.form_submit_button("등록하기", use_container_width=True):
            if f_name and f_phone:
                new_row = pd.DataFrame({'반': [f_class], '이름': [f_name], '연락처': [f_phone]})
                st.session_state['students'] = pd.concat([st.session_state['students'], new_row], ignore_index=True)
                st.success(f"{f_name} 등록 완료!")

    st.divider()
    st.dataframe(st.session_state['students'], use_container_width=True)

with tab3:
    st.subheader("환경 설정")
    st.session_state['school_name'] = st.text_input("학교명 변경", value=st.session_state['school_name'])
    new_cls = st.text_input("새로운 반 이름 추가")
    if st.button("반 추가"):
        if new_cls and new_cls not in st.session_state['classes']:
            st.session_state['classes'].append(new_cls)
            st.rerun()
