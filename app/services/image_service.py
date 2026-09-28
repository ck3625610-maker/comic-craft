import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import InferenceClient

GENERATED = Path("generated")
GENERATED.mkdir(exist_ok=True)

def _placeholder(prompt: str, panel_number: int) -> Path:
    """Offline-safe fallback so the app can be demonstrated without an HF token."""
    path = GENERATED / f"panel_{panel_number}.png"
    img = Image.new("RGB", (1024, 768), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((24, 24, 1000, 744), outline="black", width=8)
    draw.rectangle((48, 48, 976, 150), fill="#111827")
    draw.text((70, 78), f"COMIC PANEL {panel_number}", fill="white")
    wrapped = prompt[:420]
    draw.text((70, 205), wrapped, fill="black")
    draw.text((70, 680), "Add HF_TOKEN to enable AI image generation.", fill="#374151")
    img.save(path)
    return path

def generate_panel(image_prompt: str, panel_number: int, art_style: str) -> Path:
    mode = os.getenv("IMAGE_MODE", "auto").lower()
    token = os.getenv("HF_TOKEN")
    if mode == "placeholder" or (mode == "auto" and not token):
        return _placeholder(image_prompt, panel_number)

    client = InferenceClient(api_key=token)
    model = os.getenv("HF_MODEL", "stabilityai/stable-diffusion-2-1")
    prompt = (
        f"{image_prompt}. Comic-book panel, {art_style}, clean composition, "
        "consistent character design, expressive faces, no text, no watermark."
    )
    try:
        image = client.text_to_image(
            prompt=prompt,
            model=model,
            width=1024,
            height=768,
            num_inference_steps=25,
        )
        path = GENERATED / f"panel_{panel_number}.png"
        image.save(path)
        return path
    except Exception as exc:
        # Keep the project demo usable if an inference provider/model is temporarily unavailable.
        return _placeholder(f"Image generation fallback. {image_prompt}", panel_number)
