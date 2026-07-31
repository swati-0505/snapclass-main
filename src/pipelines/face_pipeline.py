import numpy as np
import dlib
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st
from src.database.db import get_all_students
@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )
    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )
    return detector, sp, facerec
def get_face_embedding(image_np):
    try:
        detector, sp, facerec = load_dlib_models()
        faces = detector(image_np, 1)
        encodings = []
        for face in faces:
            shape = sp(image_np, face)
            face_descriptor = facerec.compute_face_descriptor(
                image_np,
                shape,
                1
            )
            encodings.append(
                np.array(face_descriptor)
            )
        return encodings
    except Exception as e:
        st.error(
            f"Face Embedding Error: {e}"
        )
        return []
@st.cache_resource
def get_trained_model():
    try:
        X = []
        y = []
        student_db = get_all_students()
        if not student_db:
            return None
        for student in student_db:
            embedding = student.get(
                "face_embedding"
            )
            if embedding:
                X.append(
                    np.array(embedding)
                )
                y.append(
                    student.get("student_id")
                )
        if len(X) == 0:
            return None
        if len(set(y)) < 2:
            return {
                "clf": None,
                "X": X,
                "y": y
            }
        clf = SVC(
            kernel="linear",
            probability=True,
            class_weight="balanced"
        )
        clf.fit(X, y)
        return {
            "clf": clf,
            "X": X,
            "y": y
        }
    except Exception as e:
        st.error(
            f"Training Error: {e}"
        )
        return None
def train_classifier():
    try:
        st.cache_resource.clear()
        model_data = get_trained_model()
        return bool(model_data)
    except Exception as e:
        st.error(
            f"Classifier Error: {e}"
        )
        return False
def predict_attendance(class_image_np):
    try:
        encodings = get_face_embedding(
            class_image_np
        )
        detected_student = {}
        model_data = get_trained_model()
        if not model_data:
            return {}, [], 0
        X_train = model_data["X"]
        y_train = model_data["y"]
        all_students = sorted(
            set(y_train)
        )
        resemblance_threshold = 0.6
        for encoding in encodings:
            distances=[np.linalg.norm(np.array(x)-encoding) for x in X_train]
            best_idx=int(np.argmin(distances))
            best_distance=distances[best_idx]
            if best_distance < resemblance_threshold:
                predicted_id=int(y_train[best_idx])
                detected_student[predicted_id] = True
        return (
            detected_student,
            all_students,
            len(encodings)
        )
    except Exception as e:
        st.error(
            f"Prediction Error: {e}"
        )
        return {}, [], 0