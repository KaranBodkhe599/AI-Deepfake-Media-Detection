# scanner.py

from modules.scraper import scrape_article
from modules.ai_bot import analyze_text
from modules.inference import analyze_image
from modules.scoring import calculate_score

def scan_article(url):
    try:
        article = scrape_article(url)

        image_result = analyze_image(article["image"])

        text_result = analyze_text(article["text"])

        final = calculate_score(
            image_result["score"],
            text_result["score"]
        )

        return {
            "title": article["title"],
            "image_score": image_result["score"],
            "text_score": text_result["score"],
            "final_score": final["final_score"],
            "verdict": final["verdict"]
        }

    except Exception as e:
        print("Scanner Error:", str(e))

        return {
            "title": "Processing Failed",
            "image_score": 0,
            "text_score": 0,
            "final_score": 0,
            "verdict": "Error"
        }