import customtkinter as ctk

from chatbot import get_response
from voice import listen_text, speak_text


# =========================
# LANGUAGE DETECTION
# =========================

def detect_language(text):
    return "ar" if any('\u0600' <= c <= '\u06FF' for c in text) else "en"


def main():
    # =========================
    # APP SETUP
    # =========================
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.geometry("900x700")
    app.title("Legal AI Assistant")

    app.resizable(True, True)
    app.minsize(600, 500)

    # =========================
    # UI
    # =========================
    title = ctk.CTkLabel(app, text="⚖️ Legal AI Assistant", font=("Arial", 28, "bold"))
    title.pack(pady=20)

    chat_box = ctk.CTkTextbox(app, font=("Arial", 18))
    chat_box.pack(pady=20, fill="both", expand=True)

    entry = ctk.CTkEntry(app, height=45, font=("Arial", 18))
    entry.pack(pady=10, fill="x", padx=20)

    # =========================
    # TEXT MESSAGE
    # =========================
    def send_message():
        user_message = entry.get()

        if user_message == "":
            return

        response = get_response(user_message)

        chat_box.insert("end", f"\n👤 YOU:\n{user_message}\n\n")
        chat_box.insert("end", f"⚖️ BOT:\n{response}\n\n")

        entry.delete(0, "end")
        chat_box.see("end")

    # =========================
    # VOICE MESSAGE
    # =========================
    def voice_input():
        chat_box.insert("end", "\n🎤 Listening...\n")
        app.update()

        # Arabic + English voice input
        text, err = listen_text(preferred_lang="ar-EG")

        if text == "":
            chat_box.insert("end", f"❌ {err}\n")
            return

        response = get_response(text)

        chat_box.insert("end", f"\n🎤 YOU:\n{text}\n\n")
        chat_box.insert("end", f"⚖️ BOT:\n{response}\n\n")

        # Speak back in the same language the user spoke
        speak_lang = detect_language(text)
        speak_text(response, lang=("ar" if speak_lang == "ar" else "en"))

        entry.delete(0, "end")
        chat_box.see("end")

    # =========================
    # BUTTONS
    # =========================
    frame = ctk.CTkFrame(app)
    frame.pack(pady=20, fill="x")

    ctk.CTkButton(frame, text="Send", command=send_message, width=150, height=45).grid(row=0, column=0, padx=20)
    ctk.CTkButton(frame, text="🎤 Speak", command=voice_input, width=150, height=45).grid(row=0, column=1, padx=20)

    app.mainloop()


if __name__ == "__main__":
    main()