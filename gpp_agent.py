"""
GPP agent - LangGraph version.
Reviews code, then self-checks whether the review is complete.
If not, loops back for another pass (up to a max), focusing on
what was missed. Never edits the student's code - stays a
teaching tool, not an autofixer.
"""

import subprocess
from pathlib import Path
from typing import TypedDict
from langgraph.graph import StateGraph, END
from anthropic import Anthropic
from retrieve import load_index, retrieve_relevant_chunks

MAX_PASSES = 2  # each extra pass = another full API call; 2 balances
                # thoroughness against cost for a beginner-facing tool

PROMPTS_FOLDER = Path("prompts")


# --- The shared state every node reads from and writes to ---
class GPPState(TypedDict):
    code: str
    linter_output: str
    pep_context: str
    review: str
    pass_count: int
    is_complete: bool
    missed_feedback: str


# --- Prompt loading ---
def load_prompt(name, **values):
    """Load a prompt template from prompts/ and fill in the placeholders."""
    template = (PROMPTS_FOLDER / f"{name}.txt").read_text(encoding="utf-8")
    return template.format(**values)


# --- Reused helpers from earlier versions ---
def run_linter(file_path):
    result = subprocess.run(
        ["pycodestyle", "--max-line-length=79", str(file_path)],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def call_claude(prompt):
    client = Anthropic()
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}],
    )
    for block in message.content:
        if block.type == "text":
            return block.text
    return ""


# --- Node 1: review the code ---
def review_node(state: GPPState) -> dict:
    print(f"\n[Pass {state['pass_count'] + 1}] Reviewing...")

    extra_instruction = ""
    if state.get("missed_feedback"):
        extra_instruction = f"""
On the previous pass, this was missed or incomplete:
{state['missed_feedback']}
Make sure to address it this time.
"""

    issues = state["linter_output"] or "No formatting issues found."

    prompt = load_prompt(
        "review",
        code=state["code"],
        linter_output=issues,
        pep_context=state["pep_context"],
        extra_instruction=extra_instruction,
    )

    review = call_claude(prompt)
    return {
        "review": review,
        "pass_count": state["pass_count"] + 1,
    }


# --- Node 2: self-check whether the review is complete ---
def check_completeness_node(state: GPPState) -> dict:
    print(f"[Pass {state['pass_count']}] Checking completeness...")

    prompt = load_prompt(
        "completeness_check",
        code=state["code"],
        review=state["review"],
        linter_output=state["linter_output"],
    )

    check = call_claude(prompt)
    print(f"  -> {check.strip()}")

    is_complete = check.strip().upper().startswith("COMPLETE")
    missed_feedback = "" if is_complete else check

    return {
        "is_complete": is_complete,
        "missed_feedback": missed_feedback,
    }


# --- Conditional edge: decide whether to loop or stop ---
def should_continue(state: GPPState) -> str:
    if state["is_complete"]:
        return "done"
    if state["pass_count"] >= MAX_PASSES:
        print(f"Reached max passes ({MAX_PASSES}), stopping.")
        return "done"
    return "retry"


# --- Build the graph ---
def build_graph():
    graph = StateGraph(GPPState)

    graph.add_node("review", review_node)
    graph.add_node("check", check_completeness_node)

    graph.set_entry_point("review")
    graph.add_edge("review", "check")
    graph.add_conditional_edges(
        "check",
        should_continue,
        {"retry": "review", "done": END},
    )

    return graph.compile()


def review_file(file_path):
    code = Path(file_path).read_text()
    linter_output = run_linter(file_path)

    index = load_index()
    if linter_output:
        results = retrieve_relevant_chunks(linter_output, index, top_k=3)
        pep_context = "\n\n---\n\n".join(r["chunk"] for r in results)
    else:
        pep_context = "No specific PEP 8 sections needed."

    initial_state = {
        "code": code,
        "linter_output": linter_output,
        "pep_context": pep_context,
        "review": "",
        "pass_count": 0,
        "is_complete": False,
        "missed_feedback": "",
    }

    agent = build_graph()
    final_state = agent.invoke(initial_state)

    print(f"\nFinished after {final_state['pass_count']} pass(es).")
    return final_state["review"]


if __name__ == "__main__":
    report = review_file("sample_student.py")
    Path("report_agent.txt").write_text(report, encoding="utf-8")
    print("Done. See report_agent.txt")