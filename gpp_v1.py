"""
GPP v1 - prompt-only reviewer.
No linter, no tools. Just asks the LLM to find PEP 8 issues.
This version exists to show WHERE a plain LLM goes wrong,
so Week 2 knows exactly what to fix.
"""

from pathlib import Path
from anthropic import Anthropic


def review_file(file_path):
    code = Path(file_path).read_text()

    prompt = f"""You are a Python tutor for a beginner.
Read this code and list every PEP 8 issue you find.
For each issue, give the line number, what's wrong, and how to fix it.

Code:
```python
{code}
```
"""

    client = Anthropic()
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    #print("DEBUG:", message.content)  # temporary, remove later
    for block in message.content:
        if block.type == "text":
            return block.text
    return ""


if __name__ == "__main__":
    report = review_file("sample_student.py")
    Path("report_v1.txt").write_text(report, encoding="utf-8")
    print("Done. See report_v1.txt")