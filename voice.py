import speech_recognition as sr
from gtts import gTTS
import pygame
import time
import os


# =========================
# VOICE INPUT (Arabic + English)
# =========================

def _count_arabic_chars(text: str) -> int:
    return sum(1 for c in text if "\u0600" <= c <= "\u06FF")


def _count_latin_chars(text: str) -> int:
    return sum(1 for c in text if ("a" <= c.lower() <= "z"))


def _choose_best_transcript(ar_text: str, en_text: str) -> str:
    """
    Pick the best transcript between Arabic and English attempts.
    We prefer the one whose script matches its language (Arabic letters vs Latin letters),
    because mis-detections can transliterate English into Arabic script (or vice-versa).
    """
    ar_text = (ar_text or "").strip()
    en_text = (en_text or "").strip()

    if not ar_text and not en_text:
        return ""
    if ar_text and not en_text:
        return ar_text
    if en_text and not ar_text:
        return en_text

    ar_ar = _count_arabic_chars(ar_text)
    ar_la = _count_latin_chars(ar_text)
    en_ar = _count_arabic_chars(en_text)
    en_la = _count_latin_chars(en_text)

    # Strong preference rules
    if en_la >= 4 and en_la >= (en_ar * 2 + 1):
        return en_text
    if ar_ar >= 3 and ar_ar >= (ar_la * 2 + 1):
        return ar_text

    # If both are mixed/unclear, prefer the one with "more signal"
    ar_signal = ar_ar + ar_la
    en_signal = en_ar + en_la
    if en_signal > ar_signal:
        return en_text
    if ar_signal > en_signal:
        return ar_text

    # Final fallback: longer string
    return en_text if len(en_text) >= len(ar_text) else ar_text


def list_microphones() -> list[str]:
    try:
        return sr.Microphone.list_microphone_names()
    except Exception:
        return []

def _auto_pick_microphone_index(names: list[str]) -> int | None:
    """
    Heuristic: prefer actual mics (Microphone Array / FrontMic), avoid Stereo Mix/output mappers.
    Returns an index into `names` or None to use system default.
    """
    if not names:
        return None

    def norm(s: str) -> str:
        return s.strip().lower()

    avoid = ("stereo mix", "sound mapper - output", "primary sound driver", "output")
    prefer = ("microphone array", "frontmic", "microphone", "input")

    # First pass: strong prefer + not avoided
    for i, n in enumerate(names):
        nn = norm(n)
        if any(a in nn for a in avoid):
            continue
        if "microphone array" in nn or "frontmic" in nn:
            return i

    # Second pass: any preferred mic-like device, not avoided
    for i, n in enumerate(names):
        nn = norm(n)
        if any(a in nn for a in avoid):
            continue
        if any(p in nn for p in prefer) and "mapper - output" not in nn:
            return i

    return None


def listen_text(preferred_lang: str = "ar-EG", device_index: int | None = None):

    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True

    try:
        # If you have multiple input devices, set device_index to the correct mic.
        if device_index is None:
            names = list_microphones()
            auto_index = _auto_pick_microphone_index(names)
            mic = sr.Microphone(device_index=auto_index) if auto_index is not None else sr.Microphone()
        else:
            mic = sr.Microphone(device_index=device_index)
    except Exception as e:
        return "", f"Microphone error: {e}"

    with mic as source:

        print("Listening...")

        # Make detection a bit more forgiving in quiet rooms / cheap mics.
        try:
            recognizer.energy_threshold = 300
        except Exception:
            pass
        recognizer.adjust_for_ambient_noise(source, duration=0.8)

        try:
            # Avoid hanging forever if there's no speech detected.
            audio = recognizer.listen(source, timeout=12, phrase_time_limit=18)
        except sr.WaitTimeoutError:
            return "", "No speech detected (timeout). Click 🎤 Speak and start talking immediately."

    def _try_langs(langs: tuple[str, ...]) -> tuple[str, str]:
        for lang in langs:
            try:
                text = recognizer.recognize_google(audio, language=lang)
                text = (text or "").strip()
                if text:
                    return text, ""
            except sr.UnknownValueError:
                # Speech detected but not understood in this language.
                continue
            except sr.RequestError as e:
                return "", f"Speech API request failed: {e}"
            except Exception as e:
                return "", f"Speech recognition error: {e}"
        return "", ""

    # Two passes: English-first and Arabic-first.
    en_text, en_err = _try_langs(("en-US",))

    ar_langs: list[str] = []
    if preferred_lang:
        ar_langs.append(preferred_lang)
    for lang in ("ar-EG", "ar-SA", "ar"):
        if lang not in ar_langs:
            ar_langs.append(lang)
    ar_text, ar_err = _try_langs(tuple(ar_langs))

    chosen = _choose_best_transcript(ar_text=ar_text, en_text=en_text)
    print(f"STT chosen: {chosen!r}")
    if chosen:
        return chosen, ""

    # If we couldn't decode any text, surface the most useful error (if any).
    err = en_err or ar_err
    return "", (err or "Could not understand audio (try speaking louder / closer to mic).")


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