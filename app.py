import streamlit as st
from gtts import gTTS
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

st.set_page_config(page_title="🎧 G-ma's Audiobook Maker", layout="centered")
st.title("🎧 G-ma's Audiobook Maker")
st.markdown("Upload your book or paste your story below to create an audiobook!")

# 📂 File uploader
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
story_text = st.text_area("✍️ You can still edit your story below:", story_text, height=500)
language = st.selectbox("🌍 Language", ["en", "es", "fr", "de", "it"])
speed = st.radio("🚗 Speed", ["Normal", "Slow"])
is_slow = speed == "Slow"

# TTS generator
if st.button("🎙️ Generate Audiobook"):
    if not story_text.strip():
        st.warning("Please upload a file or paste story text.")
    else:
        st.info("Splitting and generating audio. Please be patient...")

        chunks = textwrap.wrap(story_text, width=1200, break_long_words=False, replace_whitespace=False)
        progress_bar = st.progress(0)
        audio_bytes = b""
        skipped_chunks = 0

        def contains_image_data(text):
            return (
                "data:image" in text.lower() or
                "<img" in text.lower() or
                re.search(r"[A-Za-z0-9+/=]{500,}", text)
            )

        for i, chunk in enumerate(chunks):
            if contains_image_data(chunk):
                skipped_chunks += 1
                progress_bar.progress((i + 1) / len(chunks))
                continue

            try:
                tts = gTTS(text=chunk, lang=language, slow=is_slow)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tts.save(tmp.name)
                    audio_bytes += open(tmp.name, "rb").read()
                    os.remove(tmp.name)
                time.sleep(1.5)
            except Exception as e:
                st.error(f"❌ Error processing chunk {i+1}: {e}")
                break

            progress_bar.progress((i + 1) / len(chunks))

        if audio_bytes:
            st.success("✅ Audiobook is ready!")
            if skipped_chunks > 0:
                st.warning(f"⚠️ Skipped {skipped_chunks} chunk(s) due to images or invalid data.")

            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                label="⬇️ Download MP3",
                data=audio_bytes,
                file_name=f"{book_title.replace(' ', '_')}.mp3",
                mime="audio/mp3"
            )
