import traceback
import requests
import cv2
import numpy as np

STOCK_PHOTO_DOMAINS = [
    "shutterstock.com", "gettyimages.com", "istockphoto.com",
    "alamy.com", "depositphotos.com", "dreamstime.com",
    "123rf.com", "stock.adobe.com", "unsplash.com", "pexels.com"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def analyze_image(image_url: str) -> dict:

    if not image_url:
        return fallback("No image")

    try:
        # DOWNLOAD IMAGE
        response = requests.get(image_url, timeout=8, headers=HEADERS)

        if response.status_code != 200:
            return fallback(f"HTTP {response.status_code}")

        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            return fallback("Invalid content")

        raw_bytes = response.content
        file_size = len(raw_bytes)

        # DECODE IMAGE
        img_array = np.frombuffer(raw_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            return fallback("Decode failed")

        height, width = img.shape[:2]

        if height == 0 or width == 0:
            return fallback("Invalid dimensions")

        total_pixels = height * width

        # IMPROVED BASE SCORE
        score = 0.6
        flags = []
        positive = []

        # SHARPNESS (Laplacian)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sharpness = float(np.var(cv2.Laplacian(gray, cv2.CV_64F)))

        if sharpness > 300:
            score += 0.15
            positive.append("High sharpness")
        elif sharpness > 80:
            score += 0.05
            positive.append("Moderate sharpness")
        elif sharpness > 20:
            score -= 0.08
            flags.append("Low sharpness")
        else:
            score -= 0.15
            flags.append("Very blurry")

        # COMPRESSION (bytes per pixel)
        bpp = file_size / total_pixels

        if bpp < 0.10:
            score -= 0.15
            flags.append("Extreme compression")
        elif bpp < 0.25:
            score -= 0.08
            flags.append("High compression")
        elif bpp > 1.5:
            score += 0.10
            positive.append("High quality image")

        # ASPECT RATIO
        aspect = width / height

        if aspect > 4 or aspect < 0.25:
            score -= 0.12
            flags.append("Extreme aspect ratio")
        elif aspect > 2.5 or aspect < 0.4:
            score -= 0.05
            flags.append("Unusual aspect ratio")

        # STOCK IMAGE CHECK
        if any(domain in image_url.lower() for domain in STOCK_PHOTO_DOMAINS):
            score -= 0.10
            flags.append("Stock image source")

        # FINAL SCORE CLAMP
        score = round(max(0.0, min(1.0, score)), 2)

        # IMPROVED ANALYSIS TEXT
        analysis = f"Image score {score}. "

        if score >= 0.75:
            analysis += "Image appears natural and high quality."
        elif score >= 0.55:
            analysis += "Image looks mostly normal with minor issues."
        elif score >= 0.35:
            analysis += "Suspicious patterns detected in the image."
        else:
            analysis += "Image shows strong signs of manipulation or low quality."

        if flags:
            analysis += " Issues: " + ", ".join(flags)

        if positive:
            analysis += " Positive signs: " + ", ".join(positive)

        print(
            f"[Image] sharpness={sharpness:.1f} | "
            f"bpp={bpp:.2f} | aspect={aspect:.2f} | "
            f"score={score} | flags={flags} | positive={positive}"
        )

        return {
            "score": score,
            "analysis": analysis,
            "flags": flags,
            "positive_signals": positive,

            # Extra metrics for dashboard
            "sharpness": round(sharpness, 2),
            "bytes_per_pixel": round(bpp, 3),
            "aspect_ratio": round(aspect, 2),
            "dimensions": f"{width}x{height}",
        }

    except requests.exceptions.Timeout:
        return fallback("Timeout")

    except Exception:
        print(f"[Image ERROR]\n{traceback.format_exc()}")
        return fallback("Exception")


# FALLBACK
def fallback(reason="Error"):
    return {
        "score": 0.5,
        "analysis": f"Image analysis failed ({reason})",
        "flags": [],
        "positive_signals": []
    }