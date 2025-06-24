import streamlit as st
from gtts import gTTS
import tempfile
import os
from pydub import AudioSegment
import textwrap

st.set_page_config(page_title="🎧 G-ma's Audiobook Maker", layout="centered")

st.title("🎧 G-ma's Audiobook Maker")
st.markdown("Paste your full book and this tool will break it up into an audiobook automatically!")

# Input fields
book_title = st.text_input("📘 Book Title", "My Story")
story_text = st.text_area("✍️ Paste your entire story here:", height=500)
language = st.selectbox("🌍 Language", ["en", "es", "fr", "de", "it"])
speed = st.radio("🚗 Speed", ["Normal", "Slow"])
is_slow = True if speed == "Slow" else False

# Generate button
if st.button("🎙️ Generate Audiobook"):
    if not story_text.strip():
        st.warning("Please paste your book content.")
    else:
        st.info("Splitting book into parts...")

        # Split into chunks (~1000–1500 characters)
        chunks = textwrap.wrap(story_text, width=1200, break_long_words=False, replace_whitespace=False)

        full_audio = AudioSegment.silent(duration=1000)  # 1s silence start
        st.info(f"Generating {len(chunks)} audio chunks. Please wait...")

        for i, chunk in enumerate(chunks):
            tts = gTTS(text=chunk, lang=language, slow=is_slow)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                tts.save(temp_file.name)
                audio_chunk = AudioSegment.from_mp3(temp_file.name)
                full_audio += audio_chunk + AudioSegment.silent(duration=500)
                os.remove(temp_file.name)
            st.progress((i + 1) / len(chunks))

        # Save final file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as final_audio_file:
            full_audio.export(final_audio_file.name, format="mp3")
            audio_data = open(final_audio_file.name, "rb").read()

        st.success("✅ Audiobook is ready!")
        st.audio(audio_data, format="audio/mp3")
        st.download_button(
            label="⬇️ Download Audiobook",
            data=audio_data,
            file_name=f"{book_title.replace(' ', '_')}.mp3",
            mime="audio/mp3"
        )
