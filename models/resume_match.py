from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match(resume_text, jd_text):
    # SAFETY CHECKS
    if not resume_text or not jd_text:
        return 0.0

    resume_text = resume_text.lower()
    jd_text = jd_text.lower()

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([resume_text, jd_text])

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(similarity * 100, 2)


