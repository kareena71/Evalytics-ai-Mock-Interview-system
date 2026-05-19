import pytesseract
from pdf2image import convert_from_path
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import PyPDF2
import re

def calculate_answer_quality(answer):
    if not answer or len(answer.strip()) == 0:
        return 0.0

    answer = answer.lower()

    word_count = len(answer.split())
    sentence_count = len(answer.split("."))

    # ---- Keyword scoring ----
    keywords = [
        "overfitting",
        "training",
        "test",
        "generalization",
        "variance",
        "model",
        "data"
    ]

    keyword_score = 0
    for word in keywords:
        if word in answer:
            keyword_score += 1

    keyword_percent = (keyword_score / len(keywords)) * 40

    # ---- Length scoring ----
    length_score = min(word_count * 1.5, 30)

    # ---- Structure scoring ----
    structure_score = min(sentence_count * 5, 30)

    final_score = keyword_percent + length_score + structure_score

    return round(min(final_score, 100), 1)



def calculate_confidence(violations):
    confidence = 100 - (violations * 10)
    return max(confidence, 0)


def calculate_integrity(violations):
    integrity = 100 - (violations * 15)
    return max(integrity, 0)


def resume_match_score(resume_text, jd_text):
    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())

    if len(jd_words) == 0:
        return 0

    common = resume_words.intersection(jd_words)
    return int((len(common) / len(jd_words)) * 100)


app = Flask(__name__)
app.secret_key = "mock-interview-secret"
app.permanent_session_lifetime = timedelta(hours=2)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------ UTILS ------------------

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

def read_pdf_safe(path):
    text = ""

    try:
        # First try normal PDF text extraction
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "

        # If nothing extracted, use OCR
        if len(text.strip()) == 0:
            images = convert_from_path(path)
            for img in images:
                text += pytesseract.image_to_string(img)

    except Exception as e:
        print("PDF read error:", e)

    return text.strip()

def calculate_resume_match(resume_text, jd_text):
    if not resume_text or not jd_text:
        return 0.0

    resume_text = clean_text(resume_text)
    jd_text = clean_text(jd_text)

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000
    )

    vectors = vectorizer.fit_transform([resume_text, jd_text])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

    return round(similarity * 100, 2)


def calculate_answer_quality(answer):
    if not answer:
        return 0.0

    answer = answer.lower()

    keywords = [
        "overfitting",
        "training",
        "generalization",
        "test",
        "high variance",
        "memorize",
        "model"
    ]

    score = 0
    for word in keywords:
        if word in answer:
            score += 1

    return round((score / len(keywords)) * 100, 1)

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return redirect(url_for("setup"))

@app.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        session.clear()
        session.permanent = True

        session["candidate_name"] = request.form.get("name")
        session["role"] = request.form.get("role")

        jd_text = request.form.get("jd_text")
        jd_file = request.files.get("jd_file")
        resume_file = request.files.get("resume_file")

        # Save JD
        if jd_file and jd_file.filename != "":
            jd_path = os.path.join(UPLOAD_FOLDER, "jd.pdf")
            jd_file.save(jd_path)
        elif jd_text:
            with open(os.path.join(UPLOAD_FOLDER, "jd.txt"), "w", encoding="utf-8") as f:
                f.write(jd_text)

        # Save Resume
        if resume_file and resume_file.filename != "":
            resume_path = os.path.join(UPLOAD_FOLDER, "resume.pdf")
            resume_file.save(resume_path)

        session["final_answer"] = ""
        session["focus_violations"] = 0
        session["pause_count"] = 0

        return redirect(url_for("interview"))

    return render_template("setup.html")

@app.route("/interview")
def interview():
    return render_template(
        "interview.html",
        name=session.get("candidate_name"),
        role=session.get("role")
    )

@app.route("/submit_interview", methods=["POST"])
def submit_interview():
    data = request.get_json()

    answer = data["answer"]
    violations = data["violations"]

    print("FINAL ANSWER LENGTH:", len(answer)) 

    session["final_answer"] = answer
    session["focus_violations"] = violations

    return jsonify({"status": "success"})

@app.route("/result")
def result():
    if "candidate_name" not in session:
        return redirect(url_for("setup"))

    resume_pdf = os.path.join(UPLOAD_FOLDER, "resume.pdf")
    jd_pdf = os.path.join(UPLOAD_FOLDER, "jd.pdf")
    jd_txt = os.path.join(UPLOAD_FOLDER, "jd.txt")

    # -------- READ RESUME --------
    if os.path.exists(resume_pdf):
        resume_text = read_pdf_safe(resume_pdf)
    else:
        resume_text = ""

    # -------- READ JD --------
    if os.path.exists(jd_pdf):
        jd_text = read_pdf_safe(jd_pdf)
    elif os.path.exists(jd_txt):
        with open(jd_txt, "r", encoding="utf-8") as f:
            jd_text = f.read()
    else:
        jd_text = ""

    # -------- DEBUG PRINTS --------
    print("Resume length:", len(resume_text))
    print("JD length:", len(jd_text))

    answer_text = session.get("final_answer", "")
    pause_count = session.get("pause_count", 0)
    focus_violations = session.get("focus_violations", 0)

    # -------- DEBUG ANSWER --------
    print("ANSWER LENGTH:", len(answer_text))
    print("ANSWER PREVIEW:", answer_text[:200])

    answer_quality = calculate_answer_quality(answer_text)
    resume_match = calculate_resume_match(resume_text, jd_text)

    if len(answer_text.strip()) == 0:
        confidence_level = 0
    else:
        word_based_score = min(100, len(answer_text.split()) * 2)
        pause_penalty = pause_count * 5
        confidence_level = max(0, word_based_score - pause_penalty)

    integrity_score = max(0, min(100, 100 - focus_violations * 10))

    final_score = round(
        (answer_quality * 0.4) +
        (confidence_level * 0.3) +
        (integrity_score * 0.3),
        1
    )

    report = {
        "final_score": final_score,
        "answer_quality": answer_quality,
        "confidence_level": confidence_level,
        "resume_match": resume_match,
        "integrity_score": integrity_score,
        "focus_violations": focus_violations
    }

    return render_template(
        "result.html",
        report=report,
        name=session["candidate_name"],
        role=session["role"]
    )   


if __name__ == "__main__":
    app.run(debug=True)   