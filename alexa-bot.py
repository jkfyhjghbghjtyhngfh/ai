import requests
import re
import os
import sys
import datetime
import time
import subprocess

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

# ---------- SPEAK ----------
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

# ---------- SPOTIFY PLAY ----------
def play_song(query):
    try:
        subprocess.Popen("start spotify", shell=True)
        time.sleep(5)

        devices = sp.devices()['devices']

        if not devices:
            speak("No Spotify device found")
            return

        device_id = devices[0]['id']

        sp.transfer_playback(device_id=device_id, force_play=True)

        time.sleep(1)

        results = sp.search(q=query, limit=1, type='track')

        if not results['tracks']['items']:
            speak("Song not found")
            return

        track = results['tracks']['items'][0]

        sp.start_playback(
            device_id=device_id,
            uris=[track['uri']]
        )

        speak(f"Playing {track['name']}")

    except Exception as e:
        speak("Spotify error")
        print(e)

# ---------- COMMAND HANDLER (FIXED ORDER) ----------
def handle_command(cmd):

    cmd = cmd.lower().strip()
    cmd = re.sub(r'\s+', ' ', cmd)

    # ---------- EXIT ----------
    if cmd == "exit":
        speak("Shutting down")
        sys.exit()

    # ---------- SPOTIFY (MUST BE FIRST) ----------
    if cmd in ["pause music", "pause song"]:
        try:
            sp.pause_playback()
            speak("Paused")
        except:
            speak("No music playing")
        return

    if cmd in ["resume music", "play music"]:
        try:
            sp.start_playback()
            speak("Resuming")
        except:
            speak("Nothing to resume")
        return

    if cmd in ["stop music", "turn off music", "stop song"]:
        try:
            sp.pause_playback()
            speak("Stopped")
        except:
            speak("No music playing")
        return

    if cmd.startswith("play "):
        song = cmd.replace("play ", "", 1)
        play_song(song)
        return

    # ---------- OTHER COMMANDS ----------
    if "time" in cmd:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return

    if "your name" in cmd:
        speak("I am your assistant")
        return

    if "hi" in cmd:
        speak("Hello")
        return

    # ---------- AI FALLBACK ----------
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