import time
import cv2
import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.dialog_enroll import enroll_dialog
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import (
    predict_attendance,
    get_face_embedding,
    train_classifier
)
from src.pipelines.voice_pipeline import get_voice_embedding
from src.components.subject_card import subject_card
from src.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,unenroll_student_to_subject
)
def student_dashboard():
        student_data = st.session_state.student_data
        student_id=student_data['student_id']
        c1, c2 = st.columns(2)
        with c1:
            header_dashboard()
        with c2:
            st.subheader(f"Welcome, {student_data['name']}!")
            if st.button(
                'Logout',
                type='secondary',
                key='loginbackbtn'
            ):
                st.session_state['is_logged_in'] = False
                del st.session_state['student_data']
                st.rerun()
        st.space()

        c1,c2=st.columns(2)
        with c1:
            st.header('Your Enrolled Subject')
        with c2:
            if st.button('Enroll in Subject',type='primary',use_container_width=True):
                enroll_dialog()

        st.divider()
        with st.spinner('Loading your enrolled subjects..'):
            subjects = get_student_subjects(student_id)
            logs = get_student_attendance(student_id)
        stats_map = {}    
        for log in logs:
            sid = log['subject_id']
            if sid not in stats_map:
                stats_map[sid] = {"total":0, "attended": 0}
            stats_map[sid]['total'] +=1
            if log.get('is_present'):
                stats_map[sid]['attended'] += 1
        cols = st.columns(2)
        for i, sub_node in enumerate(subjects):
            sub = sub_node['subjects']
            sid = sub['subject_id']
            stats = stats_map.get(sid,{"total":0, "attended": 0} )
            def unenroll_button():
                    if st.button("Unenroll from tihs course", key=f"unenroll_{student_id}_{sub['subject_code']}_{i}", type='tertiary', width='stretch', icon=':material/delete_forever:'):
                        unenroll_student_to_subject(student_id, sid)
                        st.toast(f"Unenrolled from {sub['name']} successfully!")
                        st.rerun()
            with cols[i % 2]:
                subject_card(
                    name = sub['name'],
                    code =sub['subject_code'],
                    section = sub['section'],
                    stats = [
                        ('📅', 'Total', stats['total']),
                        ('✅', 'Attended', stats['attended'])
                    ],
                    footer_callback=unenroll_button
            )
        footer_dashboard()
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
            "Go back to Home",
            type="secondary",
            key="loginbackbtn"
        ):
            st.session_state["login_type"] = None
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
        try:
            img = np.array(
                Image.open(photo_source).convert("RGB")
            )
            img = cv2.cvtColor(
                img,
                cv2.COLOR_RGB2BGR
            )
        except Exception as e:
            st.error(
                f"Camera Error: {e}"
            )
    elif uploaded_file:
        try:
            img = np.array(
                Image.open(uploaded_file).convert("RGB")
            )
            img = cv2.cvtColor(
                img,
                cv2.COLOR_RGB2BGR
            )
        except Exception as e:
            st.error(
                f"Upload Error: {e}"
            )
    if img is not None:
        with st.spinner("Processing Face..."):
            try:
                detected, all_ids, num_faces = predict_attendance(img)
                if num_faces == 0:
                    st.error(
                        "No face detected. Please try again."
                    )
                    show_registration = True
                elif num_faces > 1:
                    st.error(
                        "Multiple faces detected."
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
                            st.session_state.user_role = "student"
                            st.session_state.student_data = student
                            st.success(
                                f"Welcome {student['name']}!"
                            )
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.info(
                            "Face not recognized. Register below."
                        )
                        show_registration = True
            except Exception as e:
                st.error(
                    f"Face Processing Error: {e}"
                )
                show_registration = True
    if show_registration:
        with st.container(border=True):
            st.header(
                "Don't have an account? Register here!"
            )
            new_name = st.text_input(
                "Enter your name",
                placeholder="E.g. John Doe"
            )
            st.subheader(
                "Voice Enrollment"
            )
            st.info(
                "Record your voice for voice attendance."
            )
            audio_data = None
            try:
                audio_data = st.audio_input(
                    "Record your voice"
                )
            except Exception as e:
                st.warning(
                    f"Audio Error: {e}"
                )
            if st.button(
                "Create Account",
                type="primary"
            ):
                if not new_name:
                    st.warning(
                        "Please enter your name."
                    )
                elif img is None:
                    st.warning(
                        "Please upload face image."
                    )
                else:
                    with st.spinner(
                        "Creating Profile..."
                    ):
                        try:
                            # FACE EMBEDDING
                            encodings = get_face_embedding(img)
                            if not encodings:
                                st.error(
                                    "Face encoding failed. Use clearer image."
                                )
                            else:
                                face_emb = encodings[0].tolist()
                                voice_emb = None
                                # VOICE EMBEDDING
                                if audio_data is not None:
                                    try:
                                        audio_bytes = audio_data.read()
                                        if audio_bytes:
                                            voice_emb = get_voice_embedding(
                                                audio_bytes
                                            )
                                    except Exception as e:
                                        st.warning(
                                            f"Voice skipped: {e}"
                                        )
                                response_data = create_student(
                                    new_name,
                                    face_emb,
                                    voice_emb
                                )
                                try:
                                    train_classifier()
                                except Exception as e:
                                    st.warning(
                                        f"Training skipped: {e}"
                                    )
                                if response_data:
                                    st.session_state.is_logged_in = True
                                    st.session_state.user_role = "student"
                                    st.session_state.student_data = response_data[0]
                                    st.success(
                                        f"Profile Created Successfully!"
                                    )
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(
                                        "Database save failed."
                                    )
                        except Exception as e:
                            st.error(
                                f"Registration Error: {e}"
                            )
    footer_dashboard()
