from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_ai(text):
    if not OPENAI_API_KEY:
        return "OpenAI API key sozlanmagan."
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":text}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"AI xatosi: {str(e)}"
