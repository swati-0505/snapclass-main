import time
import cv2
import os
import streamlit as st
from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout
)
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import (
    predict_attendance,
    get_face_embedding,
    train_classifier
)
from src.pipelines.voice_pipeline import (
    get_voice_embedding
)
from src.database.db import (
    get_all_students,
    create_student
)
def student_dashboard():
    st.header("Welcome to your Dashboard!")
def student_screen():
    style_background_dashboard()
    style_base_layout()
    if "student_data" in st.session_state:
        student_dashboard()
        return
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
    st.header("Login using FaceID")
    st.write("")
    st.write("")
    show_registration = False
    photo_source = st.camera_input(
        "Position your face in the center"
    )
    uploaded_file = st.file_uploader(
        "Or upload from gallery",
        type=["jpg", "jpeg", "png"]
    )
    img = None
    if photo_source:
        img = np.array(
            Image.open(photo_source).convert('RGB')
        )
    elif uploaded_file:
        img = np.array(
            Image.open(uploaded_file).convert('RGB')
        )
    if photo_source or uploaded_file:
        with st.spinner("Processing..."):
            detected, all_ids, num_faces = predict_attendance(img)
            if num_faces == 0:
                st.error(
                    "No face detected. Please try again."
                )
                show_registration = True
            elif num_faces > 1:
                st.error(
                    "Multiple faces detected. Please ensure only one face is visible."
                )
            else:
                if detected:
                    student_id = list(
                        detected.keys()
                    )[0]
                    all_students = get_all_students()
                    student = next(
                        (
                            s for s in all_students
                            if s["student_id"] == student_id
                        ),
                        None
                    )
                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student

                        st.toast(
                            f"Welcome, {student['name']}!",
                            icon="👋"
                        )
                        time.sleep(2)
                        st.rerun()
                else:
                    st.info(
                        "Face not recognized. You might be a new student!"
                    )
                    show_registration = True
    if show_registration:
        with st.container(border=True):
            st.header(
                "Don't have an account? Register here!"
            )
            new_name = st.text_input(
                "Enter your name",
                placeholder='E.g. John Doe'
            )
            st.subheader(
                "Optional: Voice Enrollment"
            )
            st.info(
                "Enroll your voice for voice only attendance"
            )
            audio_data = None
            try:
                audio_data = st.audio_input(
                    "Record your voice for enrollment like: I am Present, My name is Alice!"
                )
            except Exception:
                st.error(
                    "Audio Data Failed!"
                )
            if st.button(
                'Create Account',
                type='primary'
            ):
                if new_name:
                    with st.spinner(
                        "Creating your Profile..."
                    ):
                        encodings = get_face_embedding(img)
                        if encodings:
                            face_emb = encodings[0].tolist()
                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(
                                    audio_data
                                )
                            response_data = create_student(
                                new_name,
                                face_embedding=face_emb,
                                voice_embedding=voice_emb
                            )
                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(
                                    f"Profile Created! Hi {new_name}!",
                                    icon="👋"
                                )
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(
                                    "Failed to create profile."
                                )
                        else:
                            st.error(
                                "Face encoding failed. Please try again with a clearer photo."
                            )
                else:
                    st.warning(
                        "Enter your name!"
                    )
    footer_dashboard()