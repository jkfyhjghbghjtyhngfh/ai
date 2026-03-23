import pyttsx3
import requests
import json
import re
import os
import sys
import time

# ---------- CONFIG ----------
OLLAMA_URL = "http://localhost:11434/api/generate"
RAW_URL = "https://raw.githubusercontent.com/jkfyhjghbghjtyhngfh/ai/main/alexa-bot.py"
SELF_FILE = os.path.abspath(__file__)

# ---------- CLEAN TEXT ----------
def clean_text(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# ---------- SPEAK (STABLE) ----------
def speak(text):
    text = clean_text(text)

    engine = pyttsx3.init()  # fresh each time (prevents bugs)
    engine.setProperty('rate', 170)

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)

    engine.say(text)
    engine.runAndWait()
    engine.stop()

# ---------- OLLAMA STREAM ----------
def ask_ollama_stream(prompt):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "gemma3:1b",
            "prompt": "You are a helpful AI. Give detailed answers. No emojis.\n\nUser: " + prompt,
            "stream": True,
            "options": {
                "num_predict": 500
            }
        }, stream=True)

        full = ""

        print("AI: ", end="", flush=True)

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                chunk = data.get("response", "")
                print(chunk, end="", flush=True)
                full += chunk

        print()
        return full

    except Exception as e:
        print("Ollama error:", e)
        return ""

# ---------- SELF UPDATE ----------
def update_self():
    try:
        print("Updating from GitHub...")
        r = requests.get(RAW_URL)
        code = r.text

        if not code.strip():
            speak("Update failed. File is empty.")
            return

        with open(SELF_FILE, "w", encoding="utf-8") as f:
            f.write(code)

        speak("Update complete. Restarting.")

        time.sleep(1)
        os.execv(sys.executable, [sys.executable, SELF_FILE])

    except Exception as e:
        speak(f"Update failed: {e}")
        print("Error:", e)

# ---------- MAIN ----------
print("Type: hey assistant <your message> (or 'exit' to quit)")

while True:
    try:
        text = input("You: ").strip().lower()

        if text == "exit":
            break

        if text.startswith("hey assistant"):
            command = text.replace("hey assistant", "").strip()

            if not command:
                speak("Yes?")
                continue

            if command == "/update":
                update_self()
                continue

            reply = ask_ollama_stream(command)

            # ONLY speak after fully done
            if reply.strip():
                speak(reply)
            else:
                print("No response to speak.")

    except Exception as e:
        print("Error:", e)

# ---------- KEEP WINDOW OPEN ----------
print("\nAssistant ended. Press Enter to close.")
input()