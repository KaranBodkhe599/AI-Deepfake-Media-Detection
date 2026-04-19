import random

def analyze_image(image_url):
    try:
        if not image_url:
            return {"score": 0.5}

        score = random.uniform(0.5, 0.95)

        return {"score": round(score, 2)}

    except:
        return {"score": 0.5}