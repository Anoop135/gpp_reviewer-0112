"""
GPP web UI - upload a .py file, get a PEP 8 review displayed on screen.
"""

import subprocess
from pathlib import Path
from flask import Flask, request, render_template
from anthropic import Anthropic

app = Flask(__name__)


def run_linter(file_path):
    result = subprocess.run(
        ["pycodestyle", "--max-line-length=79", str(file_path)],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def review_file(file_path):
    code = Path(file_path).read_text()
    linter_output = run_linter(file_path)
    issues = linter_output if linter_output else "No formatting issues found."

    prompt = f"""You are a Python tutor for a beginner.

Code:
```python
{code}
```

Linter findings (trust these line numbers):
{issues}

Write a two-section report:
SECTION 1 - Explain each linter issue in plain English.
SECTION 2 - Point out naming, docstring, or clarity issues the linter can't catch.
"""

    client = Anthropic()
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    for block in message.content:
        if block.type == "text":
            return block.text
    return ""


@app.route("/")
def index():
    return render_template("index.html", report=None)


UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

@app.route("/review", methods=["POST"])
def review():
    uploaded = request.files["student_file"]
    save_path = UPLOAD_FOLDER / uploaded.filename
    uploaded.save(save_path)

    report = review_file(save_path)
    return render_template("index.html", report=report)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)