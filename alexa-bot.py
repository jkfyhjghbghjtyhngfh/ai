import requests
import json
import re
import os
import sys
import time

import pyttsx3

# ---------- CONFIG ----------
OLLAMA_URL = "http://localhost:11434/api/generate"
SELF_FILE = os.path.abspath(__file__)

# ---------- TTS ----------
engine = pyttsx3.init()
engine.setProperty('rate', 170)

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    if text.strip():
        engine.say(text)
        engine.runAndWait()

# ---------- ASK AI (NO STREAMING) ----------
def ask_ollama(prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": "gemma3:1b",
        "prompt": "No emojis. Respond clearly.\n\nUser: " + prompt,
        "stream": False
    })

    data = response.json()
    return data.get("response", "")

# ---------- UPDATE ----------
def update_self():
    url = "https://raw.githubusercontent.com/jkfyhjghbghjtyhngfh/ai/main/alexa-bot.py"

    print("Updating...")
    r = requests.get(url)

    if r.text.strip():
        with open(SELF_FILE, "w", encoding="utf-8") as f:
            f.write(r.text)

        print("Restarting...")
        os.execv(sys.executable, [sys.executable, SELF_FILE])

# ---------- MAIN ----------
print("Type: hey assistant <message>")

while True:
    text = input("You: ").strip().lower()

    if text == "exit":
        break

    if text.startswith("hey assistant"):
        cmd = text.replace("hey assistant", "").strip()

        if not cmd:
            speak("Yes")
            continue

        if cmd == "/update":
            update_self()
            continue

        print("AI thinking...")

        reply = ask_ollama(cmd)

        print("AI:", reply)

        speak(reply)

print("Press Enter to close...")
input()