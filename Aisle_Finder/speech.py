import streamlit as st
import speech_recognition as sr

def get_voice_input():
    """Captures voice input and converts it to text."""
    recognizer = sr.Recognizer()

    mic_index = 2  # Change this to another index from the list
    with sr.Microphone(device_index=mic_index) as source:
        st.write("🎤 Listening... Speak now")

        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=2)

        # Increase pause threshold to allow natural pauses
        recognizer.pause_threshold = 2.0  # Wait longer before stopping

        try:
            audio = recognizer.listen(source)  # Removed timeout to wait indefinitely
            st.write("🔊 Audio received. Processing...")
        except sr.WaitTimeoutError:
            return "❌ Timeout: No speech detected."

    try:
        item_name = recognizer.recognize_google(audio)
        st.write(f"✅ You said: {item_name}")
        return item_name
    except sr.UnknownValueError:
        return "❌ Sorry, I couldn't understand that."
    except sr.RequestError:
        return "❌ API request error. Check internet connection."

# Streamlit App
st.title("🎤 Speech-to-Text with Streamlit")

if st.button("Start Recording"):
    result = get_voice_input()
    st.write("Result:", result)