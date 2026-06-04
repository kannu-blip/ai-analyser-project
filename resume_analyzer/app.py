from flask import Flask, render_template, request
import pdfplumber
import re

app = Flask(__name__)

# -------------------------------
# PDF TEXT EXTRACTION
# -------------------------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

# -------------------------------
# HOME ROUTE
# -------------------------------
@app.route('/')
def home():
    return render_template('index.html')

# -------------------------------
# UPLOAD ROUTE
# -------------------------------
@app.route('/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        return "No file uploaded"

    file = request.files['resume']

    if file.filename == '':
        return "No selected file"

    # Extract text
    resume_text = extract_text_from_pdf(file)
    resume_text = resume_text.lower()
    
    # Clean text
    resume_text = re.sub(r'\s+', ' ', resume_text)
    resume_text = re.sub(r'[^a-z0-9\s]', ' ', resume_text)
    resume_text = re.sub(r'\s+', ' ', resume_text)

    # Get job description
    job_description = request.form['job_description'].lower()

    # -------------------------------
    # SKILL VARIATIONS (Smart Matching)
    # -------------------------------
    skill_variations = {
        "python": ["python"],
        "machine learning": ["machine learning", "ml"],
        "flask": ["flask"],
        "sql": ["sql", "mysql", "postgresql"],
        "git": ["git", "github"],
        "docker": ["docker"],
        "aws": ["aws", "amazon web services"],
        "api": ["api", "rest api"]
    }

    matched_skills = []
    missing_skills = []

    resume_no_space = resume_text.replace(" ", "")

    for skill, variations in skill_variations.items():
        found = False
        for variant in variations:
            variant_clean = variant.replace(" ", "")
            if variant in resume_text or variant_clean in resume_no_space:
                found = True
                break
        if found:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    # Calculate Score
    total_skills = len(skill_variations)
    score = (len(matched_skills) / total_skills) * 100
    score = round(score, 2)

    # Suggestions
    suggestions = []
    if score < 40:
        suggestions.append("Consider adding more relevant technical skills.")
    if len(missing_skills) > 0:
        suggestions.append("Try including missing technical keywords in your resume.")

    return render_template(
        'result.html',
        score=score,
        matched=matched_skills,
        missing=missing_skills,
        suggestions=suggestions
    )

if __name__ == '__main__':
    app.run(debug=True)