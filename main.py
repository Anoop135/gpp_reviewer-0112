"""
GPP web UI - FastAPI version.
"""

import io
from pathlib import Path
import markdown
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from report_export import build_html, build_pdf
from gpp_agent import review_file

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

LAST_REPORT = {"markdown": "", "filename": ""}

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"report": None, "scorecard": None}
    )


@app.post("/review", response_class=HTMLResponse)
async def review(request: Request, student_file: UploadFile = File(...)):
    save_path = UPLOAD_FOLDER / student_file.filename
    contents = await student_file.read()
    save_path.write_bytes(contents)

    report, scorecard = review_file(save_path)

    LAST_REPORT["markdown"] = report
    LAST_REPORT["filename"] = student_file.filename

    report_html = markdown.markdown(
        report, extensions=["fenced_code", "tables"]
    )
    return templates.TemplateResponse(
        request, "index.html", {"report": report_html, "scorecard": scorecard}
    )


@app.get("/download/html")
def download_html():
    html = build_html(LAST_REPORT["markdown"], LAST_REPORT["filename"])
    return StreamingResponse(
        io.BytesIO(html.encode("utf-8")),
        media_type="text/html",
        headers={
            "Content-Disposition": f'attachment; filename="gpp_review_{LAST_REPORT["filename"]}.html"'
        },
    )


@app.get("/download/pdf")
def download_pdf():
    pdf_bytes = build_pdf(LAST_REPORT["markdown"], LAST_REPORT["filename"])
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="gpp_review_{LAST_REPORT["filename"]}.pdf"'
        },
    )