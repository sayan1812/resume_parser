from flask import Flask, render_template, request
import fitz  # PyMuPDF
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class ResumeParser:
    def __init__(self, lines):
        self.lines = lines
        self.sections = {}

    def is_section_title(self, line):
        return line.isupper() and not any(char in line for char in "●:.,") and len(line.split()) <= 3

    def fallback_is_section(self, line):
        keywords = [
            "EDUCATION", "EXPERIENCE", "PROJECT", "INTERNSHIP", "ACHIEVEMENT",
            "SKILLS", "RESPONSIBILITY", "PROFILE", "COURSE", "CERTIFICATION"
        ]
        return any(k in line.upper() for k in keywords)

    def group_into_sections(self):
        current_section = "PROFILE"
        self.sections[current_section] = []

        for line in self.lines:
            line = line.strip()
            if not line:
                continue
            if self.is_section_title(line) or self.fallback_is_section(line):
                current_section = line.upper()
                if current_section not in self.sections:
                    self.sections[current_section] = []
            self.sections[current_section].append(line)
        return self.sections


def extract_lines_from_pdf(file_path):
    doc = fitz.open(file_path)
    lines = []
    for page in doc:
        text = page.get_text("text")
        lines.extend(text.splitlines())
    return lines


@app.route("/", methods=["GET", "POST"])
def index():
    sections = {}
    if request.method == "POST":
        file = request.files["resume"]
        if file:
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)
            lines = extract_lines_from_pdf(path)
            parser = ResumeParser(lines)
            sections = parser.group_into_sections()
    return render_template("index.html", sections=sections)


if __name__ == "__main__":
    app.run(debug=True)
