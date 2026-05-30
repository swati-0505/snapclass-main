import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.components.dialog_share_subject import share_subject_dialog
from src.database.db import check_teacher_exist, create_teacher, teacher_login,get_teacher_subjects
from src.components.dialog_create_subject import create_subject_dialog

def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()

    elif 'teacher_login_type' not in st.session_state:
        st.session_state['teacher_login_type'] = 'login'

    if st.session_state['teacher_login_type'] == 'login':
        teacher_screen_login()

    elif st.session_state['teacher_login_type'] == 'register':
        teacher_screen_register()

def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2)
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {teacher_data['name']}!")
        if st.button(
            'Logout',
            type='secondary',
            key='loginbackbtn'
        ):
            st.session_state['is_logged_in'] = False
            del st.session_state['teacher_data']
            st.rerun()
    st.write("")
    if "current_teacher_tab" not in st.session_state:
        st.session_state['current_teacher_tab'] = "take_attendance"
    tab1, tab2, tab3 = st.columns(3)
    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance',type=type1, width='stretch', icon=':material/person_check:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()
    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()
    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Attendance Records',type=type3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()
    st.divider()
    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()
    footer_dashboard()
def teacher_tab_take_attendance():
    st.header("Take AI Attendance")
def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header("Manage Subjects")
    with col2:
        if st.button(
            "Create New Subject",
            use_container_width=True
        ):
            create_subject_dialog(teacher_id)
    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.info("No Subject Found! Create One.")
        return
    for idx, sub in enumerate(subjects):
        stats = [
            ("🙋", "Students", sub["total_students"]),
            ("⏱️", "Classes", sub["total_classes"]),
        ]
        def share_btn(
            name=sub["name"],
            code=sub["subject_code"],
            index=idx
        ):
            if st.button(
                f"Share Code: {name}",
                key=f"share_{code}",
                icon=":material/share:"
            ):
                share_subject_dialog(name, code)
        subject_card(
            name=sub["name"],
            code=sub["subject_code"],
            section=sub["section"],
            stats=stats,
            footer_callback=share_btn
        )
        st.write("")
def teacher_tab_attendance_records():
    st.header("Attendance Records")
def login_teacher(username,password):
    if not username or not password:
        st.error("Please enter both username and password!")
        return False
    success, teacher = teacher_login(username, password)
    if success:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False
def teacher_screen_login():
    c1, c2 = st.columns(2)
    with c1:
        header_dashboard()
    with c2:
        if st.button(
            'Go back to Home',
            type='secondary',
            key='loginbackbtn1'
        ):
            st.session_state['login_type'] = None
            st.rerun()
    st.header('Login using password')
    st.write("")
    st.write("")
    teacher_username = st.text_input(
        'Enter Username',
        placeholder='name123'
    )
    teacher_pass = st.text_input(
        'Enter Password',
        placeholder='********',
        type='password'
    )
    st.divider()
    btnc1, btnc2 = st.columns(2)
    with btnc1:
        if st.button(
            'Login',
            icon=':material/passkey:',
            use_container_width=True
        ):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("Welcome back!", icon="👋")
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error("Invalid username or password!")
    with btnc2:
        if st.button(
            'Register Instead',
            type='primary',
            icon=':material/passkey:',
            use_container_width=True
        ):
            st.session_state['teacher_login_type'] = 'register'
            st.rerun()
    footer_dashboard()
def register_teacher(
    teacher_username,
    teacher_pass,
    teacher_name,
    teacher_pass_confirm
):
    if not teacher_username or not teacher_pass or not teacher_name or not teacher_pass_confirm:
        return False, "All fields are required!"
    if check_teacher_exist(teacher_username):
        return False, "Username already exists!"
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords do not match!"
    try:
        create_teacher(
            teacher_username,
            teacher_pass,
            teacher_name
        )
        return True, "Successfully registered! Please login now."
    except Exception as e:
        return False, "Unexpected error occurred during registration!"
def teacher_screen_register():
    c1, c2 = st.columns(2)
    with c1:
        header_dashboard()
    with c2:
        if st.button(
            'Go back to Home',
            type='secondary',
            key='registerbackbtn'
        ):
            st.session_state['login_type'] = None
            st.rerun()
    st.header('Register your teacher profile')
    st.write("")
    st.write("")
    teacher_username = st.text_input(
        'Enter Username',
        placeholder='name123'
    )
    teacher_name = st.text_input(
        'Enter Name',
        placeholder='John Doe'
    )
    teacher_pass = st.text_input(
        'Enter Password',
        placeholder='********',
        type='password'
    )
    teacher_pass_confirm = st.text_input(
        'Confirm your password',
        placeholder='********',
        type='password'
    )
    st.divider()
    btnc1, btnc2 = st.columns(2)
    with btnc1:
        if st.button(
            'Register now',
            icon=':material/passkey:',
            use_container_width=True
        ):
            success, message = register_teacher(
                teacher_username,
                teacher_pass,
                teacher_name,
                teacher_pass_confirm
            )
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state['teacher_login_type'] = 'login'
                st.rerun()
            else:
                st.error(message)
    with btnc2:
        if st.button(
            'Login Instead',
            type='primary',
            icon=':material/passkey:',
            use_container_width=True
        ):
            st.session_state['teacher_login_type'] = 'login'
            st.rerun()
    footer_dashboard()