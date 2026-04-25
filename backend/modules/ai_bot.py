import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={api_key}"

MAX_CHARS = 12000

def analyze_text(text: str, url: str = "") -> dict:

    if not text.strip():
        return fallback_analysis(text)

    if not API_KEY:
        print("[TextAnalysis] No API key — fallback used.")
        return fallback_analysis(text)

    truncated = text[:MAX_CHARS]

    prompt = f"""
You are an expert AI system for detecting fake news and misinformation.

Analyze the following news article carefully using these criteria:
- Factual accuracy and realism
- Presence of verifiable sources or evidence
- Tone (neutral vs sensational or emotional)
- Logical consistency of claims
- Signs of misinformation, propaganda, or exaggeration

Scoring rules:
- 0.9–1.0 → Highly credible, factual, reliable journalism
- 0.7–0.89 → Mostly credible with minor issues
- 0.4–0.69 → Suspicious, lacks evidence or contains exaggeration
- 0.0–0.39 → Likely fake, misleading, or fabricated

Be decisive. Avoid neutral answers unless truly uncertain.

Return ONLY valid JSON:
{{
  "score": <number between 0 and 1>,
  "verdict": "<Real|Mostly Real|Suspicious|Fake>",
  "reason": "<clear 1-2 line explanation>"
}}

Article:
{truncated}
"""
    try:
        response = requests.post(
            GEMINI_URL.format(api_key=API_KEY),
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=15
        )

        print("[Gemini Status]", response.status_code)

        if response.status_code != 200:
            print("[TextAnalysis] HTTP Error:", response.text[:200])
            return fallback_analysis(text)

        data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            print("[TextAnalysis] No candidates")
            return fallback_analysis(text)

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            print("[TextAnalysis] No parts")
            return fallback_analysis(text)

        raw = parts[0].get("text", "")
        print("[TextAnalysis] Output:", raw[:300])

        match = re.search(r'\{[\s\S]*\}', raw)

        if not match:
            print("No JSON found")
            return fallback_analysis(text)

        try:
            result = json.loads(match.group())
        except json.JSONDecodeError as e:
            print("JSON parse error:", e)
            return fallback_analysis(text)

        score = round(max(0.0, min(1.0, float(result.get("score", 0.5)))), 2)

        return {
            "score": score,
            "analysis": result.get("reason", "Analysis complete"),
            "verdict": result.get("verdict", "Unknown"),

            "summary": "",
            "red_flags": [],
            "positive_signals": [],
            "risk_level": "",

            "fake_keywords": 0,
            "real_keywords": 0,
            "trusted_matches": 0,
        }

    except requests.exceptions.Timeout:
        print("[TextAnalysis] Timeout")
        return fallback_analysis(text)

    except Exception as e:
        print("[TextAnalysis ERROR]", e)
        return fallback_analysis(text)

def fallback_analysis(text: str) -> dict:
    text_lower = text.lower()

    fake_words = [
        "shocking", "fake", "hoax", "viral", "unbelievable",
        "exposed", "conspiracy", "breaking", "urgent"
    ]

    real_words = [
        "report", "official", "confirmed", "according to",
        "research", "study", "data", "evidence"
    ]

    fake_count = sum(1 for w in fake_words if w in text_lower)
    real_count = sum(1 for w in real_words if w in text_lower)

    score = 0.5 + (real_count * 0.08) - (fake_count * 0.08)
    score = round(max(0.0, min(1.0, score)), 2)

    return {
        "score": score,
        "analysis": "Fallback keyword analysis used",
        "verdict": "Unknown",

        "summary": "No summary available",
        "red_flags": [],
        "positive_signals": [],
        "risk_level": "Unknown",

        "fake_keywords": fake_count,
        "real_keywords": real_count,
        "trusted_matches": 0,
    }