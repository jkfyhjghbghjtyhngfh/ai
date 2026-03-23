import requests
import json
import re
import pyttsx3
import threading

OLLAMA_URL = "http://localhost:11434/api/generate"

# ---------- TTS (shared engine = faster) ----------
engine = pyttsx3.init()
engine.setProperty('rate', 170)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def clean(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

def speak_async(text):
    def run():
        text_clean = clean(text)
        engine.say(text_clean)
        engine.runAndWait()

    threading.Thread(target=run, daemon=True).start()

# ---------- STREAM + SPEAK WHILE GENERATING ----------
def ask_ollama_stream_speaking(prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": "gemma3:1b",
        "prompt": "NO emojis. Be short.\n\nUser: " + prompt,
        "stream": True
    }, stream=True)

    buffer = ""
    full = ""

    print("AI: ", end="", flush=True)

    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            chunk = data.get("response", "")

            print(chunk, end="", flush=True)
            full += chunk
            buffer += chunk

            # Speak when we hit sentence endings
            if any(p in buffer for p in [".", "!", "?"]):
                speak_async(buffer)
                buffer = ""

    # speak leftover
    if buffer.strip():
        speak_async(buffer)

    print()
    return full