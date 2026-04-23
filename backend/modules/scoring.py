def calculate_score(image_score: float, text_score: float, fact_score: float) -> dict:

    # ── Clamp inputs ──────────────────────────────────────────
    image_score = max(0.0, min(1.0, float(image_score)))
    text_score  = max(0.0, min(1.0, float(text_score)))
    fact_score  = max(0.0, min(1.0, float(fact_score)))

    # ── Weighted base score ───────────────────────────────────
    # Image weight is low — OpenCV sharpness/FFT is not reliable
    # for fake detection. Gemini text + fact carry the real signal.
    final = (image_score * 0.15) + (text_score * 0.50) + (fact_score * 0.35)

    # ── Conflict penalty ──────────────────────────────────────
    # Only measure conflict between text and fact (both Gemini-based).
    # Image is excluded from conflict since it's a different signal type.
    conflict = abs(text_score - fact_score)     # 0.0 → 1.0
    penalty  = conflict * 0.08                  # up to -0.08
    final    = round(max(0.0, min(1.0, final - penalty)), 2)

    # ── Confidence ────────────────────────────────────────────
    raw_confidence = abs(final - 0.5) * 200
    conflict_drag  = conflict * 15
    confidence     = round(max(5.0, min(100.0, raw_confidence - conflict_drag)), 1)

    # ── Verdict ───────────────────────────────────────────────
    if final >= 0.78:
        verdict = "Real"
    elif final >= 0.62:
        verdict = "Mostly Real"
    elif final >= 0.42:
        verdict = "Suspicious"
    else:
        verdict = "Fake"

    print(
        f"[Scoring] image={image_score} | text={text_score} | fact={fact_score} "
        f"| conflict={round(conflict, 2)} | penalty={round(penalty, 3)} "
        f"→ final={final} | confidence={confidence}% | verdict={verdict}"
    )

    return {
        "final_score": final,
        "confidence":  confidence,
        "verdict":     verdict,
        "breakdown": {
            "image":    image_score,
            "text":     text_score,
            "fact":     fact_score,
            "conflict": round(conflict, 2),
        }
    }