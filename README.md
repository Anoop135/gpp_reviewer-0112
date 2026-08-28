# GPP — PEP 8 Learning Assistant

GPP reviews a beginner's Python file and produces a plain-English report
on its PEP 8 style issues — not just flagging violations like a standard
linter, but explaining *why* each rule matters, grounding explanations in
the real PEP 8/257 text, and catching issues a linter can't (naming,
docstrings, clarity).

## How it works

GPP combines four layers, built incrementally:

1. **Linter (pycodestyle)** — finds exact, line-numbered formatting
   violations. Reliable ground truth; no guessing.
2. **LLM (Claude)** — explains those violations in beginner-friendly
   language, and separately reviews the code for issues the linter can't
   catch (naming, docstrings, clarity).
3. **RAG** — retrieves the actual PEP 8 / PEP 257 text most relevant to
   each issue (via TF-IDF + cosine similarity) and grounds the LLM's
   explanations in the real spec instead of its paraphrase of it.
4. **Agent (LangGraph)** — reviews the code, then self-checks whether the
   review is complete (every finding explained, every function/class
   covered). If not, loops back with feedback on what was missed, up to
   2 passes. Does **not** edit the student's code — stays a teaching
   tool, not an autofixer, by design.

## Project structure
gpp-project/
├── app.py # Flask web UI
├── main.py # FastAPI web UI (same logic, different framework)
├── templates/
│ └── index.html # shared UI template
├── gpp_v1.py # Week 1: prompt-only reviewer (baseline)
├── gpp_v2.py # Week 2: hybrid linter + LLM reviewer
├── gpp_v3.py # Week 3: hybrid + RAG
├── gpp_agent.py # Weeks 4-5: LangGraph agent with iterate-until-clean loop
├── fetch_pep_docs.py # downloads real PEP 8 / PEP 257 text
├── build_index.py # chunks PEP docs, builds TF-IDF index
├── retrieve.py # finds relevant PEP chunks via cosine similarity
├── scorecard.py # evaluation: precision/recall against known sample files
├── eval_samples/ # test files + hand-written ground truth
├── pep_docs/ # fetched PEP 8/257 text (source data)
└── requirements.txt


## Setup

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key-here"   # Windows: setx ANTHROPIC_API_KEY "..."
```

## Usage

**Terminal (any version):**
```bash
python gpp_v3.py       # hybrid + RAG, single pass
python gpp_agent.py    # full agent, up to 2 passes
```

**Web UI:**
```bash
python app.py                                    # Flask, http://localhost:5000
uvicorn main:app --host 0.0.0.0 --port 8000       # FastAPI, http://localhost:8000
```

**Evaluation scorecard:**
```bash
python scorecard.py
```
Runs the reviewer against `eval_samples/` and computes precision/recall
against hand-written ground truth. Current result: 100% recall / 100%
precision on a 4-file set — note this is a small, self-authored test
set, not a broad benchmark.

## Design decisions worth knowing

- **The agent never edits code.** "Iterate until clean" means the
  *review* becomes more complete across passes, not that the code gets
  auto-fixed. This preserves the tool's teaching intent.
- **RAG grounds explanations, not detection.** The linter still does all
  the actual issue-finding; RAG only improves how issues get explained.
- **Cost/thoroughness tradeoff.** Each agent pass is a full extra API
  call. Capped at 2 passes as a balance for a beginner-facing tool.

## Roadmap status

| Week | Deliverable | Status |
|------|-------------|--------|
| 1 | Prompt-only reviewer | ✅ |
| 2 | Linter wired in via subprocess | ✅ |
| 3 | RAG over PEP style-guide docs | ✅ |
| 4-5 | LangGraph agent, iterate-until-clean loop | ✅ |
| 6 | Scorecard, evaluation, CLI/UI polish | ✅ |

## Tech stack

Python, pycodestyle, scikit-learn (TF-IDF/RAG), LangGraph, Anthropic API
(Claude), Flask, FastAPI
