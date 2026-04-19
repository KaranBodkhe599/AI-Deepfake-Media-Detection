def calculate_score(image_score, text_score):
    final = (image_score * 0.6) + (text_score * 0.4)

    if final > 0.7:
        verdict = "Real"
    elif final > 0.4:
        verdict = "Suspicious"
    else:
        verdict = "Fake"

    return {
        "final_score": round(final, 2),
        "verdict": verdict
    }