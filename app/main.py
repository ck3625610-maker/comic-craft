import json
import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.services.gemini_service import generate_story
from app.services.image_service import generate_panel
from app.services.pdf_service import build_pdf

load_dotenv()

app = FastAPI(title="ComicCraft - AI Comic Story Creator")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/generated", StaticFiles(directory="generated"), name="generated")
templates = Jinja2Templates(directory="app/templates")

# Simple in-memory demo store. Replace with a database if required later.
COMICS: dict[str, dict] = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={...}
    )

@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
    panel_count: int = Form(4),
):
    panel_count = max(2, min(panel_count, 6))
    try:
        story = generate_story(
            story_prompt, character_name, setting, tone, art_style, panel_count
        )
        image_paths = []
        for i, panel in enumerate(story["panels"], start=1):
            path = generate_panel(panel["image_prompt"], i, art_style)
            image_paths.append(path)

        comic_id = uuid4().hex
        COMICS[comic_id] = {
            "story": story,
            "image_paths": [str(p) for p in image_paths],
        }
        return templates.TemplateResponse(
            "comic_preview.html",
            {
                "request": request,
                "comic_id": comic_id,
                "story": story,
                "image_urls": ["/" + str(p).replace("\\", "/") for p in image_paths],
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "default_panels": panel_count,
                "error": str(exc),
            },
            status_code=400,
        )

@app.get("/export/{comic_id}")
async def export_comic(comic_id: str):
    comic = COMICS.get(comic_id)
    if not comic:
        return HTMLResponse("Comic not found.", status_code=404)

    story = comic["story"]
    image_paths = [Path(p) for p in comic["image_paths"]]
    pdf_path = build_pdf(story.get("title", "ComicCraft"), story["panels"], image_paths)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )

@app.get("/success/{comic_id}", response_class=HTMLResponse)
async def success(request: Request, comic_id: str):
    comic = COMICS.get(comic_id)
    if not comic:
        return HTMLResponse("Comic not found.", status_code=404)
    story = comic["story"]
    return templates.TemplateResponse(
        "export_success.html",
        {"request": request, "comic_id": comic_id, "title": story.get("title", "Comic")},
    )

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ComicCraft"}
