from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "study-content"
VISUALS = OUTPUT / "visuals"
UNKNOWN = "\ufffd"
TESSERACT = Path(os.environ.get("TESSERACT_EXE", r"C:\Program Files\Tesseract-OCR\tesseract.exe"))
TESSDATA = ROOT / "tmp" / "tessdata"


def table(headers: list[str], rows: list[list[str]]) -> dict:
    return {"type": "table", "headers": headers, "rows": rows}


# A few source pages contain vector tables or screenshots: PDF text extraction
# and OCR cannot reconstruct their rows reliably. These verified transcriptions
# keep the lesson native and accessible instead of falling back to a page image.
PAGE_OVERRIDES: dict[tuple[str, int], dict] = {
    ("logica-multipli-sottomultipli", 1): {
        "title": "Prefissi del Sistema Internazionale",
        "blocks": [
            {"type": "paragraph", "text": "I prefissi indicano potenze di dieci applicate all’unità di misura. Per convertire una misura, individua l’esponente del prefisso di partenza e quello di arrivo, quindi sposta la virgola della differenza tra i due esponenti."},
            table(
                ["Potenza", "Prefisso", "Simbolo", "Valore"],
                [
                    ["10²⁴", "yotta", "Y", "quadrilione"], ["10²¹", "zetta", "Z", "triliardo"],
                    ["10¹⁸", "exa", "E", "trilione"], ["10¹⁵", "peta", "P", "biliardo"],
                    ["10¹²", "tera", "T", "bilione"], ["10⁹", "giga", "G", "miliardo"],
                    ["10⁶", "mega", "M", "milione"], ["10³", "kilo", "k", "mille"],
                    ["10²", "etto", "h", "cento"], ["10¹", "deca", "da", "dieci"],
                    ["10⁻¹", "deci", "d", "decimo"], ["10⁻²", "centi", "c", "centesimo"],
                    ["10⁻³", "milli", "m", "millesimo"], ["10⁻⁶", "micro", "µ", "milionesimo"],
                    ["10⁻⁹", "nano", "n", "miliardesimo"], ["10⁻¹²", "pico", "p", "bilionesimo"],
                    ["10⁻¹⁵", "femto", "f", "biliardesimo"], ["10⁻¹⁸", "atto", "a", "trilionesimo"],
                    ["10⁻²¹", "zepto", "z", "triliardesimo"], ["10⁻²⁴", "yocto", "y", "quadrilionesimo"],
                ],
            ),
        ],
    },
    ("logica-multipli-sottomultipli-2", 1): {
        "title": "Scala pratica dei multipli e sottomultipli",
        "blocks": [
            {"type": "paragraph", "text": "La scala mette in relazione ogni prefisso con il suo moltiplicatore. A ogni salto tra kilo, etto, deca, unità, deci, centi e milli corrisponde un fattore 10."},
            table(
                ["Prefisso", "Moltiplicatore", "Simbolo"],
                [
                    ["tera", "10¹²", "T"], ["giga", "10⁹", "G"], ["mega", "10⁶", "M"],
                    ["kilo", "10³", "k"], ["etto", "10²", "h"], ["deca", "10¹", "da"],
                    ["unità di misura", "10⁰", "—"], ["deci", "10⁻¹", "d"], ["centi", "10⁻²", "c"],
                    ["milli", "10⁻³", "m"], ["micro", "10⁻⁶", "µ"], ["nano", "10⁻⁹", "n"],
                    ["pico", "10⁻¹²", "p"], ["femto", "10⁻¹⁵", "f"], ["atto", "10⁻¹⁸", "a"],
                ],
            ),
        ],
    },
    ("chimica-nomenclatura", 33): {
        "title": "Formazione e nomenclatura degli ossiacidi",
        "blocks": [table(
            ["Reagenti", "Formula", "Nome tradizionale", "Nome IUPAC"],
            [
                ["CO₂ + H₂O", "H₂CO₃", "acido carbonico", "acido triossocarbonico(IV)"],
                ["N₂O₃ + H₂O", "HNO₂", "acido nitroso", "acido diossonitrico(III)"],
                ["N₂O₅ + H₂O", "HNO₃", "acido nitrico", "acido triossonitrico(V)"],
                ["Cl₂O + H₂O", "HClO", "acido ipocloroso", "acido monoossoclorico(I)"],
                ["Cl₂O₃ + H₂O", "HClO₂", "acido cloroso", "acido diossoclorico(III)"],
                ["Cl₂O₅ + H₂O", "HClO₃", "acido clorico", "acido triossoclorico(V)"],
                ["Cl₂O₇ + H₂O", "HClO₄", "acido perclorico", "acido tetraossoclorico(VII)"],
            ],
        )],
    },
    ("chimica-nomenclatura", 34): {
        "title": "Esempi di ossiacidi",
        "blocks": [table(
            ["Formula", "n.o. del non metallo", "Nome tradizionale", "Nome IUPAC"],
            [
                ["H₂SO₃", "+4", "acido solforoso", "acido triossosolforico(IV)"],
                ["H₂SO₄", "+6", "acido solforico", "acido tetraossosolforico(VI)"],
                ["HNO₂", "+3", "acido nitroso", "acido diossonitrico(III)"],
                ["HNO₃", "+5", "acido nitrico", "acido triossonitrico(V)"],
                ["H₂CO₃", "+4", "acido carbonico", "acido triossocarbonico(IV)"],
                ["H₃PO₃", "+3", "acido fosforoso", "acido triossofosforico(III)"],
                ["H₃PO₄", "+5", "acido fosforico", "acido tetraossofosforico(V)"],
                ["HClO", "+1", "acido ipocloroso", "acido ossoclorico(I)"],
                ["HClO₂", "+3", "acido cloroso", "acido diossoclorico(III)"],
                ["HClO₃", "+5", "acido clorico", "acido triossoclorico(V)"],
                ["HClO₄", "+7", "acido perclorico", "acido tetraossoclorico(VII)"],
            ],
        )],
    },
    ("chimica-nomenclatura", 39): {
        "title": "Dagli ossiacidi ai sali ternari",
        "blocks": [
            {"type": "paragraph", "text": "Il nome dell’anione deriva dall’acido: il suffisso -oso diventa -ito, mentre -ico diventa -ato. I prefissi ipo- e per- restano invariati."},
            table(
                ["Acido", "Anione", "Esempi di sali"],
                [
                    ["HClO · acido ipocloroso", "ClO⁻ · ipoclorito", "NaClO ipoclorito di sodio; Ba(ClO)₂ ipoclorito di bario"],
                    ["HClO₂ · acido cloroso", "ClO₂⁻ · clorito", "KClO₂ clorito di potassio; Zn(ClO₂)₂ clorito di zinco"],
                    ["HClO₃ · acido clorico", "ClO₃⁻ · clorato", "LiClO₃ clorato di litio; Al(ClO₃)₃ clorato di alluminio"],
                    ["HClO₄ · acido perclorico", "ClO₄⁻ · perclorato", "KClO₄ perclorato di potassio; Cu(ClO₄)₂ perclorato rameico"],
                ],
            ),
        ],
    },
    ("chimica-nomenclatura", 40): {
        "title": "Esempi di sali",
        "blocks": [table(
            ["Formula", "Nome tradizionale"],
            [
                ["CaCO₃", "carbonato di calcio"], ["NaNO₂", "nitrito di sodio"],
                ["NaNO₃", "nitrato di sodio"], ["KClO", "ipoclorito di potassio"],
                ["KClO₂", "clorito di potassio"], ["KClO₃", "clorato di potassio"],
                ["KClO₄", "perclorato di potassio"], ["BaSO₄", "solfato di bario"],
            ],
        )],
    },
    ("chimica-reazioni", 4): {
        "title": "Reazioni di sintesi: schemi ed esempi",
        "blocks": [table(
            ["Reazione", "Esempio"],
            [
                ["non metallo + ossigeno → ossido acido", "C + O₂ → CO₂"],
                ["metallo + ossigeno → ossido basico", "2Cu + O₂ → 2CuO"],
                ["metallo + non metallo → sale binario", "2Al + 3I₂ → 2AlI₃"],
                ["metallo + idrogeno → idruro", "2Li + H₂ → 2LiH"],
                ["alogeno + idrogeno → idracido", "Cl₂ + H₂ → 2HCl"],
                ["ossido acido + acqua → ossiacido", "SO₃ + H₂O → H₂SO₄"],
                ["ossido basico + acqua → idrossido", "BaO + H₂O → Ba(OH)₂"],
            ],
        )],
    },
}

PAGE_OVERRIDES.update({
    ("chimica-generale", 28): {
        "title": "Geometrie molecolari e angoli di legame",
        "blocks": [
            {"type": "paragraph", "text": "La disposizione dei gruppi elettronici attorno all’atomo centrale determina la geometria della molecola e i suoi angoli di legame."},
            table(
                ["Molecola", "Gruppi elettronici", "Forma", "Angolo di legame"],
                [["BeH₂", "2", "lineare", "180°"], ["BH₃", "3", "triangolare planare", "120°"], ["CH₄", "4", "tetraedrica", "109,5°"]],
            ),
        ],
    },
    ("chimica-nomenclatura", 42): {
        "title": "Ioni poliatomici: nitrito, nitrato, fosfato e carbonato",
        "blocks": [
            {"type": "paragraph", "text": "Togliendo gli atomi di idrogeno da un ossiacido si ottiene un anione poliatomico; la carica negativa corrisponde al numero di H rimossi."},
            table(
                ["Ione", "Nome", "Derivazione"],
                [
                    ["NO₂⁻", "nitrito", "dall’acido nitroso HNO₂, dopo la perdita di un H⁺"],
                    ["NO₃⁻", "nitrato", "dall’acido nitrico HNO₃, dopo la perdita di un H⁺"],
                    ["PO₄³⁻", "fosfato", "dall’acido fosforico H₃PO₄, dopo la perdita di tre H⁺"],
                    ["CO₃²⁻", "carbonato", "dall’acido carbonico H₂CO₃, dopo la perdita di due H⁺"],
                ],
            ),
        ],
    },
    ("fisica-cinematica", 20): {
        "title": "Velocità angolare",
        "blocks": [
            {"type": "paragraph", "text": "Nel moto circolare uniforme vengono percorsi angoli uguali in intervalli di tempo uguali. La velocità angolare è il rapporto fra l’angolo descritto e il tempo impiegato."},
            {"type": "heading", "text": "ω = Δθ / Δt = 2π / T = 2πf"},
            {"type": "paragraph", "text": "Nel Sistema Internazionale si misura in rad/s. Il vettore velocità angolare è perpendicolare al piano della circonferenza: è entrante nel moto orario e uscente nel moto antiorario."},
        ],
    },
    ("fisica-cinematica", 21): {
        "title": "Formule del moto circolare uniforme",
        "blocks": [
            {"type": "paragraph", "text": "Nel moto circolare uniforme frequenza e periodo sono legati da f = 1/T. Le formule seguenti collegano raggio, periodo, frequenza, velocità tangenziale, velocità angolare e accelerazione centripeta."},
            table(
                ["Grandezza", "Relazioni"],
                [
                    ["Velocità tangenziale", "v = 2πr/T = 2πrf = ωr"],
                    ["Velocità angolare", "ω = 2π/T = 2πf = v/r"],
                    ["Accelerazione centripeta", "a = v²/r = 4π²r/T² = 4π²rf² = ω²r"],
                ],
            ),
        ],
    },
    ("fisica-cinematica", 24): {
        "title": "Valori notevoli di seno e coseno",
        "blocks": [table(
            ["Radianti", "Gradi", "Seno", "Coseno"],
            [
                ["0", "0°", "0", "1"], ["π/6", "30°", "1/2", "√3/2"],
                ["π/4", "45°", "√2/2", "√2/2"], ["π/3", "60°", "√3/2", "1/2"],
                ["π/2", "90°", "1", "0"], ["π", "180°", "0", "−1"],
                ["3π/2", "270°", "−1", "0"], ["2π", "360°", "0", "1"],
            ],
        )],
    },
    ("informatica-reti", 34): {
        "title": "Sala server e infrastruttura di rete",
        "blocks": [
            {"type": "paragraph", "text": "Una sala server concentra sistemi di elaborazione, memoria, apparati di rete e alimentazione. Gli armadi rack organizzano i dispositivi e ne facilitano collegamenti, raffreddamento, manutenzione e controllo degli accessi."},
        ],
    },
})

PAGE_TITLES: dict[tuple[str, int], str] = {
    ("fisica-cinematica", 17): "Direzione della velocità tangenziale",
    ("fisica-cinematica", 19): "Direzione dell’accelerazione centripeta",
    ("fisica-cinematica", 23): "Conversioni fra gradi e radianti: esercizi",
    ("fisica-cinematica", 26): "Caduta libera e moto uniformemente accelerato",
    ("fisica-cinematica", 28): "Gittata nel moto parabolico",
    ("fisica-cinematica", 30): "Periodo e pulsazione del moto armonico",
    ("fisica-cinematica", 31): "Esempi di moto armonico",
    ("logica-attenzione", 7): "Soluzione di una sequenza pari-dispari",
    ("logica-equivalenze-2", 5): "Operazioni con le misure angolari",
    ("logica-serie-tabelle", 4): "Calcolo percentuale su una tabella retributiva",
    ("test-logica-2024-08-02", 6): "Quesiti 26-29",
    ("test-logica-verbale-2024-07-19", 3): "Quesiti 18-24",
}

PAGE_SKIPS: set[tuple[str, int]] = {
    ("fisica-forze", 1),
    ("fisica-statica", 1),
    ("informatica-base", 1),
    ("informatica-reti", 15),
}


def load_resources() -> list[dict]:
    script = "import('./study-paths.js').then(m=>process.stdout.write(JSON.stringify(m.allStudyResources)))"
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


COMMON_REPAIRS = {
    "®gni": "Ogni",
    "pu�": "può",
    "Pu�": "Può",
    "pi�": "più",
    "Pi�": "Più",
    "cos�": "così",
    "Cos�": "Così",
    "perch�": "perché",
    "Perch�": "Perché",
    "poich�": "poiché",
    "Poich�": "Poiché",
    "affinch�": "affinché",
    "finch�": "finché",
    "nonch�": "nonché",
    "bench�": "benché",
    "n�": "né",
    "N�": "Né",
    "s�": "sì",
    "S�": "Sì",
    "gi�": "già",
    "Gi�": "Già",
    "l�": "lì",
    "L�": "Lì",
    "citt�": "città",
    "et�": "età",
    "met�": "metà",
    "unit�": "unità",
    "quantit�": "quantità",
    "qualit�": "qualità",
    "propriet�": "proprietà",
    "attivit�": "attività",
    "velocit�": "velocità",
    "capacit�": "capacità",
    "possibilit�": "possibilità",
    "probabilit�": "probabilità",
    "modalit�": "modalità",
    "difficolt�": "difficoltà",
    "libert�": "libertà",
    "societ�": "società",
    "realt�": "realtà",
    "elettricit�": "elettricità",
    "identit�": "identità",
    "continuit�": "continuità",
    "necessit�": "necessità",
    "validit�": "validità",
    "stabilit�": "stabilità",
    "densit�": "densità",
    "intensit�": "intensità",
    "metter�": "metterà",
    "sar�": "sarà",
    "avr�": "avrà",
    "far�": "farà",
    "dar�": "darà",
    "andr�": "andrà",
    "potr�": "potrà",
    "dovr�": "dovrà",
    "verr�": "verrà",
    "porter�": "porterà",
    "risulter�": "risulterà",
    "cio�": "cioè",
    "Cio�": "Cioè",
    "qual �": "qual è",
    "Qual �": "Qual è",
    "non �": "non è",
    "Non �": "Non è",
    "che �": "che è",
    "Che �": "Che è",
    "si �": "si è",
    "Si �": "Si è",
    "ed �": "ed è",
    "� un": "è un",
    "� una": "è una",
    "� il": "è il",
    "� la": "è la",
    "� lo": "è lo",
    "� l’": "è l’",
    "� l'": "è l’",
    "� stato": "è stato",
    "� stata": "è stata",
    "� possibile": "è possibile",
    "� necessario": "è necessario",
    "� detta": "è detta",
    "� detto": "è detto",
    "� definita": "è definita",
    "� definito": "è definito",
    "� uguale": "è uguale",
    "� maggiore": "è maggiore",
    "� minore": "è minore",
    "� rappresentato": "è rappresentato",
    "� rappresentata": "è rappresentata",
    "� formato": "è formato",
    "� formata": "è formata",
    "� costituito": "è costituito",
    "� costituita": "è costituita",
    "� chiamato": "è chiamato",
    "� chiamata": "è chiamata",
    "� presente": "è presente",
    "� pari": "è pari",
    "� direttamente": "è direttamente",
    "� invece": "è invece",
    "� quindi": "è quindi",
    "� sempre": "è sempre",
    "� anche": "è anche",
    "� tradizionalmente": "è tradizionalmente",
}


def repair_text(value: str) -> str:
    text = (
        value.replace("\u00a0", " ")
        .replace("\u00ad", "")
        .replace("\u0091", "‘")
        .replace("\u0092", "’")
        .replace("\u0093", "“")
        .replace("\u0094", "”")
        .replace("\u0095", "•")
        .replace("\u0096", "-")
        .replace("\u0097", "-")
    )
    text = re.sub(rf"(?m)^\s*{UNKNOWN}\s+", "• ", text)
    text = re.sub(
        rf"\b(l|d|all|dall|dell|nell|sull|coll|quest|un|anch|com){UNKNOWN}(?=[A-Za-zÀ-ÿ])",
        lambda match: f"{match.group(1)}’",
        text,
        flags=re.IGNORECASE,
    )
    for broken, fixed in COMMON_REPAIRS.items():
        text = text.replace(broken, fixed)
    text = re.sub(rf"\b([A-Za-zÀ-ÿ]*it){UNKNOWN}\b", r"\1à", text, flags=re.IGNORECASE)
    text = re.sub(rf"\b([A-Za-zÀ-ÿ]+r){UNKNOWN}\b", r"\1à", text, flags=re.IGNORECASE)
    text = re.sub(rf"\b([A-Za-zÀ-ÿ]+ch){UNKNOWN}\b", r"\1é", text, flags=re.IGNORECASE)
    text = re.sub(rf"(?<!\w){UNKNOWN}(?=\s|[.,;:!?)]|$)", "è", text)
    text = re.sub(rf"(?<=\w){UNKNOWN}(?=\w)", "’", text)
    text = re.sub(rf"(?<=\w){UNKNOWN}(?=\s|[.,;:!?)]|$)", "à", text)
    text = text.replace(UNKNOWN, "’")
    return re.sub(r"[ \t]+", " ", text).strip()


def normalized_line(value: str) -> str:
    return re.sub(r"\W+", " ", value, flags=re.UNICODE).strip().lower()


def clean_lines(text: str, repeated: set[str]) -> list[str]:
    lines: list[str] = []
    for raw in repair_text(text).splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        line = re.sub(r"\s*https?\s*:\s*/+\S+.*$", "", line, flags=re.IGNORECASE).strip()
        if not line or normalized_line(line) in repeated:
            continue
        if re.search(r"\.{5,}", line):
            continue
        if re.fullmatch(r"(?:pagina\s+)?\d+(?:\s*/\s*\d+)?", line, re.IGNORECASE):
            continue
        lines.append(line)
    return lines


def is_heading(line: str) -> bool:
    value = line.strip(" •-\t")
    if not value or len(value) > 120:
        return False
    words = value.split()
    if len(words) > 14:
        return False
    if re.match(r"^(?:capitolo|lezione|unità|parte|modulo|\d+(?:\.\d+)*[.)-])\s+", value, re.IGNORECASE):
        return True
    letters = [character for character in value if character.isalpha()]
    if letters and sum(character.isupper() for character in letters) / len(letters) > 0.78:
        return True
    if value.endswith("?") and len(words) <= 10:
        return True
    return len(words) <= 7 and not re.search(r"[.;:]$", value) and value[:1].isupper()


def blocks_from_lines(lines: list[str]) -> tuple[str | None, list[dict]]:
    if not lines:
        return None, []
    title: str | None = lines[0] if is_heading(lines[0]) else None
    source = lines[1:] if title else lines
    blocks: list[dict] = []
    paragraph: list[str] = []
    bullets: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph:
            return
        text = " ".join(paragraph)
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)
        if text:
            blocks.append({"type": "paragraph", "text": text})
        paragraph.clear()

    def flush_bullets() -> None:
        if bullets:
            blocks.append({"type": "list", "items": bullets.copy()})
            bullets.clear()

    for line in source:
        bullet = re.match(r"^(?:[•●▪◦]|[-–—]|\d+[.)])\s*(.+)$", line)
        if bullet:
            flush_paragraph()
            bullets.append(bullet.group(1).strip())
            continue
        if bullets and not is_heading(line):
            # PDF extraction often wraps one list item over multiple lines.
            # Keep the continuation with its bullet instead of turning it into
            # a disconnected paragraph in the digital lesson.
            if not re.search(r"[.!?;:]$", bullets[-1]) and not line.startswith(("=", "→")):
                bullets[-1] = f"{bullets[-1]} {line}".strip()
                continue
        flush_bullets()
        if is_heading(line):
            flush_paragraph()
            blocks.append({"type": "heading", "text": line.strip()})
            continue
        if paragraph and paragraph[-1].endswith("-") and line[:1].islower():
            paragraph[-1] = paragraph[-1][:-1] + line
        else:
            paragraph.append(line)
    flush_bullets()
    flush_paragraph()
    return title, blocks


def inferred_section_title(blocks: list[dict], position: int) -> str:
    if blocks and blocks[0].get("type") == "heading":
        return blocks.pop(0).get("text") or f"Sezione {position}"
    for block in blocks:
        text = block.get("text") or " ".join(block.get("items", []))
        words = re.findall(r"\S+", text)
        if words:
            candidate = " ".join(words[:10]).strip(" ,.;:-")
            return candidate + ("…" if len(words) > 10 else "")
    return f"Schema ed esempio {position}"


def repeated_lines(page_texts: list[str]) -> set[str]:
    counter: Counter[str] = Counter()
    for text in page_texts:
        seen = {
            normalized_line(line)
            for line in repair_text(text).splitlines()
            if 2 <= len(normalized_line(line)) <= 80
        }
        counter.update(seen)
    threshold = max(3, round(len(page_texts) * 0.42))
    return {line for line, count in counter.items() if count >= threshold}


def ocr_page(page, extracted: str) -> str:
    """Recover pages made of images or outlined text instead of PDF text."""
    extracted_words = len(re.findall(r"\b\w+\b", extracted))
    if extracted_words >= 25 or not TESSERACT.exists() or not (TESSDATA / "ita.traineddata").exists():
        return extracted
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
        temporary = Path(handle.name)
    try:
        page.to_image(resolution=210).original.save(temporary, "PNG")
        result = subprocess.run(
            [str(TESSERACT), str(temporary), "stdout", "--tessdata-dir", str(TESSDATA), "-l", "ita", "--psm", "6"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        recognized = repair_text(result.stdout)
        recognized_words = len(re.findall(r"\b\w+\b", recognized))
        return recognized if recognized_words >= max(8, extracted_words + 4) else extracted
    finally:
        temporary.unlink(missing_ok=True)


def useful_image_boxes(page) -> list[tuple[float, float, float, float]]:
    """Return actual figures, excluding page-sized scans and decorative marks."""
    page_area = float(page.width * page.height)
    boxes: list[tuple[float, float, float, float]] = []
    word_count = len(page.extract_words())
    for item in page.images:
        box = (float(item["x0"]), float(item["top"]), float(item["x1"]), float(item["bottom"]))
        width, height = box[2] - box[0], box[3] - box[1]
        ratio = (width * height) / page_area if page_area else 0
        if width < 75 or height < 55 or ratio < 0.015 or ratio > 0.68:
            continue
        if word_count <= 5 and ratio > 0.55:
            continue
        boxes.append(box)
    return boxes


def visual_score(page, text: str) -> float:
    boxes = useful_image_boxes(page)
    if not boxes:
        return 0
    largest = max((box[2] - box[0]) * (box[3] - box[1]) for box in boxes)
    keyword_bonus = 4 if re.search(r"\b(esempio|schema|grafico|diagramma|figura|tabella|formula|equazione)\b", repair_text(text), re.IGNORECASE) else 0
    return largest / 5000 + len(boxes) * 2 + keyword_bonus


def select_visual_pages(pages, page_texts: list[str], limit: int) -> list[int]:
    candidates = [
        (index, visual_score(page, page_texts[index]))
        for index, page in enumerate(pages)
        if visual_score(page, page_texts[index]) >= 2.5
    ]
    if len(candidates) <= limit:
        return [index for index, _ in candidates]
    chosen: set[int] = set()
    for index, _ in sorted(candidates, key=lambda item: item[1], reverse=True):
        if all(abs(index - other) > 1 for other in chosen):
            chosen.add(index)
        if len(chosen) >= max(2, limit // 2):
            break
    ordered = [index for index, _ in candidates if index not in chosen]
    remaining = limit - len(chosen)
    if remaining > 0 and ordered:
        for position in range(remaining):
            chosen.add(ordered[round(position * (len(ordered) - 1) / max(1, remaining - 1))])
    return sorted(chosen)[:limit]


def render_visual(page, resource_id: str, page_number: int) -> str:
    filename = f"{resource_id}-figure-p{page_number}.jpg"
    target = VISUALS / filename
    if not target.exists():
        box = max(useful_image_boxes(page), key=lambda item: (item[2] - item[0]) * (item[3] - item[1]))
        margin = 12
        crop = (
            max(0, box[0] - margin),
            max(0, box[1] - margin),
            min(float(page.width), box[2] + margin),
            min(float(page.height), box[3] + margin),
        )
        image = page.crop(crop).to_image(resolution=150).original.convert("RGB")
        image.save(target, "JPEG", quality=82, optimize=True, progressive=True)
    return f"study-content/visuals/{filename}"


def build_resource(resource: dict) -> dict:
    source = ROOT / resource["file"]
    with pdfplumber.open(source) as document:
        pages = list(document.pages)
        page_texts = [ocr_page(page, page.extract_text() or "") for page in pages]
        repeated = repeated_lines(page_texts)
        limit = 4 if len(pages) <= 12 else 6 if len(pages) <= 30 else 8
        visual_indexes = set(select_visual_pages(pages, page_texts, limit))
        sections: list[dict] = []
        for index, text in enumerate(page_texts):
            page_key = (resource["id"], index + 1)
            if page_key in PAGE_SKIPS:
                continue
            override = PAGE_OVERRIDES.get(page_key)
            if override:
                section = json.loads(json.dumps({"id": f"section-{index + 1}", **override}, ensure_ascii=False))
                title = section["title"]
            else:
                lines = clean_lines(text, repeated)
                title, blocks = blocks_from_lines(lines)
                if not blocks and index not in visual_indexes:
                    continue
                section = {
                    "id": f"section-{index + 1}",
                    "title": title or inferred_section_title(blocks, len(sections) + 1),
                    "blocks": blocks,
                }
            if page_key in PAGE_TITLES:
                section["title"] = PAGE_TITLES[page_key]
                title = section["title"]
            if index in visual_indexes:
                section["visual"] = render_visual(pages[index], resource["id"], index + 1)
                section["visualAlt"] = f"Schema ed esempio visuale: {title or resource['title']}"
            sections.append(section)

    def block_text(block: dict) -> str:
        return " ".join(
            [block.get("text", ""), *block.get("items", []), *block.get("headers", []), *(cell for row in block.get("rows", []) for cell in row)]
        )

    word_count = sum(
        len(re.findall(r"\b\w+\b", block_text(block)))
        for section in sections
        for block in section["blocks"]
    )
    remaining = sum(
        (section["title"] + " " + " ".join(block_text(block) for block in section["blocks"])).count(UNKNOWN)
        for section in sections
    )
    return {
        "id": resource["id"],
        "title": resource["title"],
        "pageCount": resource.get("pages", len(sections)),
        "wordCount": word_count,
        "visualCount": sum(1 for section in sections if section.get("visual")),
        "sections": sections,
        "remainingBrokenCharacters": remaining,
    }


def main() -> int:
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    VISUALS.mkdir(parents=True, exist_ok=True)
    all_resources = [resource for resource in load_resources() if resource["type"] in {"pdf", "test"}]
    selected_ids = set(sys.argv[1:])
    resources = [resource for resource in all_resources if not selected_ids or resource["id"] in selected_ids]
    if selected_ids - {resource["id"] for resource in all_resources}:
        raise SystemExit(f"Lezioni sconosciute: {', '.join(sorted(selected_ids - {resource['id'] for resource in all_resources}))}")
    manifest_by_id: dict[str, dict] = {}
    manifest_path = OUTPUT / "manifest.json"
    if selected_ids and manifest_path.exists():
        manifest_by_id = {item["id"]: item for item in json.loads(manifest_path.read_text(encoding="utf-8"))}
    for index, resource in enumerate(resources, start=1):
        content = build_resource(resource)
        target = OUTPUT / f"{resource['id']}.json"
        target.write_text(json.dumps(content, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        manifest_by_id[content["id"]] = {key: content[key] for key in ("id", "title", "pageCount", "wordCount", "visualCount", "remainingBrokenCharacters")}
        print(f"[{index:02d}/{len(resources)}] {resource['id']}: {content['wordCount']} parole, {content['visualCount']} visuali")
    manifest = [manifest_by_id[resource["id"]] for resource in all_resources]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Digitalizzati {len(resources)} documenti: {sum(item['wordCount'] for item in manifest)} parole, {sum(item['visualCount'] for item in manifest)} esempi visuali.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
