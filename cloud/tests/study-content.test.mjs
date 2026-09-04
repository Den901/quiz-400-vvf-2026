import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import {fileURLToPath} from 'node:url';

import {classifyLogicQuestion,normalizedQuestionText} from '../../logic-topics.js';
import {classifySubjectQuestion} from '../../subject-topics.js';
import {checkpointQuestionPool,studyQuestionTopics} from '../../study-checkpoint.js';
import {allStudyResources,studyCoveredTopics,studyResourceById} from '../../study-paths.js';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'study-content/manifest.json'),'utf8'));
const questions=JSON.parse(fs.readFileSync(path.join(root,'quiz-dataset.json'),'utf8'));

test('tutte le dispense hanno una lezione digitale leggibile',()=>{
 const documents=allStudyResources.filter(resource=>['pdf','test'].includes(resource.type));
 assert.equal(documents.length,85);
 assert.equal(manifest.length,documents.length);
 assert.ok(manifest.reduce((sum,item)=>sum+item.wordCount,0)>166000);
 assert.ok(manifest.reduce((sum,item)=>sum+item.visualCount,0)>200);
 for(const resource of documents){
  const filename=path.join(root,'study-content',`${resource.id}.json`);
  assert.ok(fs.existsSync(filename),resource.id);
  const content=JSON.parse(fs.readFileSync(filename,'utf8'));
  assert.equal(content.id,resource.id);
  assert.ok(content.sections.length>0,resource.id);
  assert.equal('source' in content,false,`${resource.id}: riferimento PDF esposto`);
  const serialized=JSON.stringify(content);
  assert.equal(serialized.includes('\ufffd'),false,resource.id);
  assert.equal(/\(cid:\d+\)/i.test(serialized),false,`${resource.id}: codice CID non convertito`);
  assert.equal(/[]/.test(serialized),false,`${resource.id}: simbolo elenco non convertito`);
  assert.ok(content.sections.every(section=>section.visual||(section.blocks||[]).length),`${resource.id}: sezione vuota`);
  for(const section of content.sections)if(section.visual)assert.ok(fs.existsSync(path.join(root,section.visual)),section.visual);
 }
});

test('le tabelle che non erano estraibili sono state ricostruite come contenuto nativo',()=>{
 const generale=JSON.parse(fs.readFileSync(path.join(root,'study-content/chimica-generale.json'),'utf8'));
 const nomenclatura=JSON.parse(fs.readFileSync(path.join(root,'study-content/chimica-nomenclatura.json'),'utf8'));
 const reazioni=JSON.parse(fs.readFileSync(path.join(root,'study-content/chimica-reazioni.json'),'utf8'));
 const multipli=JSON.parse(fs.readFileSync(path.join(root,'study-content/logica-multipli-sottomultipli.json'),'utf8'));
 const cinematica=JSON.parse(fs.readFileSync(path.join(root,'study-content/fisica-cinematica.json'),'utf8'));
 for(const [content,sectionIds] of [[generale,['section-28']],[nomenclatura,['section-33','section-34','section-39','section-40','section-42']],[reazioni,['section-4']],[multipli,['section-1']],[cinematica,['section-24']]]){
  for(const id of sectionIds){
   const section=content.sections.find(item=>item.id===id);
   assert.ok(section,id);
   assert.ok(section.blocks.some(block=>block.type==='table'&&block.rows.length),id);
  }
 }
});

test('la verifica usa il capitolo corrente e non trascina le lezioni precedenti',()=>{
 assert.deepEqual(studyCoveredTopics(studyResourceById('storia-unita')),['risorgimento']);
 assert.deepEqual(studyCoveredTopics(studyResourceById('storia-destra-sinistra')),['italia-postunitaria']);
 assert.deepEqual(studyCoveredTopics(studyResourceById('fisica-fluidi')),['fluidi']);
 assert.deepEqual(studyQuestionTopics(studyResourceById('chimica-generale')),['materia','atomo','legami','moli-soluzioni']);
});

test('ogni capitolo campione trova quesiti reali pertinenti',()=>{
 for(const id of ['storia-unita','logica-sequenze','fisica-cinematica','chimica-acidi-basi','informatica-reti']){
  const resource=studyResourceById(id),pool=checkpointQuestionPool(resource,questions);
  assert.ok(pool.length>=5,`${id}: ${pool.length}`);
  assert.ok(pool.every(question=>questions.some(item=>String(item.id)===String(question.id))),id);
 }
});

test('i quesiti sono mirati al contenuto specifico della lezione',()=>{
 const postunitaria=checkpointQuestionPool(studyResourceById('storia-destra-sinistra'),questions);
 assert.ok(postunitaria.length>=5);
 assert.ok(postunitaria.every(question=>classifySubjectQuestion(question)==='italia-postunitaria'));

 const word=checkpointQuestionPool(studyResourceById('informatica-word'),questions);
 assert.ok(word.length>=5);
 assert.ok(word.every(question=>classifySubjectQuestion(question)==='word'));

 const probabilita=checkpointQuestionPool(studyResourceById('logica-probabilita'),questions);
 assert.ok(probabilita.length>=5);
 assert.ok(probabilita.every(question=>classifyLogicQuestion(question)==='calcolo'&&normalizedQuestionText(`${question.text} ${(question.answers||[]).join(' ')}`).includes('probabil')));

 const access=checkpointQuestionPool(studyResourceById('informatica-access'),questions);
 assert.ok(access.length>=5);
 assert.ok(access.every(question=>!/(access point|posta elettronica|e mail|email|outlook)/.test(normalizedQuestionText(`${question.text} ${(question.answers||[]).join(' ')}`))));
});

test('il sommario interno non cambia la rotta del portale e i PDF non entrano nel pacchetto server',()=>{
 const ui=fs.readFileSync(path.join(root,'study-content-ui.js'),'utf8');
 const docker=fs.readFileSync(path.join(root,'cloud/Dockerfile'),'utf8');
 const builder=fs.readFileSync(path.join(root,'cloud/build-server-release.py'),'utf8');
 assert.ok(ui.includes('data-study-section-target'));
 assert.equal(ui.includes('href="#lesson-'),false);
 assert.equal(docker.includes('study-materials ./study-materials'),false);
 assert.ok(docker.includes('study-materials/images ./study-materials/images'));
 assert.equal(builder.includes('(ROOT / "study-materials").rglob'),false);
 assert.ok(builder.includes('glob("*-figure-p*.jpg")'));
});
