import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import check_teacher_exist, create_teacher, teacher_login

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
    st.header(f"Welcome, {teacher_data['name']}!")

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
            key='loginbackbtn'
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