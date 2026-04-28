from bot.ai import ask_ai

def recommend_music(mood):
    prompt = f"Give 10 songs for mood: {mood}. Provide only the list of artist - song name."
    return ask_ai(prompt)
