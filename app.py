import streamlit as st
from gtts import gTTS
import tempfile

st.set_page_config(page_title="🎧 G-ma's Audiobook Maker", layout="centered")

st.title("🎧 G-ma's Audiobook Maker")
st.markdown("Type or paste your story below, and create your own audiobook!")

# Input fields
book_title = st.text_input("📘 Book Title", "My Story")
story_text = st.text_area("✍️ Your Story", height=300)

language = st.selectbox("🌍 Language", ["en", "es", "fr", "de", "it"])
speed = st.radio("🚗 Speed", ["Normal", "Slow"])
is_slow = True if speed == "Slow" else False

# Generate button
if st.button("🎙️ Generate Audiobook"):
    if not story_text.strip():
        st.warning("Please write something first!")
    else:
        st.info("Generating audio...")

        # Generate with gTTS
        tts = gTTS(text=story_text, lang=language, slow=is_slow)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            audio_data = open(tmp_file.name, "rb").read()

        st.success("✅ Audiobook ready!")
        st.audio(audio_data, format='audio/mp3')

        st.download_button(
            label="⬇️ Download MP3",
            data=audio_data,
            file_name=f"{book_title.replace(' ', '_')}.mp3",
            mime="audio/mp3"
        )
