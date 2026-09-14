"""Import the authorized Office export saved from the public quiz exercise."""
import html,json,re,unicodedata,sys
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1])
questions=[]
for name in ['mininterno-office.json','mininterno-office-301.json']:
    questions+=json.loads((source/name).read_text(encoding='utf-8'))['esame']['quiz']
assert len(questions)==350 and len({q['id'] for q in questions})==350
def clean(value):return re.sub(r'\s+',' ',re.sub('<[^>]+>',' ',html.unescape(value))).strip()
def norm(value):
    value=re.sub(r"^Rispondere al seguente quesito facendo riferimento all'IMMAGINE dis\d+:\s*",'',clean(value))
    return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower())
bankfile=ROOT/'quiz-dataset.json'
bank=json.loads(bankfile.read_text(encoding='utf-8'))
index={}
for q in bank:
    if q['category']=='informatica':index.setdefault(norm(q['text']),[]).append(q)
added=[];duplicates=[];conflicts=[]
for q in questions:
    answers=[clean(q[f'risp{i}']) for i in range(1,int(q['numrisp'])+1)]
    correct=int(q['esatta'])-1
    assert len(answers)==4 and 0<=correct<4 and all(answers)
    # Equal prompts can offer different valid alternatives: only skip an identical answer set.
    existing=[old for old in index.get(norm(q['testo']),[]) if sorted(map(norm,old['answers']))==sorted(map(norm,answers))]
    if existing:
        duplicates.append(q['id'])
        if not any(norm(old['answers'][old['correct']])==norm(answers[correct]) for old in existing):conflicts.append(q['id'])
        continue
    filename=Path(q['img'].replace('\\','/')).name
    target=ROOT/'quiz-images'/('office-mininterno-'+Path(filename).stem+'.png')
    if not target.exists():
        with Image.open(source/filename) as im:im.convert('RGB').save(target)
    item={'id':'office-mininterno-'+q['id'],'category':'informatica','text':clean(q['testo']),
          'answers':answers,'correct':correct,'explanation':'','image':'quiz-images/'+target.name,'subjectTopic':'figure'}
    bank.append(item);index.setdefault(norm(q['testo']),[]).append(item);added.append(item['id'])
bankfile.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
imagesfile=ROOT/'quiz-images.json'
images=json.loads(imagesfile.read_text(encoding='utf-8'))
imagesfile.write_text(json.dumps(list(dict.fromkeys(images+[q['image'] for q in bank if q.get('image')])),ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'added':len(added),'duplicates':len(duplicates),'conflicts':conflicts,'office_total':sum(q['category']=='informatica' and bool(q.get('image')) for q in bank)}))
