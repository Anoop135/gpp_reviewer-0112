"""
GPP web UI - FastAPI version.
Same review logic as the Flask version, different framework.
"""

import subprocess
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from anthropic import Anthropic
import markdown

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


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

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"report": None}
    )
@app.post("/review", response_class=HTMLResponse)
async def review(request: Request, student_file: UploadFile = File(...)):
    save_path = UPLOAD_FOLDER / student_file.filename
    contents = await student_file.read()
    save_path.write_bytes(contents)

    report = review_file(save_path)
    report_html = markdown.markdown(report, extensions=["fenced_code", "tables"])
    return templates.TemplateResponse(
        request, "index.html", {"report": report_html}
    )
   