from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import pdfplumber
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "build-study-content.py"
OUTPUT = ROOT / "tmp" / "study-content-audit"


def load_generator():
    spec = importlib.util.spec_from_file_location("study_content_generator", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def main() -> int:
    generator = load_generator()
    resources = {item["id"]: item for item in generator.load_resources()}
    missing: list[dict] = []
    for resource_id, resource in resources.items():
        content_path = ROOT / "study-content" / f"{resource_id}.json"
        if not content_path.exists() or resource.get("type") not in {"pdf", "test"}:
            continue
        content = json.loads(content_path.read_text(encoding="utf-8"))
        covered = {int(section["id"].split("-")[-1]) for section in content["sections"]}
        for page_number in range(1, int(content["pageCount"]) + 1):
            if page_number not in covered:
                missing.append({"resource": resource, "page": page_number})

    OUTPUT.mkdir(parents=True, exist_ok=True)
    cards: list[Image.Image] = []
    report: list[dict] = []
    for entry in missing:
        resource, page_number = entry["resource"], entry["page"]
        with pdfplumber.open(ROOT / resource["file"]) as document:
            page = document.pages[page_number - 1]
            extracted = generator.repair_text(page.extract_text() or "")
            ocr = generator.ocr_page(page, extracted)
            rendered = page.to_image(resolution=100).original.convert("RGB")
        rendered.thumbnail((440, 620))
        card = Image.new("RGB", (480, 700), "white")
        draw = ImageDraw.Draw(card)
        draw.text((18, 12), f"{resource['id']} · pagina {page_number}", fill="black")
        card.paste(rendered, ((480 - rendered.width) // 2, 48))
        cards.append(card)
        report.append({
            "id": resource["id"],
            "page": page_number,
            "extracted": extracted[:500],
            "ocr": ocr[:1000],
        })

    columns = 4
    rows = math.ceil(len(cards) / columns)
    contact = Image.new("RGB", (columns * 480, rows * 700), "#dddddd")
    for index, card in enumerate(cards):
        contact.paste(card, ((index % columns) * 480, (index // columns) * 700))
    contact.save(OUTPUT / "missing-pages-contact.jpg", quality=90)
    (OUTPUT / "missing-pages.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(missing)} pagine non incluse; audit: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
