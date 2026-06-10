import anthropic
import speech_recognition as sr
import datetime
import sys
import asyncio
import edge_tts
import tempfile
import os
import subprocess

# ── CONFIG ──────────────────────────────────────────
API_KEY = "YOUR_API_KEY_HERE"   # <-- your key here
# ────────────────────────────────────────────────────

client = anthropic.Anthropic(api_key=API_KEY)
history = []

async def speak_async(text):
    voice = "en-GB-RyanNeural"
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tmp = f.name
    await communicate.save(tmp)
    subprocess.call(["powershell", "-c", f"Add-Type -AssemblyName presentationCore; $mp = New-Object System.Windows.Media.MediaPlayer; $mp.Open('{tmp}'); $mp.Play(); Start-Sleep 7"], shell=False)
    os.unlink(tmp)

def speak(text):
    print(f"\n  [J.A.R.V.I.S]: {text}\n")
    try:
        asyncio.run(speak_async(text))
    except Exception as e:
        print(f"  [AUDIO ERROR]: {e}")

def listen():
    import sounddevice as sd
    import io
    import wave
    recognizer = sr.Recognizer()
    print("  [LISTENING...] Speak now, sir.")
    try:
        duration = 5
        fs = 16000
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(recording.tobytes())
        buf.seek(0)
        with sr.AudioFile(buf) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        print(f"  [YOU]: {text}")
        return text
    except Exception as e:
        print(f"  [MIC ERROR]: {e}")
        return None

def ask_jarvis(user_input):
    history.append({"role": "user", "content": user_input})
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=300,
        system="""You are J.A.R.V.I.S (Just A Rather Very Intelligent System), 
Tony Stark's AI assistant. Speak in a calm, intelligent British tone. 
Occasionally address the user as 'sir'. Be concise under 80 words.""",
        messages=history
    )
    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    return reply

def banner():
    print("""
  ╔══════════════════════════════════════════╗
  ║         J . A . R . V . I . S           ║
  ║   Just A Rather Very Intelligent System  ║
  ║           Python Terminal v1.0           ║
  ╚══════════════════════════════════════════╝
    """)
    now = datetime.datetime.now()
    print(f"  Time : {now.strftime('%H:%M:%S')}  |  {now.strftime('%A, %d %B %Y')}")
    print("\n  Type your message and press Enter")
    print("  Type 'voice' to use microphone")
    print("  Type 'quit' to shut down")
    print("  " + "─"*42 + "\n")

def main():
    banner()
    speak("Good day sir. J.A.R.V.I.S is now online. All systems operational.")
    while True:
        try:
            user_input = input("  [YOU] > ").strip()
            if not user_input:
                continue
            if user_input.lower() == 'quit':
                speak("Shutting down. Goodbye sir.")
                sys.exit()
            elif user_input.lower() == 'voice':
                user_input = listen()
                if not user_input:
                    continue
            print("  [THINKING...]")
            reply = ask_jarvis(user_input)
            speak(reply)
        except KeyboardInterrupt:
            speak("Shutting down. Goodbye sir.")
            sys.exit()

if __name__ == "__main__":
    main()
