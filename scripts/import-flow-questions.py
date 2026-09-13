"""Import supplied flow charts after checking every question/answer against its PDF."""
import json
import re
import shutil
import sys
from pathlib import Path
from pypdf import PdfReader
from importlib.util import spec_from_file_location
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[1])
gears = '--gears' in sys.argv[2:]
pdf_name = '50_quiz_ingranaggi_scuole_superiori.pdf' if gears else '50_quiz_logica.pdf'
prefix = 'gear-school-' if gears else 'flow-logic-'
image_prefix = 'gear-school-' if gears else 'flow-'
topic = 'ingranaggi' if gears else 'flow-chart'
def norm(value):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower())
rows = json.loads((SOURCE/'quiz.json').read_text(encoding='utf-8'))
pdf = PdfReader(SOURCE/pdf_name)
assert len(rows)==50 and len(pdf.pages)==57
solutions = '\n'.join(page.extract_text() for page in pdf.pages[51:])
dataset_path = ROOT/'quiz-dataset.json'
dataset = json.loads(dataset_path.read_text(encoding='utf-8'))
for q in dataset:
    if str(q['id']).startswith('gear-logic-'):
        q['logicTopic']='ingranaggi'
added=0
for i,row in enumerate(rows):
    page=pdf.pages[i+1].extract_text()
    assert page.startswith(row['id']+' ')
    assert norm(row['scenario']) in norm(page),row['id']
    assert norm(row['question']) in norm(page),row['id']
    pattern = row['id']+r'\s*·\s*'+row['answer']+r'\b' if gears else row['id']+r'\s*•\s*Risposta\s+'+row['answer']+r'\b'
    assert re.search(pattern,solutions)
    assert all(norm(a) in norm(page) for a in row['options'])
    assert len(row['options'])==len(set(row['options']))==4
    q={'id':prefix+row['id'].lower(),'category':'logica','logicTopic':topic,
       'text':row['scenario']+'\n\n'+row['question'],'answers':row['options'],
       'correct':'ABCD'.index(row['answer']),'explanation':row['explanation'],
       'image':'quiz-images/'+image_prefix+row['id'].lower()+'.png'}
    if any(old['id']==q['id'] for old in dataset):
        continue
    image=(SOURCE/row['image']).read_bytes()
    duplicates=[old for old in dataset if norm(old['text'])==norm(q['text']) and sorted(map(norm,old['answers']))==sorted(map(norm,q['answers']))]
    if any((ROOT/(old.get('image') or '')).is_file() and (ROOT/old['image']).read_bytes()==image for old in duplicates):
        continue
    shutil.copyfile(SOURCE/row['image'],ROOT/q['image'])
    dataset.append(q)
    added+=1
dataset_path.write_text(json.dumps(dataset,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
path=ROOT/'quiz-images.json'
images=json.loads(path.read_text(encoding='utf-8'))
path.write_text(json.dumps(list(dict.fromkeys(images+[q['image'] for q in dataset if q['id'].startswith(prefix)])),ensure_ascii=False)+'\n',encoding='utf-8')
print(f'PDF/JSON: 50 validated; imported {added}; topic {topic}')
