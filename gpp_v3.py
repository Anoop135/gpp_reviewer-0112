"""
GPP v3 - hybrid reviewer + RAG.
Same as v2 (linter + LLM), but now also retrieves the actual PEP 8
text relevant to each issue, so explanations are grounded in the
real style guide instead of the model's paraphrase of it.
"""

import subprocess
from pathlib import Path
from anthropic import Anthropic
from retrieve import load_index, retrieve_relevant_chunks


def run_linter(file_path):
    result = subprocess.run(
        ["pycodestyle", "--max-line-length=79", str(file_path)],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_pep_context(linter_output, index, top_k=3):
    """Retrieve PEP text relevant to the linter's findings."""
    if not linter_output:
        return "No specific PEP 8 sections needed - no formatting issues found."

    # Use the linter output itself as the search query
    results = retrieve_relevant_chunks(linter_output, index, top_k=top_k)
    context = "\n\n---\n\n".join(r["chunk"] for r in results)
    return context


def review_file(file_path):
    code = Path(file_path).read_text()
    linter_output = run_linter(file_path)
    issues = linter_output if linter_output else "No formatting issues found."

    if not Path("pep_index.pkl").exists():
        print("No index found - building one now...")
        from build_index import build_index
        build_index()

    index = load_index()
    pep_context = get_pep_context(linter_output, index)
    ...

    prompt = f"""You are a Python tutor for a beginner.

Code:
```python
{code}
```

Linter findings (trust these line numbers):
{issues}

Here are the actual relevant sections from PEP 8 / PEP 257, for
grounding your explanations in the real style guide:
{pep_context}

Write a two-section report:
SECTION 1 - Explain each linter issue in plain English, referencing
the actual PEP 8 wording above where relevant.
SECTION 2 - Point out naming, docstring, or clarity issues the
linter can't catch.
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
    Path("report_v3.txt").write_text(report, encoding="utf-8")
    print("Done. See report_v3.txt")