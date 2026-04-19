import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def analyze_text(text):
    try:
        if not API_KEY:
            return {"score": 0.5}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

        prompt = f"""
        Analyze the following news article and give a credibility score.

        Rules:
        - Return ONLY a number between 0 and 1
        - 0 = completely fake
        - 1 = completely real

        Example output:
        0.75

        Text:
        {text}
        """

        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        res = requests.post(url, json=payload)
        data = res.json()

        if "candidates" not in data:
            return {"score": 0.5}

        output = data['candidates'][0]['content']['parts'][0]['text']

        print("Gemini Output:", output)

        # Extract number safely
        try:
            score = float(output.strip())
            score = max(0, min(score, 1))  # clamp between 0–1
        except:
            score = 0.5

        return {"score": round(score, 2)}

    except Exception as e:
        print("Gemini Error:", str(e))
        return {"score": 0.5}