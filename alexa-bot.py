import pyttsx3
import requests
import json
import re
import threading
import queue
import os
import sys
import time

# ---------- CONFIG ----------
OLLAMA_URL = "http://localhost:11434/api/generate"
RAW_URL = "https://raw.githubusercontent.com/jkfyhjghbghjtyhngfh/ai/main/alexa-bot.py"
SELF_FILE = os.path.abspath(__file__)

# ---------- CLEAN ----------
def clean(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# ---------- SPEECH QUEUE ----------
speech_queue = queue.Queue()

# ---------- TTS WORKER ----------
def tts_worker():
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)

    while True:
        word = speech_queue.get()

        if word is None:
            break

        word = clean(word)

        if word.strip():
            try:
                engine.say(word)
                engine.runAndWait()
            except:
                pass

        speech_queue.task_done()

# start TTS thread
threading.Thread(target=tts_worker, daemon=True).start()

# ---------- STREAM + SPEAK ----------
def ask_ollama_stream(prompt):
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "gemma3:1b",
            "prompt": "No emojis. Speak naturally.\n\nUser: " + prompt,
            "stream": True,
            "options": {
                "num_predict": 300
            }
        }, stream=True)

        print("AI: ", end="", flush=True)

        buffer = ""

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                chunk = data.get("response", "")

                print(chunk, end="", flush=True)
                buffer += chunk

                # split words + punctuation
                words = re.findall(r'\b\w+\b|[.,!?]', buffer)

                # keep incomplete last word
                if not buffer.endswith((" ", ".", "!", "?")):
                    buffer = words[-1]
                    words = words[:-1]
                else:
                    buffer = ""

                for word in words:
                    speech_queue.put(word)

        # flush leftover
        if buffer.strip():
            speech_queue.put(buffer)

        print()

    except Exception as e:
        print("Ollama error:", e)

# ---------- UPDATE ----------
def update_self():
    try:
        print("Updating from GitHub...")
        r = requests.get(RAW_URL)
        code = r.text

        if not code.strip():
            print("Update failed: empty file")
            return

        with open(SELF_FILE, "w", encoding="utf-8") as f:
            f.write(code)

        print("Restarting...")
        time.sleep(1)
        os.execv(sys.executable, [sys.executable, SELF_FILE])

    except Exception as e:
        print("Update error:", e)

# ---------- MAIN ----------
print("Type: hey assistant <message> (or exit)")

while True:
    try:
        text = input("You: ").strip().lower()

        if text == "exit":
            break

        if text.startswith("hey assistant"):
            command = text.replace("hey assistant", "").strip()

            if not command:
                speech_queue.put("yes")
                continue

            if command == "/update":
                update_self()
                continue

            ask_ollama_stream(command)

    except Exception as e:
        print("Error:", e)

# stop TTS thread
speech_queue.put(None)

print("\nPress Enter to close...")
input()