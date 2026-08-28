"""
GPP evaluation scorecard.
Runs the reviewer on each eval sample, shows the output next to the
ground truth, and lets you mark hits/misses by hand to compute
precision and recall.
"""

import subprocess
from pathlib import Path
from anthropic import Anthropic
from eval_samples.ground_truth import GROUND_TRUTH


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


def run_scorecard():
    eval_folder = Path("eval_samples")
    results = {}

    for filename, expected_issues in GROUND_TRUTH.items():
        file_path = eval_folder / filename
        print("\n" + "=" * 70)
        print(f"FILE: {filename}")
        print("=" * 70)

        report = review_file(file_path)

        print("\n--- GPP'S REPORT ---")
        print(report)

        print("\n--- GROUND TRUTH (what SHOULD be found) ---")
        if expected_issues:
            for i, issue in enumerate(expected_issues, 1):
                print(f"{i}. {issue}")
        else:
            print("(this file is clean - no real issues)")

        # Manual scoring
        print("\n--- YOUR SCORING ---")
        if expected_issues:
            hits = input(
                f"How many of the {len(expected_issues)} real issues did GPP catch? "
            )
        else:
            hits = 0

        false_positives = input(
            "How many issues did GPP report that AREN'T real (invented/wrong)? "
        )

        results[filename] = {
            "expected": len(expected_issues),
            "hits": int(hits),
            "false_positives": int(false_positives),
        }

    # Compute overall precision/recall
    total_expected = sum(r["expected"] for r in results.values())
    total_hits = sum(r["hits"] for r in results.values())
    total_false_positives = sum(r["false_positives"] for r in results.values())

    recall = total_hits / total_expected if total_expected else 0
    precision = (
        total_hits / (total_hits + total_false_positives)
        if (total_hits + total_false_positives)
        else 0
    )

    print("\n" + "=" * 70)
    print("SCORECARD SUMMARY")
    print("=" * 70)
    for filename, r in results.items():
        print(f"{filename}: {r['hits']}/{r['expected']} caught, {r['false_positives']} false positives")

    print(f"\nOverall Recall:    {recall:.0%}  (% of real issues GPP found)")
    print(f"Overall Precision: {precision:.0%}  (% of GPP's findings that were real)")


if __name__ == "__main__":
    run_scorecard()