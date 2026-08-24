"""
GPP v2 - hybrid reviewer.
Runs the real linter first (ground truth), then asks the LLM to
explain those findings in plain English AND catch naming/docstring
issues the linter can't see.
"""

import subprocess
from pathlib import Path
from anthropic import Anthropic


def run_linter(file_path):
    """Run pycodestyle on the file and return its raw output."""
    result = subprocess.run(
        ["pycodestyle", "--max-line-length=79", file_path],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def review_file(file_path):
    code = Path(file_path).read_text()
    linter_output = run_linter(file_path)

    issues = linter_output if linter_output else "No formatting issues found."

    prompt = f"""You are a Python tutor for a beginner.

Here is the student's code:
```python
{code}
```

A linter (pycodestyle) found these exact issues. Trust these line
numbers completely - do not invent or change them:
{issues}

Write a report with two sections.

SECTION 1 - Formatting issues (from the linter)
For each issue above, explain it in plain English: what's wrong,
why it matters, and how to fix it. Use the line numbers given.

SECTION 2 - Beyond the linter
Look at the code yourself and point out anything the linter can't
catch: bad naming (should be snake_case for functions/variables,
PascalCase for classes), unclear variable names, missing docstrings.
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


if __name__ == "__main__":
    report = review_file("sample_student.py")
    Path("report_v2.txt").write_text(report, encoding="utf-8")
    print("Done. See report_v2.txt")