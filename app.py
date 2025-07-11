import streamlit as st
import requests
import tempfile
import os
import textwrap
import time
import re

try:
    import docx
except ImportError:
    import subprocess
    subprocess.call(['pip', 'install', 'python-docx'])
    import docx

# -- Settings --
st.set_page_config(page_title="🎧 G-ma's Audiobook Maker", layout="centered")
ELEVEN_API_KEY = st.secrets["ELEVEN_API_KEY"]  # Store your key in .streamlit/secrets.toml

# -- UI --
st.title("🎧 G-ma's Audiobook Maker with ElevenLabs")
st.markdown("Upload a book or paste text to generate ultra-realistic audiobooks.")

# File upload
uploaded_file = st.file_uploader("📄 Upload .txt or .docx", type=["txt", "docx"])
story_text = ""

if uploaded_file:
    if uploaded_file.type == "text/plain":
        story_text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        story_text = "\n".join([para.text for para in doc.paragraphs])
    else:
        st.error("Unsupported file format.")

# Inputs
book_title = st.text_input("📘 Book Title", "My Story")
story_text = st.text_area("✍️ You can edit your story below:", story_text, height=500)

# Fetch voices from ElevenLabs
headers = {"xi-api-key": ELEVEN_API_KEY}
voices_resp = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)
voice_list = voices_resp.json().get("voices", [])
voice_names = [v["name"] for v in voice_list]
voice_id_map = {v["name"]: v["voice_id"] for v in voice_list}

voice_choice = st.selectbox("🎤 Choose a voice", voice_names or ["Rachel"])
selected_voice_id = voice_id_map.get(voice_choice, "EXAVITQu4vr4xnSDxMaL")

# Generate button
if st.button("🎙️ Generate Audiobook"):
    if not story_text.strip():
        st.warning("Please upload a file or paste story text.")
    else:
        st.info("Generating with ElevenLabs...")

        # Chunk large text if necessary
        chunks = textwrap.wrap(story_text, width=2000, break_long_words=False, replace_whitespace=False)
        audio_bytes = b""
        progress_bar = st.progress(0)

        for i, chunk in enumerate(chunks):
            try:
                response = requests.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{selected_voice_id}",
                    headers={
                        "xi-api-key": ELEVEN_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": chunk,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    }
                )
                response.raise_for_status()
                audio_bytes += response.content
                time.sleep(1)
            except Exception as e:
                st.error(f"Error on chunk {i+1}: {e}")
                break

            progress_bar.progress((i + 1) / len(chunks))

        # Play + download
        if audio_bytes:
            st.success("✅ Audiobook is ready!")
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                label="⬇️ Download MP3",
                data=audio_bytes,
                file_name=f"{book_title.replace(' ', '_')}.mp3",
                mime="audio/mp3"
            )
