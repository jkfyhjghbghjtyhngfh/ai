import requests
import json
import re
import os
import sys
import datetime

import pyttsx3
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ---------- CONFIG ----------
OLLAMA_URL = "http://localhost:11434/api/generate"
SELF_FILE = os.path.abspath(__file__)

# ---------- SPOTIFY CONFIG ----------
SPOTIPY_CLIENT_ID = "12a4b608e28142848fa2afa54d08606f"
SPOTIPY_CLIENT_SECRET = "f35a99acbe164153852286d95260ea0a"
SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-read-playback-state,user-modify-playback-state"
))

# ---------- SPEAK (FIXED) ----------
def speak(text):
    import pyttsx3

    text = re.sub(r'[^\x00-\x7F]+', '', str(text))
    if not text.strip():
        return

    print("Bot:", text)

    engine = pyttsx3.init()
    engine.setProperty('rate', 170)

    engine.say(text)
    engine.runAndWait()
    engine.stop()

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
        return "AI error. Make sure Ollama is running."

# ---------- SPOTIFY ----------
def play_song(query):
    try:
        results = sp.search(q=query, limit=1, type='track')

        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            uri = track['uri']
            name = track['name']
            artist = track['artists'][0]['name']

            sp.start_playback(uris=[uri])
            speak(f"Playing {name} by {artist}")
        else:
            speak("Song not found")

    except Exception as e:
        speak("Spotify error")
        print(e)

# ---------- UPDATE ----------
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

    # greeting
    if "hi" in cmd:
        speak("Hello")
        return

    # ---------- SPOTIFY COMMANDS ----------
    if cmd.startswith("play "):
        song = cmd.replace("play ", "")
        play_song(song)
        return

    if "pause music" in cmd:
        sp.pause_playback()
        speak("Paused")
        return

    if "resume music" in cmd:
        sp.start_playback()
        speak("Resuming")
        return

    if "next song" in cmd:
        sp.next_track()
        speak("Skipping")
        return

    # ---------- AI ----------
    speak("Thinking")
    reply = ask_ollama(cmd)
    speak(reply)

# ---------- MAIN ----------
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