import traceback
from modules.scraper import scrape_article
from modules.ai_bot import analyze_text
from modules.inference import analyze_image
from modules.fact_check import fact_check_article
from modules.scoring import calculate_score


# Default error response
def _error_result(reason: str = "Processing failed") -> dict:
    return {
        "title": "Error",
        "image_score": 0.0,
        "text_score": 0.0,
        "fact_score": 0.0,
        "final_score": 0.0,
        "confidence": 0.0,
        "verdict": "Error",
        "analysis": reason,
        "fact_analysis": "",
        "fact_verdict": "",
        "fake_words": 0,
        "real_words": 0,
        "trusted_score": 0,
        "word_count": 0,
        "image_count": 0,
        "video_count": 0,
    }


# Main function
def scan_article(url: str) -> dict:
    try:
        print("🔍 Starting scan...")

        # ── 1. SCRAPE ─────────────────────────────
        article = scrape_article(url)
        text = article.get("text", "")
        image = article.get("image", "")

        if not text or len(text.strip()) < 50:
            print("⚠️ No valid text found")
            return _error_result("No text extracted from article")

        print(f"📰 Title: {article.get('title')}")
        print(f"🧾 Text length: {len(text)} chars")
        print(f"🖼 Image found: {'Yes' if image else 'No'}")

        # ── 2. ANALYSIS ───────────────────────────
        image_result = analyze_image(image)
        text_result = analyze_text(text, url)
        fact_result = fact_check_article(text)

        # ── 3. SCORES ─────────────────────────────
        image_score = float(image_result.get("score", 0.5))
        text_score = float(text_result.get("score", 0.5))
        fact_score = float(fact_result.get("fact_score", 0.5))

        print(f"[Scores] image={image_score} | text={text_score} | fact={fact_score}")

        # ── 4. FINAL SCORE ────────────────────────
        final = calculate_score(image_score, text_score, fact_score)

        # ── 5. BUILD RESULT ───────────────────────
        result = {
            "title": article.get("title", "No Title"),

            "image_score": image_score,
            "text_score": text_score,
            "fact_score": fact_score,
            "final_score": final.get("final_score", 0),
            "confidence": final.get("confidence", 0),
            "verdict": final.get("verdict", "Unknown"),

            "analysis": text_result.get("analysis", ""),
            "fact_analysis": fact_result.get("fact_analysis", ""),
            "fact_verdict": fact_result.get("fact_verdict", ""),

            "fake_words": text_result.get("fake_keywords", 0),
            "real_words": text_result.get("real_keywords", 0),
            "trusted_score": text_result.get("trusted_matches", 0),

            "word_count": len(text.split()),
            "image_count": 1 if image else 0,
            "video_count": 0,
        }

        print("✅ Scan completed successfully")

        return result

    except Exception as e:
        print(f"[Scanner ERROR]\n{traceback.format_exc()}")
        return _error_result(str(e))