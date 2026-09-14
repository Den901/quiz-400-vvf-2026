"""Recover the supplied PDF's missing Unicode mapping from identical Arial glyphs."""
import io,json,re,sys
from pathlib import Path
import pymupdf
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
info='--informatica' in sys.argv
SOURCE=Path(sys.argv[1])
doc=pymupdf.open(SOURCE)
def signature(font,name):
    glyph=font['glyf'][name]
    coords,ends,flags=glyph.getCoordinates(font['glyf'])
    return (tuple(map(tuple,coords)),tuple(ends),tuple(flags))
known={}
for name in ['arial.ttf','arialbd.ttf','ariali.ttf','arialbi.ttf']:
    font=TTFont('C:/Windows/Fonts/'+name)
    for code,glyph in font.getBestCmap().items():
        known.setdefault(signature(font,glyph),chr(code))
maps={}
for xref,ext,kind,name,resource,encoding in {tuple(f) for page in doc for f in page.get_fonts()}:
    font=TTFont(io.BytesIO(doc.extract_font(xref)[3]))
    name=name.split('+')[-1]
    maps[name]={i:known.get(signature(font,glyph)) for i,glyph in enumerate(font.getGlyphOrder())}
    print(name,'matched',sum(v is not None for v in maps[name].values()),'of',len(maps[name]))
def decode(span):
    mapping=maps[span['font']]
    return ''.join(mapping.get(ord(c)) or ('\n' if c=='\n' else c) for c in span['text'])
pages=[]
for page in doc:
    spans=[]
    for block in page.get_text('dict')['blocks']:
        if block['type']!=0:continue
        for line in block['lines']:
            for span in line['spans']:
                spans.append({'bbox':span['bbox'],'text':decode(span)})
    pages.append(spans)
out=ROOT/('tmp/pdfs/informatica-extracted.json' if info else 'tmp/pdfs/logica-extracted.json')
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf8')
rows=[]
for page_index,(page,spans) in enumerate(zip(doc,pages)):
    boundaries=sorted(set(round(draw['rect'].y0,3) for draw in page.get_drawings() if abs(draw['rect'].x0-37)<.1 and abs(draw['rect'].x1-67)<.1 and draw['rect'].height<.1))
    for number in [s for s in spans if s['bbox'][0]<60 and s['text'].isdigit()]:
        middle=(number['bbox'][1]+number['bbox'][3])/2
        top=max(y for y in boundaries if y<middle)
        if not boundaries:continue
        bottom=min((y for y in boundaries if y>middle),default=784)
        ends=[212,292.5,373,453.5,534,550] if info else [212,276.4,340.8,405.2,469.6,534,550]
        cells=[[] for _ in ends]
        for s in spans:
            x0,y0,x1,y1=s['bbox']
            if not top<(y0+y1)/2<bottom or x0<67:continue
            col=next((i for i,end in enumerate(ends) if (x0+x1)/2<end),None)
            if col is not None:cells[col].append(s)
        text=[' '.join(s['text'] for s in sorted(cell,key=lambda s:(s['bbox'][1],s['bbox'][0]))) for cell in cells]
        assert text[-1] in 'ABCDE' and len(text[-1])==1,(page_index,text)
        images=[b for b in page.get_text('dict')['blocks'] if b['type']==1 and top<(b['bbox'][1]+b['bbox'][3])/2<bottom]
        assert (text[0] or images),(page_index,number,top,bottom,text)
        if not text[0]:text[0]='Quesito illustrato: leggi il testo nella figura.'
        answers=[a for a in text[1:-1] if a]
        correct='ABCDE'.index(text[-1])
        assert correct<len(answers)
        rows.append({'number':int(number['text']),'text':text[0],'answers':answers,'correct':correct,'page':page_index+1,'images':[list(b['bbox']) for b in images]})
expected=1170 if info else 720
assert [q['number'] for q in rows]==list(range(1,expected+1)),(len(rows),[q['number'] for q in rows[-5:]])
(out.parent/('informatica-rows.json' if info else 'logica-rows.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
import unicodedata
def norm(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
# Append the actual passages instead of importing questions with dangling references.
passages={}
current=None
for s in pages[-1]:
    match=re.fullmatch(r'BRANO n\.(\d+)',s['text'])
    if match:current=int(match[1]);passages[current]=[]
    elif current is not None and 40<=s['bbox'][0] and s['bbox'][1]<790:passages[current].append(s['text'])
if not info:
    for q in rows:
        match=re.search(r'LEGGI IL BRANO n\.(\d+)',q['text'])
        if match:
            n=int(match[1]);assert passages.get(n)
            q['text']=' '.join(passages[n])+'\n\n'+q['text']
dataset=json.loads((ROOT/'quiz-dataset.json').read_text(encoding='utf8'))
index={}
for old in dataset:index.setdefault(norm(old['text']),[]).append(old)
duplicates=[];new=[]
for q in rows:
    matches=[old for old in index.get(norm(q['text']),[]) if sorted(map(norm,old['answers']))==sorted(map(norm,q['answers']))]
    (duplicates if matches else new).append(q)
print('Rows',len(rows),'duplicate candidates',len(duplicates),'new',len(new),'with images',sum(bool(q['images']) for q in rows))
print('New sample:',json.dumps(new[:3],ensure_ascii=False))
if '--import' not in sys.argv:sys.exit(0)
from PIL import Image,ImageChops,ImageStat
def pixels(data):
    return Image.open(io.BytesIO(data)).convert('RGB').resize((240,180))
def same_image(left,right):
    return max(ImageStat.Stat(ImageChops.difference(left,right)).mean)<2
image_cache={}
def old_pixels(q):
    path=ROOT/q.get('image','')
    if not path.is_file():return None
    if str(path) not in image_cache:image_cache[str(path)]=pixels(path.read_bytes())
    return image_cache[str(path)]
added=[];skipped=[];conflicts=[]
for q in rows:
    page=doc[q['page']-1]
    image_blocks=[b for b in page.get_text('dict')['blocks'] if b['type']==1 and list(b['bbox']) in q['images']]
    assert len(image_blocks)<=1,(q['number'],'multiple images')
    picture=pixels(image_blocks[0]['image']) if image_blocks else None
    candidates=index.get(norm(q['text']),[])
    if picture is not None:
        candidates=[old for old in candidates if old_pixels(old) is not None and same_image(picture,old_pixels(old))]
    else:candidates=[old for old in candidates if not old.get('image')]
    if candidates:
        skipped.append(q['number'])
        if not any(norm(old['answers'][old['correct']])==norm(q['answers'][q['correct']]) for old in candidates):conflicts.append(q['number'])
        continue
    prefix='info-pdf-' if info else 'logic-pdf-'
    imported={'id':prefix+str(q['number']).zfill(4),'category':'informatica' if info else 'logica','text':q['text'],'answers':q['answers'],'correct':q['correct'],'explanation':'','image':''}
    if image_blocks:
        image_name=('info-illustrated-' if info else 'logic-illustrated-')+str(q['number']).zfill(4)+'.png'
        target=ROOT/'quiz-images'/image_name
        Image.open(io.BytesIO(image_blocks[0]['image'])).convert('RGB').save(target)
        imported['image']='quiz-images/'+image_name
    dataset.append(imported);index.setdefault(norm(q['text']),[]).append(imported);added.append(imported['id'])
(ROOT/'quiz-dataset.json').write_text(json.dumps(dataset,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
images_path=ROOT/'quiz-images.json'
images=json.loads(images_path.read_text(encoding='utf8'))
images_path.write_text(json.dumps(list(dict.fromkeys(images+[q['image'] for q in dataset if q['image']])),ensure_ascii=False)+'\n',encoding='utf8')
report={'source':str(SOURCE),'total':len(rows),'added':added,'duplicates':skipped,'existing_answer_conflicts':conflicts}
(out.parent/('informatica-import-report.json' if info else 'logica-import-report.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('Imported',len(added),'skipped',len(skipped),'conflicting existing answers',conflicts)
