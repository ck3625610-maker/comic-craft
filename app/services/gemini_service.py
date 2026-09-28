import json
import os
from google import genai
from google.genai import types

SYSTEM_PROMPT = """You are ComicCraft, an AI comic story planner.
Create an original, family-friendly comic in a consistent tone.
Return ONLY valid JSON with this shape:
{
  "title": "...",
  "summary": "...",
  "panels": [
    {
      "panel_number": 1,
      "scene": "...",
      "narration": "...",
      "dialogue": [{"speaker": "...", "text": "..."}],
      "image_prompt": "..."
    }
  ]
}
Rules:
- Make 2 to 6 panels.
- Keep the main character visually consistent across all image prompts.
- Each image_prompt must describe a single comic panel and include setting, character appearance, action, camera framing, lighting, and the requested art style.
- Avoid copyrighted characters and real-person likenesses.
- Keep dialogue concise.
"""

def _client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is missing. Add it to your .env file.")
    return genai.Client(api_key=key)

def generate_story(prompt: str, character: str, setting: str, tone: str, art_style: str, panels: int):
    client = _client()
    user_prompt = f"""
Create a {panels}-panel comic.

Story idea: {prompt}
Main character: {character}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Make the story have a clear beginning, middle, and ending.
"""
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.9,
            response_mime_type="application/json",
        ),
    )
    text = response.text
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Gemini returned invalid JSON. Please try again.") from exc

    if not isinstance(data.get("panels"), list) or not data["panels"]:
        raise RuntimeError("Gemini did not return comic panels.")
    return data
