import streamlit as st
from gtts import gTTS
import tempfile
import os
import textwrap

st.set_page_config(page_title="🎧 G-ma's Audiobook Maker", layout="centered")

st.title("🎧 G-ma's Audiobook Maker")
st.markdown("Paste your full book and this tool will break it up into an audiobook automatically!")

# Input fields
book_title = st.text_input("📘 Book Title", "My Story")
story_text = st.text_area("✍️ Paste your entire story here:", height=500)
language = st.selectbox("🌍 Language", ["en", "es", "fr", "de", "it"])
speed = st.radio("🚗 Speed", ["Normal", "Slow"])
is_slow = speed == "Slow"

# Generate
if st.button("🎙️ Generate Audiobook"):
    if not story_text.strip():
        st.warning("Please paste your book content.")
    else:
        st.info("Splitting and generating audio. Please be patient...")

        chunks = textwrap.wrap(story_text, width=1200, break_long_words=False, replace_whitespace=False)

        progress_bar = st.progress(0)
        audio_bytes = b""

        for i, chunk in enumerate(chunks):
            try:
                tts = gTTS(text=chunk, lang=language, slow=is_slow)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tts.save(tmp.name)
                    audio_bytes += open(tmp.name, "rb").read()
                    os.remove(tmp.name)
            except Exception as e:
                st.error(f"Error processing chunk {i+1}: {e}")
                break

            progress_bar.progress((i + 1) / len(chunks))

        st.success("✅ Audiobook is ready!")
        st.audio(audio_bytes, format="audio/mp3")
        st.download_button(
            label="⬇️ Download MP3",
            data=audio_bytes,
            file_name=f"{book_title.replace(' ', '_')}.mp3",
            mime="audio/mp3"
        )
