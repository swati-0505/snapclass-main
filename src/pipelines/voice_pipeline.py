import resemblyzer
from resemblyzer import VoiceEncoder, preprocess_wav
import io
import librosa
import streamlit as st
import numpy as np

@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()
def get_voice_embedding(audio_file):
    try:
        encoder=load_voice_encoder()
        audio,sr=librosa.load(io.BytesIO(audio_file.read()), sr=16000)
        wav=preprocess_wav(audio, sr)
        embedding=encoder.embed_utterance(wav)
        return embedding.tolist()
    except Exception as e:
        st.error(f"Error processing audio file: {e}")
        return None
    
def identify_speaker(new_embedding,candidates_dict,threshold=0.65):
    if new_embedding is None or not candidates_dict:
        return "Error processing audio"
    best_sid=None
    best_score=-1.0
    for sid,stored_embedding in candidates_dict.items():
        if stored_embedding:
            similarity=np.dot()
            if similarity > best_score:
                best_score=similarity
                best_sid=sid
    if best_score >= threshold:
        return best_sid, best_score
    return None, best_score

def process_bulk_audio(audio_bytes,candidates_dict,threshold=0.65):
    try:
        encoder=load_voice_encoder()
        audio,sr=librosa.load(io.BytesIO(audio_bytes),sr=16000)
        segments=librosa.effects.split(audio,top_dp=30)
        identify_results={}
        for start,end in segments:
            if (end-start)<sr*0.5:
                continue
            segment_audio=audio[start:end]
            wav=preprocess_wav(segment_audio)
            embedding=encoder.embed_utterance(wav)
            sid,score=identify_speaker(embedding,candidates_dict,threshold)

            if sid:
                if sid not in identify_results or score > identify_results[sid]:
                    identify_results[sid]=score
        return identify_results
    except Exception as e:
        st.error(f"Error processing audio file: {e}")
        return {}
