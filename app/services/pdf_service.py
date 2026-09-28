from pathlib import Path
from fpdf import FPDF

GENERATED = Path("generated")
GENERATED.mkdir(exist_ok=True)

def build_pdf(title: str, panels: list[dict], image_paths: list[Path]) -> Path:
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title).strip() or "comic"
    output = GENERATED / f"{safe_title[:60]}.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=14)

    for idx, panel in enumerate(panels):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, title)
        pdf.ln(2)

        if idx < len(image_paths) and image_paths[idx].exists():
            pdf.image(str(image_paths[idx]), x=12, y=34, w=186)

        pdf.set_y(160)
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 7, f"Panel {panel.get('panel_number', idx + 1)}")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, panel.get("narration", ""))

        for line in panel.get("dialogue", []):
            speaker = line.get("speaker", "Character")
            text = line.get("text", "")
            pdf.multi_cell(0, 6, f'{speaker}: {text}')

    pdf.output(str(output))
    return output
