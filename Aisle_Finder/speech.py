import sounddevice as sd
import numpy as np
import wave
import tempfile
import requests
import os

# Set your Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Manually set the correct microphone index
MIC_INDEX = 2  # Change this based on your working microphone

def record_audio(filename="audio.wav", duration=5, samplerate=16000):
    """Records audio from a specific microphone and saves it as a WAV file."""
    print(f"🎤 Listening... (Using mic index {MIC_INDEX})")

    try:
        # Capture audio using the correct microphone
        audio_data = sd.rec(int(samplerate * duration), samplerate=samplerate,
                            channels=1, dtype=np.int16, device=MIC_INDEX)
        sd.wait()  # Wait for recording to finish
        print("🔊 Audio recorded successfully.")

        # Save audio to a WAV file
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(samplerate)
            wf.writeframes(audio_data.tobytes())

        return filename
    except Exception as e:
        print(f"❌ Error recording audio: {e}")
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
    """Records audio and transcribes it using Groq's Whisper API."""
    audio_file = record_audio()
    if not audio_file:
        return "❌ Audio recording failed."

    text = transcribe_audio(audio_file)
    os.remove(audio_file)  # Delete temp file
    print(f"✅ You said: {text}")
    return text
