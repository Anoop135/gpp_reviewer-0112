"""
Converts a GPP markdown report into downloadable HTML and PDF files.
"""

import io
import re
import markdown
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GPP Review - {filename}</title>
    <style>
        body {{
            font-family: -apple-system, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            line-height: 1.6;
            color: #222;
        }}
        h1, h2 {{ margin-top: 28px; }}
        code {{
            background: #eee;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 90%;
        }}
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 14px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        pre code {{ background: none; color: inherit; }}
        .meta {{ color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>GPP — PEP 8 Review</h1>
    <p class="meta">File reviewed: {filename}</p>
    <hr>
    {body}
</body>
</html>
"""


def build_html(report_markdown, filename):
    """Return a complete, standalone HTML document as a string."""
    body = markdown.markdown(
        report_markdown, extensions=["fenced_code", "tables"]
    )
    return HTML_TEMPLATE.format(filename=filename, body=body)


def clean_inline(text):
    """Convert basic markdown inline formatting to reportlab's XML tags."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", text)
    text = re.sub(r"^[-*]\s+", "• ", text)
    return text


def build_pdf(report_markdown, filename):
    """Return a PDF of the report as bytes, ready to send as a download."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    code_style = ParagraphStyle(
        "CodeBlock",
        parent=styles["Code"],
        fontSize=8,
        leading=10,
        leftIndent=12,
    )

    story = [
        Paragraph("GPP — PEP 8 Review", styles["Title"]),
        Paragraph(f"File reviewed: {filename}", styles["Normal"]),
        Spacer(1, 16),
    ]

    in_code_block = False
    code_lines = []

    for line in report_markdown.split("\n"):
        if line.strip().startswith("```"):
            if in_code_block:
                story.append(Preformatted("\n".join(code_lines), code_style))
                story.append(Spacer(1, 8))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not line.strip():
            continue

        if line.startswith("## "):
            story.append(Spacer(1, 12))
            story.append(Paragraph(clean_inline(line[3:]), styles["Heading2"]))
        elif line.startswith("# "):
            story.append(Spacer(1, 12))
            story.append(Paragraph(clean_inline(line[2:]), styles["Heading1"]))
        else:
            story.append(Paragraph(clean_inline(line), styles["Normal"]))
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()