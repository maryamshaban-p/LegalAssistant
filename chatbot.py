import json
from googletrans import Translator

translator = Translator()

# =========================
# LOAD DATA
# =========================

with open("legal_data.json", "r", encoding="utf-8") as file:
    legal_data = json.load(file)


# =========================
# RESPONSE FORMAT
# =========================

def format_response(item):

    return f"""
📌 {item.get('title')}

📖 Description:
{item.get('description')}

📚 Examples:
{chr(10).join(item.get('examples_use_cases', []))}

⚖️ Key Rules:
{chr(10).join(item.get('key_articles_rules', []))}
"""


def get_response(user_input):

    # detect Arabic
    is_arabic = any('\u0600' <= c <= '\u06FF' for c in user_input)

    # translate to English for matching
    if is_arabic:
        try:
            user_input = translator.translate(user_input, src="ar", dest="en").text
        except Exception:
            # If translation fails, keep Arabic text; matching might still work on shared tokens.
            pass

    user_input = user_input.lower()

    best_match = None
    highest_score = 0

    for item in legal_data:

        text = (
            item.get("title", "") + " " +
            item.get("category", "") + " " +
            item.get("description", "") + " " +
            " ".join(item.get("examples_use_cases", [])) + " " +
            " ".join(item.get("key_articles_rules", []))
        ).lower()

        score = 0

        for word in user_input.split():
            if word in text:
                score += 1

        if score > highest_score:
            highest_score = score
            best_match = item

    if not best_match:
        return "Sorry / عذراً، لم أجد إجابة مناسبة."

    response = format_response(best_match)

    if is_arabic:
        try:
            response = translator.translate(response, src="en", dest="ar").text
        except Exception:
            # Keep English if translation fails, but still return something.
            pass

    return response