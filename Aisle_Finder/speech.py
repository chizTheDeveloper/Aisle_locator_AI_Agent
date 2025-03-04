import speech_recognition as sr
import numpy as np
import wave
import tempfile
import requests
import os

# Set your Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Manually set the correct microphone index
MIC_INDEX = 2  # Change this based on your working microphone

def record_audio():
    """Records audio from the default microphone and returns transcribed text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"📝 Recognized text: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio.")
        return None
    except sr.RequestError:
        print("❌ Could not request results, check internet connection.")
        return None

def transcribe_audio(filename):
    """Sends recorded audio to Groq's Whisper model for transcription."""
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}

    files = {"file": open(filename, "rb")}
    data = {"model": "whisper-large-v3", "language": "en"}

    response = requests.post(url, headers=headers, files=files, data=data)
    result = response.json()

    print("Groq API Response:", result)

    if "text" in result:
        return result["text"]
    else:
        return "❌ Error: Could not transcribe speech."

def get_voice_input():
    """Records audio using speech_recognition and transcribes it using Groq's Whisper API."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)

    # Save the audio to a temporary file (needed for Whisper API)
    temp_filename = "temp_audio.wav"
    with open(temp_filename, "wb") as f:
        f.write(audio.get_wav_data())

    # Transcribe using Groq Whisper API
    text = transcribe_audio(temp_filename)

    # Clean up temp file
    os.remove(temp_filename)

    print(f"✅ You said: {text}")
    return text
