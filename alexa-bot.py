import pyttsx3
import requests
import json
import re
import os
import sys
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
RAW_URL = "https://raw.githubusercontent.com/jkfyhjghbghjtyhngfh/ai/main/alexa-bot.py"
SELF_FILE = os.path.abspath(__file__)

# ---------- CLEAN ----------
def clean(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# ---------- TTS (SINGLE ENGINE) ----------
engine = pyttsx3.init()
engine.setProperty('rate', 170)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    text = clean(text)
    if text.strip():
        engine.say(text)
        engine.runAndWait()

# ---------- STREAM + SPEAK IN CHUNKS ----------
def ask_ollama_stream(prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": "gemma3:1b",
        "prompt": "No emojis. Give clear answers.\n\nUser: " + prompt,
        "stream": True,
        "options": {"num_predict": 400}
    }, stream=True)

    print("AI: ", end="", flush=True)

    buffer = ""

    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            chunk = data.get("response", "")

            print(chunk, end="", flush=True)
            buffer += chunk

            # 🔥 Speak every ~8–12 words (NOT per word)
            words = buffer.split()

            if len(words) >= 10:
                speak(" ".join(words))
                buffer = ""

    # flush remaining text
    if buffer.strip():
        speak(buffer)

    print()

# ---------- UPDATE ----------
def update_self():
    print("Updating...")
    r = requests.get(RAW_URL)
    code = r.text

    if code.strip():
        with open(SELF_FILE, "w", encoding="utf-8") as f:
            f.write(code)

        print("Restarting...")
        os.execv(sys.executable, [sys.executable, SELF_FILE])

# ---------- MAIN ----------
print("Type: hey assistant <message>")

while True:
    text = input("You: ").lower()

    if text == "exit":
        break

    if text.startswith("hey assistant"):
        cmd = text.replace("hey assistant", "").strip()

        if not cmd:
            speak("yes")
            continue

        if cmd == "/update":
            update_self()
            continue

        ask_ollama_stream(cmd)

print("Press Enter to close...")
input()