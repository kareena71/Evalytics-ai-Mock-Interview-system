def analyze_sentiment(text):
    text = text.lower()

    positive_words = [
        "success", "improved", "solved", "learned",
        "built", "optimized", "achieved", "implemented"
    ]

    negative_words = [
        "difficult", "problem", "failed",
        "issue", "error", "struggle"
    ]

    positive_score = sum(word in text for word in positive_words)
    negative_score = sum(word in text for word in negative_words)

    if positive_score >= negative_score:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    if len(text) > 150:
        confidence = "high"
    elif len(text) > 60:
        confidence = "medium"
    else:
        confidence = "low"

    return sentiment, confidence

