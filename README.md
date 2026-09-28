# ComicCraft — AI Comic Story Creator

A FastAPI web application matching the supplied Smart Internz project architecture:
- Gemini for story/dialogue/panel planning
- Hugging Face Diffusers/Stable Diffusion inference for panel artwork
- Jinja2 + HTML/CSS frontend
- PDF export using FPDF2
- Local deployment and testing

## 1. Requirements
- Python 3.11+
- A Gemini API key
- Optional: Hugging Face token with inference permission for real image generation

## 2. Setup

### Windows
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and set:
```text
GEMINI_API_KEY=...
HF_TOKEN=...
```

If you don't have an HF token yet, leave it blank. The app will use a local visual placeholder so you can test the complete workflow. Add the token later to enable generated diffusion images.

## 3. Run
```bash
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

Health check: http://127.0.0.1:8000/health

## 4. Project mapping to the assignment
- `app/main.py` → FastAPI routes and request processing
- `app/services/gemini_service.py` → Gemini story generation
- `app/services/image_service.py` → Hugging Face diffusion image generation
- `app/services/pdf_service.py` → PDF comic export
- `app/templates/index.html` → input form
- `app/templates/comic_preview.html` → comic preview
- `app/templates/export_success.html` → export confirmation
- `app/static/style.css` → responsive UI
- `generated/` → generated images/PDFs

## 5. Troubleshooting
- `GEMINI_API_KEY is missing`: add the key to `.env`.
- HF errors: check `HF_TOKEN`, model availability, or set `IMAGE_MODE=placeholder` while testing the rest of the application.
- PDF encoding: for simple English text the included FPDF2 setup works directly. If your project requires Tamil/other Unicode text in PDFs, add a Unicode TTF font and register it in `pdf_service.py`.

## 6. Demo idea
Prompt:
"A college student finds a tiny robot in the computer lab. The robot can predict bugs before the code runs, but one prediction threatens the college festival."

Character: Arun
Setting: College computer lab
Tone: Adventure
Art style: Modern colorful comic
Panels: 4
