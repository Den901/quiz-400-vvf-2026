import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import {classifyLogicQuestion,defaultLogicPlan,isLongLogicPassage,logicPlanTotal,logicTopics,normalizeLogicPlan,normalizedQuestionText,selectLogicQuestionsByPlan} from '../../logic-topics.js';

const dataset=JSON.parse(await readFile(new URL('../../quiz-dataset.json',import.meta.url),'utf8'));
const logicQuestions=dataset.filter(question=>['logica','brani','insiemi'].includes(question.category));
const imported=logicQuestions.filter(question=>String(question.id).startsWith('logic-2026-'));

test('all logic questions belong to a selectable subsection',()=>{
 const ids=new Set(logicTopics.map(topic=>topic.id));
 assert.equal(logicTopics.length,10);
 assert.equal(logicQuestions.length,5853);
 for(const question of logicQuestions){
  const topic=classifyLogicQuestion(question);
  assert.ok(ids.has(topic),`${question.id} has invalid topic ${topic}`);
  if(question.category==='logica')assert.equal(topic,question.logicTopic);
 }
});

test('brani and insiemi are selectable types inside the logic macro subject',()=>{
 assert.equal(logicQuestions.filter(question=>classifyLogicQuestion(question)==='brani').length,648);
 assert.equal(logicQuestions.filter(question=>classifyLogicQuestion(question)==='insiemi').length,274);
 const figures=logicQuestions.filter(question=>classifyLogicQuestion(question)==='figure');
 assert.equal(figures.length,785);
 assert.equal(figures.filter(question=>question.image).length,765);
});

test('the imported bank excludes long passages and duplicate questions',()=>{
 assert.equal(imported.length,3224);
 assert.ok(imported.every(question=>!isLongLogicPassage(question)));
 const signatures=new Set();
 for(const question of imported){
  const signature=`${normalizedQuestionText(question.text)}|${question.answers.map(normalizedQuestionText).sort().join('|')}|${question.image||''}`;
  assert.ok(!signatures.has(signature),`duplicate ${question.id}`);
  signatures.add(signature);
 }
});

test('logic distribution always matches the selected logic total',()=>{
 for(const total of [0,1,11,12,40]){
  const plan=defaultLogicPlan(total);
  assert.equal(logicPlanTotal(plan),total);
  assert.deepEqual(normalizeLogicPlan(plan,total),plan);
 }
 const migrated=normalizeLogicPlan(undefined,12);
 assert.equal(logicPlanTotal(migrated),12);
});

test('a 12-question logic plan draws the exact requested amount from every subsection',()=>{
 const plan={deduzioni:2,serie:1,verbale:1,calcolo:1,figure:2,insiemi:1,relazioni:1,ordinamenti:1,brani:1,mista:1};
 const selected=selectLogicQuestionsByPlan(logicQuestions,plan,(source,count)=>source.slice(0,count));
 assert.equal(selected.length,12);
 const counts=Object.fromEntries(logicTopics.map(topic=>[topic.id,selected.filter(question=>classifyLogicQuestion(question)===topic.id).length]));
 assert.deepEqual(counts,plan);
});
