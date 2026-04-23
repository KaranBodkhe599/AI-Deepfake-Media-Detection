import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key="


def fact_check_article(text):

    if not API_KEY:
        print("⚠️ No Gemini API Key")
        return fallback("No API key")

    try:
        prompt = f"""
You are a professional fact-checker.

Analyze this news and classify it:
Real | Mostly Real | Suspicious | Fake

Return ONLY valid JSON:
{{
  "fact_score": number (0 to 1),
  "verdict": "Real|Mostly Real|Suspicious|Fake",
  "reason": "short explanation"
}}

News:
{text[:1500]}
"""

        response = requests.post(
            GEMINI_URL + API_KEY,
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=10
        )

        if response.status_code != 200:
            print("❌ Gemini HTTP Error:", response.text)
            return fallback("API error")

        data = response.json()

        # 🔥 SAFE EXTRACTION
        candidates = data.get("candidates", [])
        if not candidates:
            return fallback("No candidates")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            return fallback("No content")

        output = parts[0].get("text", "")
        print("🧠 Gemini Output:", output)

        # 🔥 SAFE JSON EXTRACTION
        match = re.search(r'\{.*?\}', output, re.DOTALL)
        if not match:
            return fallback("No JSON found")

        try:
            result = json.loads(match.group())
        except:
            return fallback("Invalid JSON")

        return {
            "fact_score": round(float(result.get("fact_score", 0.5)), 2),
            "fact_verdict": result.get("verdict", "Unknown"),
            "fact_analysis": result.get("reason", "No explanation")
        }

    except requests.exceptions.Timeout:
        return fallback("Timeout")

    except Exception as e:
        print("❌ FactCheck Error:", e)
        return fallback("Exception")


# 🔻 FALLBACK
def fallback(reason="Unavailable"):
    return {
        "fact_score": 0.5,
        "fact_verdict": "Unknown",
        "fact_analysis": f"Fact check unavailable ({reason})"
    }