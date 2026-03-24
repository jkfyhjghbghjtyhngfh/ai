import requests
import json
import re
import os
import sys
import datetime

# ---------- CONFIG ----------
OLLAMA_URL = "http://localhost:11434/api/generate"
SELF_FILE = os.path.abspath(__file__)

# ---------- SPEAK (FIXED - NO FREEZING) ----------
def speak(text):
    import pyttsx3

    text = re.sub(r'[^\x00-\x7F]+', '', str(text))

    if not text.strip():
        return

    print("Bot:", text)

    engine = pyttsx3.init()   # 🔥 NEW ENGINE EVERY TIME (fixes freezing)
    engine.setProperty('rate', 170)

    engine.say(text)
    engine.runAndWait()
    engine.stop()

# ---------- AI (OLLAMA) ----------
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
        return "AI error. Make sure Ollama is running."

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

    # time
    if "time" in cmd:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return

    # name
    if "your name" in cmd:
        speak("I am your assistant")
        return

    # hello
    if "hi" in cmd:
        speak("Hello! I am working properly now.")
        return

    # AI fallback
    speak("Thinking")
    reply = ask_ollama(cmd)
    speak(reply)

# ---------- MAIN LOOP ----------
print("Type: hey assistant <message>")
speak("System online")

while True:
    text = input("You: ").strip().lower()

    if text == "exit":
        speak("Goodbye")
        break

    if text.startswith("hey assistant"):
        cmd = text.replace("hey assistant", "").strip()

        if cmd == "":
            speak("Yes?")
            continue

        handle_command(cmd)

    else:
        speak("Say 'hey assistant' first")