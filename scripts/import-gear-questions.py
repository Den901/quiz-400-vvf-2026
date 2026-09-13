"""Import the user's gear exercises, verifying the companion CSV against the PDF."""
import csv
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[1])
def norm(value):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower())
rows = list(csv.DictReader((SOURCE / 'quiz_ruote_dentate.csv').open(encoding='utf-8-sig')))
pdf = PdfReader(SOURCE / '50_quiz_semplici_con_risposte.pdf')
assert len(rows) == 50 and len(pdf.pages) == 62
dataset_path = ROOT / 'quiz-dataset.json'
dataset = json.loads(dataset_path.read_text(encoding='utf-8'))
def key(q, image):
    return (norm(q['text']), tuple(sorted(norm(a) for a in q['answers'])), hashlib.sha256(image).hexdigest())
existing = set()
for q in dataset:
    image = ROOT / (q.get('image') or '')
    existing.add(key(q, image.read_bytes() if image.is_file() else b''))
added = 0
for i, row in enumerate(rows):
    page = pdf.pages[i + 1].extract_text()
    assert page.startswith(row['id_quiz'] + ' /')
    assert f"RISPOSTA CORRETTA: {row['risposta_corretta']}" in page
    assert norm(row['domanda']) in norm(page), row['id_quiz']
    answers = [row['opzione_' + letter] for letter in 'ABCD']
    assert all(norm(a) in norm(page) for a in answers)
    assert len(set(answers)) == 4
    image = (SOURCE / row['nome_file_immagine']).read_bytes()
    q = {'id': 'gear-logic-' + row['id_quiz'].lower(), 'category': 'logica',
         'logicTopic': 'figure', 'studyTopic': 'ruote-dentate',
         'text': row['domanda'], 'answers': answers,
         'correct': 'ABCD'.index(row['risposta_corretta']),
         'explanation': row['spiegazione'],
         'image': 'quiz-images/gear-' + row['id_quiz'].lower() + '.png'}
    signature = key(q, image)
    if signature in existing:
        continue
    assert not any(old['id'] == q['id'] for old in dataset), q['id']
    shutil.copyfile(SOURCE / row['nome_file_immagine'], ROOT / q['image'])
    dataset.append(q)
    existing.add(signature)
    added += 1
dataset_path.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
images_path = ROOT / 'quiz-images.json'
images = json.loads(images_path.read_text(encoding='utf-8'))
images = list(dict.fromkeys(images + [q['image'] for q in dataset if q['id'].startswith('gear-logic-')]))
images_path.write_text(json.dumps(images, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'PDF/CSV: 50 validated; imported {added}; gear total {sum(q["id"].startswith("gear-logic-") for q in dataset)}')
