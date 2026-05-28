import io
import librosa
import numpy as np
import streamlit as st

from resemblyzer import (
    VoiceEncoder,
    preprocess_wav
)

@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()


def get_voice_embedding(audio_bytes):

    try:

        encoder = load_voice_encoder()

        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000
        )

        wav = preprocess_wav(audio, sr)

        embedding = encoder.embed_utterance(wav)

        return embedding.tolist()

    except Exception as e:

        st.error(
            f"Voice Error: {e}"
        )

        return None


def identify_speaker(
    new_embedding,
    candidates_dict,
    threshold=0.65
):

    try:

        if new_embedding is None:
            return None, 0

        best_sid = None
        best_score = -1

        new_embedding = np.array(new_embedding)

        for sid, stored_embedding in candidates_dict.items():

            if stored_embedding is None:
                continue

            stored_embedding = np.array(stored_embedding)

            similarity = np.dot(
                new_embedding,
                stored_embedding
            ) / (
                np.linalg.norm(new_embedding)
                * np.linalg.norm(stored_embedding)
            )

            if similarity > best_score:

                best_score = similarity
                best_sid = sid

        if best_score >= threshold:
            return best_sid, best_score

        return None, best_score

    except Exception as e:

        st.error(
            f"Speaker Error: {e}"
        )

        return None, 0