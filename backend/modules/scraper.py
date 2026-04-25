import traceback
import requests
from bs4 import BeautifulSoup
from newspaper import Article, Config
from urllib.parse import urljoin

# Strong headers (avoid blocking)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# 🔹 Newspaper config
NEWSPAPER_CONFIG = Config()
NEWSPAPER_CONFIG.browser_user_agent = HEADERS["User-Agent"]
NEWSPAPER_CONFIG.request_timeout = 10

MIN_TEXT_LENGTH = 100
MAX_TEXT_LENGTH = 12000

INVALID_MARKERS = [
    "enable javascript",
    "google image result",
    "please enable cookies",
    "access denied",
    "subscribe to read",
]


def scrape_article(url: str) -> dict:

    print(f"[Scraper] Fetching: {url}")

    # ── PRIMARY: newspaper3k ─────────────────────────────
    try:
        article = Article(url, config=NEWSPAPER_CONFIG)
        article.download()
        article.parse()

        title = (article.title or "").strip() or "No Title"
        text = (article.text or "").strip()
        image = article.top_image or ""
        video = article.movies[0] if article.movies else ""

        _validate(text)

        print(f"[Scraper] newspaper3k SUCCESS ({len(text)} chars)")

        return _build(title, text, image, video)

    except Exception as e:
        print(f"[Scraper] newspaper3k FAILED: {e}")

    # ── FALLBACK: BeautifulSoup ───────────────────────────
    try:
        res = requests.get(url, timeout=10, headers=HEADERS)

        if res.status_code != 200:
            raise Exception(f"HTTP {res.status_code}")

        soup = BeautifulSoup(res.text, "html.parser")

        # 🔹 TITLE
        og_title = soup.find("meta", property="og:title")
        title = (
            og_title["content"].strip()
            if og_title and og_title.get("content")
            else (soup.title.string.strip() if soup.title else "No Title")
        )

        # 🔹 TEXT
        paragraphs = soup.find_all("p")
        text = " ".join(
            p.get_text().strip()
            for p in paragraphs
            if len(p.get_text().strip()) > 40
        )

        # 🔹 IMAGE (fix relative URL)
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            image = og_image["content"]
        else:
            img = soup.find("img")
            image = img["src"] if img and img.get("src") else ""

        if image and not image.startswith("http"):
            image = urljoin(url, image)

        # 🔹 VIDEO DETECTION
        video = ""
        if soup.find("video") or soup.find("iframe", src=lambda s: s and "youtube" in s):
            video = "detected"

        _validate(text)

        print(f"[Scraper] BeautifulSoup SUCCESS ({len(text)} chars)")

        return _build(title, text, image, video)

    except Exception:
        print(f"[Scraper] FALLBACK FAILED:\n{traceback.format_exc()}")

    # ── FINAL FAIL ───────────────────────────────────────
    print("[Scraper] All methods failed")

    return {
        "title": "Scraping Failed",
        "text": "",
        "image": "",
        "video": "",
        "word_count": 0,
    }


# 🔻 VALIDATION
def _validate(text: str):
    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        raise ValueError("Text too short")

    text_lower = text.lower()

    for marker in INVALID_MARKERS:
        if marker in text_lower:
            raise ValueError(f"Blocked content: {marker}")


# 🔻 BUILD RESULT
def _build(title: str, text: str, image: str, video: str) -> dict:
    text = text[:MAX_TEXT_LENGTH]

    return {
        "title": title,
        "text": text,
        "image": image,
        "video": video,
        "word_count": len(text.split()),
    }