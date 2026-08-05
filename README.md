## GPP — PEP 8 Learning Assistant

GPP helps beginner Python coders understand and follow PEP 8 — not just
by flagging violations like a standard linter, but by explaining *why*
each rule matters and how to fix it.

### How it works
GPP uses a hybrid approach:
1. **pycodestyle** (a standard linter) scans the file for exact,
   line-numbered formatting violations — the reliable "ground truth."
2. An **LLM** takes those findings and explains them in plain,
   beginner-friendly language, and separately reviews the code for
   issues linters can't catch — bad naming, missing docstrings, and
   unclear structure.
3. The full report is written to a text file.

This combination gives the accuracy of a linter with the teaching
quality of an LLM.

### Project roadmap
- **Wk 1** — PPT, BRD, Architecture

### Tech stack
Python, pycodestyle, Anthropic API (Claude), LangGraph, RAG
