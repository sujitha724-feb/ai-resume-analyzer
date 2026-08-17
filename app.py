from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import re
import PyPDF2

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Skills that our first version can identify
SKILLS = [
    "python",
    "java",
    "c",
    "c++",
    "javascript",
    "html",
    "css",
    "sql",
    "mysql",
    "flask",
    "django",
    "spring boot",
    "react",
    "flutter",
    "dart",
    "git",
    "github",
    "machine learning",
    "data science"
]


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def extract_text_from_pdf(file_path):
    text = ""

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def find_skills(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills


def calculate_score(text, skills):
    text_lower = text.lower()

    score = 0

    # Skills: maximum 40
    skill_score = min(len(skills) * 4, 40)
    score += skill_score

    # Education: 15
    if any(word in text_lower for word in [
        "education",
        "b.tech",
        "btech",
        "bachelor",
        "degree"
    ]):
        score += 15

    # Projects: 20
    if "project" in text_lower or "projects" in text_lower:
        score += 20

    # Experience: 15
    if any(word in text_lower for word in [
        "experience",
        "internship",
        "work experience"
    ]):
        score += 15

    # Certifications: 10
    if any(word in text_lower for word in [
        "certification",
        "certifications",
        "certificate"
    ]):
        score += 10

    return min(score, 100)


def generate_suggestions(text, skills):
    text_lower = text.lower()

    suggestions = []

    if len(skills) < 5:
        suggestions.append(
            "Add more relevant technical skills."
        )

    if "project" not in text_lower and "projects" not in text_lower:
        suggestions.append(
            "Add at least one relevant project."
        )

    if "github" not in text_lower:
        suggestions.append(
            "Add your GitHub profile."
        )

    if "linkedin" not in text_lower:
        suggestions.append(
            "Add your LinkedIn profile."
        )

    if (
        "certification" not in text_lower
        and "certificate" not in text_lower
    ):
        suggestions.append(
            "Add relevant certifications."
        )

    if (
        "experience" not in text_lower
        and "internship" not in text_lower
    ):
        suggestions.append(
            "Add internship or practical experience when available."
        )

    if not suggestions:
        suggestions.append(
            "Good start! Continue improving your projects and achievements."
        )

    return suggestions


@app.route("/", methods=["GET", "POST"])
def index():

    result = None

    if request.method == "POST":

        if "resume" not in request.files:
            return render_template(
                "index.html",
                error="Please select a PDF resume."
            )

        file = request.files["resume"]

        if file.filename == "":
            return render_template(
                "index.html",
                error="Please select a PDF resume."
            )

        if not allowed_file(file.filename):
            return render_template(
                "index.html",
                error="Only PDF files are supported."
            )

        filename = secure_filename(file.filename)

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(file_path)

        try:
            text = extract_text_from_pdf(file_path)

            if not text.strip():
                return render_template(
                    "index.html",
                    error="Could not extract text from this PDF."
                )

            skills = find_skills(text)

            score = calculate_score(
                text,
                skills
            )

            suggestions = generate_suggestions(
                text,
                skills
            )

            result = {
                "score": score,
                "skills": skills,
                "suggestions": suggestions
            }

        except Exception as error:
            return render_template(
                "index.html",
                error=f"Error while analyzing resume: {error}"
            )

    return render_template(
        "index.html",
        result=result
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
      )
