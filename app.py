```python
import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정 (모바일 최적화)
st.set_page_config(page_title="출석 알리미", layout="centered")

# 2. 데이터 저장소 초기화 (세션 상태)
if 'students' not in st.session_state:
    st.session_state['students'] = pd.DataFrame(columns=['반', '이름', '연락처'])
if 'classes' not in st.session_state:
    st.session_state['classes'] = ['A반', 'B반']
if 'school_name' not in st.session_state:
    st.session_state['school_name'] = "우리 학교"

# --- 앱 상단 타이틀 ---
st.title(f"🔔 {st.session_state['school_name']}")

# --- 메뉴 구성 (탭 방식이 모바일에서 편합니다) ---
tab1, tab2, tab3 = st.tabs(["✅ 출석체크", "👥 학생관리", "⚙️ 설정"])

# --- [TAB 1] 출석체크 기능 ---
with tab1:
    sel_class = st.selectbox("관리할 반 선택", st.session_state['classes'])
    df = st.session_state['students']
    class_students = df[df['반'] == sel_class]

    if class_students.empty:
        st.info("등록된 학생이 없습니다. '학생관리' 탭에서 등록해 주세요.")
    else:
        st.write(f"### {sel_class} 출석부")
        attendance_results = []
        
        # 학생별 체크박스 생성
        for i, row in class_students.iterrows():
            cols = st.columns([3, 1])
            with cols[0]:
                st.write(f"**{row['이름']}** ({row['연락처'][-4:]})")
            with cols[1]:
                # 기본값은 출석(True)
                is_present = st.checkbox("출석", value=True, key=f"att_{i}")
            
            attendance_results.append({
                "이름": row['이름'], 
                "연락처": row['연락처'], 
                "상태": "출석" if is_present else "결석"
            })
        
        st.divider()
        
        # 문자 메시지 생성 버튼
        if st.button("🚀 단체 문자 미리보기 생성", use_container_width=True):
            st.subheader("📱 발송 예정 메시지")
            for res in attendance_results:
                status_text = "안전하게 도착했습니다" if res['상태'] == "출석" else "아직 도착하지 않았습니다(결석)"
                msg = f"[{st.session_state['school_name']}] 안녕하세요, {res['이름']} 학생이 금일 {status_text}."
                
                # 모바일에서 복사하기 쉽게 텍스트 박스로 출력
                st.text_area(f"To: {res['연락처']}", msg, height=100)
            st.success("위 내용을 복사하여 문자로 발송하세요!")

# --- [TAB 2] 학생 명단 관리 ---
with tab2:
    st.subheader("학생 등록")
    
    # 직접 입력 폼
    with st.form("add_student_form", clear_on_submit=True):
        reg_class = st.selectbox("반 선택", st.session_state['classes'])
        reg_name = st.text_input("학생 이름")
        reg_phone = st.text_input("연락처 (숫자만 입력)")
        submit = st.form_submit_button("학생 추가하기", use_container_width=True)
        
        if submit:
            if reg_name and reg_phone:
                new_student = pd.DataFrame({'반': [reg_class], '이름': [reg_name], '연락처': [reg_phone]})
                st.session_state['students'] = pd.concat([st.session_state['students'], new_student], ignore_index=True)
                st.success(f"{reg_name} 학생 등록 완료!")
            else:
                st.error("이름과 연락처를 모두 입력해주세요.")

    st.divider()
    
    # 엑셀 파일 업로드
    st.subheader("엑셀로 대량 등록")
    uploaded_file = st.file_uploader("엑셀 파일(.xlsx) 선택", type=["xlsx"])
    if uploaded_file:
        try:
            up_df = pd.read_excel(uploaded_file)
            # 엑셀에 '이름', '연락처' 컬럼이 있어야 함
            up_df['반'] = reg_class # 현재 선택된 반으로 일괄 등록
            st.session_state['students'] = pd.concat([st.session_state['students'], up_df], ignore_index=True)
            st.success("엑셀 명단 등록 성공!")
        except Exception as e:
            st.error(f"파일 오류: {e}")

    # 현재 명단 보기/삭제
    st.subheader("현재 전체 명단")
    st.dataframe(st.session_state['students'], use_container_width=True)
    if st.button("🗑️ 전체 명단 삭제", type="secondary"):
        st.session_state['students'] = pd.DataFrame(columns=['반', '이름', '연락처'])
        st.rerun()

# --- [TAB 3] 설정 (학교명, 반 추가) ---
with tab3:
    st.subheader("기본 정보 설정")
    
    # 학교명 변경
    new_school = st.text_input("학교명/학원명 변경", value=st.session_state['school_name'])
    if st.button("학교명 저장", use_container_width=True):
        st.session_state['school_name'] = new_school
        st.rerun()
    
    st.divider()
    
    # 반 추가
    st.subheader("반 관리")
    add_cls = st.text_input("새로운 반 이름 (예: C반, 햇살반)")
    if st.button("반 추가하기", use_container_width=True):
        if add_cls and add_cls not in st.session_state['classes']:
            st.session_state['classes'].append(add_cls)
            st.success(f"{add_cls}이 추가되었습니다.")
            st.rerun()
```

---

### 2. `requirements.txt`에 들어갈 내용 (중요!)

GitHub에서 파일을 하나 더 만드세요. 이름은 반드시 **`requirements.txt`**여야 합니다.

```text
streamlit
pandas
openpyxl
```

---

### 💡 팁
1. **GitHub에 저장할 때:** 아래쪽 초록색 버튼(**Commit changes**)을 꼭 눌러야 저장됩니다.
2. **Streamlit 배포 시:** 파일을 다 올린 후 [Streamlit Cloud](https://share.streamlit.io/)에 가서 배포를 누르면, 1~2분 뒤에 링크가 나옵니다.

이제 이 코드를 복사해서 진행해 보세요! 다 하신 후에 **링크가 생성되면 저에게 알려주세요.** 제대로 열리는지 함께 확인해 드릴게요.
13.5s
info
Google AI models may make mistakes, so double-check outputs.
Use Arrow Up and Arrow Down to select a turn, Enter to jump to it, and Escape to return to the chat.
Start typing a prompt
