import requests
import json
import re
import os
import sys

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
    text = re.sub(r'[^\x00-\x7F]+', '', str(text))
    if text.strip():
        print("Bot:", text)
        engine.say(text)
        engine.runAndWait()

# ---------- AI ----------
def ask_ollama(prompt):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "gemma3:1b",
            "prompt": "No emojis. Be short and clear.\n\nUser: " + prompt,
            "stream": False
        })

        data = response.json()
        return data.get("response", "")
    except:
        return "AI error."

# ---------- SELF UPDATE ----------
def update_self():
    url = "https://raw.githubusercontent.com/jkfyhjghbghjtyhngfh/ai/main/alexa-bot.py"

    speak("Updating system")

    try:
        r = requests.get(url)

        if r.text.strip():
            with open(SELF_FILE, "w", encoding="utf-8") as f:
                f.write(r.text)

            speak("Update complete. Restarting.")
            os.execv(sys.executable, [sys.executable, SELF_FILE])

    except:
        speak("Update failed.")

# ---------- COMMAND HANDLER ----------
def handle_command(cmd):

    cmd = cmd.lower().strip()

    # exit
    if cmd == "exit":
        speak("Shutting down")
        sys.exit()

    # update
    if cmd == "/update":
        update_self()
        return

    # built-in commands
    if "time" in cmd:
        import datetime
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return

    if "your name" in cmd:
        speak("I am your assistant")
        return

    # AI fallback
    speak("Thinking")
    reply = ask_ollama(cmd)
    speak(reply)

# ---------- MAIN LOOP ----------
print("Type: hey assistant <message>  |  type exit to quit")
speak("System online")

while True:
    text = input("You: ").strip().lower()

    if text == "exit":
        speak("Goodbye")
        break

    # Alexa-style trigger
    if text.startswith("hey assistant"):
        cmd = text.replace("hey assistant", "").strip()

        if cmd == "":
            speak("Yes?")
            continue

        handle_command(cmd)

    else:
        speak("Say 'hey assistant' first")