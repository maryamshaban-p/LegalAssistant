import speech_recognition as sr
from gtts import gTTS
import pygame
import time
import os


# =========================
# VOICE INPUT (Arabic + English)
# =========================

def listen_text():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("Listening...")

        recognizer.adjust_for_ambient_noise(source)

        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text

    except:
        return ""


# =========================
# VOICE OUTPUT (AUTO LANGUAGE)
# =========================

def speak_text(text, lang="en"):

    tts = gTTS(
        text=text,
        lang=lang
    )

    filename = "response.mp3"

    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.5)

    pygame.mixer.quit()
    os.remove(filename)