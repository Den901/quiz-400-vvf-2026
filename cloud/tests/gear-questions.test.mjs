import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {classifyLogicQuestion} from '../../logic-topics.js';

test('Flow chart e Ingranaggi non usano il limite compatto delle immagini',()=>{
 const css=readFileSync(new URL('../../styles-extra.css',import.meta.url),'utf8');
 assert.match(css,/\.question-image:is\(\[src\*="gear-"\],\[src\*="flow-"\]\):not\(\.mini\)\{width:min\(100%,760px\);max-width:100%;max-height:none;height:auto/);
});
test('100 ingranaggi: 50 originali più 50 nuovi con immagini e soluzioni',()=>{
 const dataset=JSON.parse(readFileSync(new URL('../../quiz-dataset.json',import.meta.url)));
 const questions=dataset.filter(q=>q.logicTopic==='ingranaggi'&&q.id.startsWith('gear-'));
 assert.equal(questions.length,100);
 assert.equal(questions.filter(q=>q.id.startsWith('gear-school-')).length,50);
 for(const q of questions){assert.equal(q.answers.length,4);assert.ok(q.correct>=0&&q.correct<4);assert.ok(q.explanation);assert.ok(existsSync(new URL('../../'+q.image,import.meta.url)))}
});
test('50 quesiti sulle ruote hanno figure, quattro risposte e soluzioni valide',()=>{
 const dataset=JSON.parse(readFileSync(new URL('../../quiz-dataset.json',import.meta.url)));
 const questions=dataset.filter(q=>q.id.startsWith('gear-logic-'));
 assert.equal(questions.length,50);
 for(const q of questions){
  assert.equal(q.category,'logica');assert.equal(classifyLogicQuestion(q),'ingranaggi');
  assert.equal(q.answers.length,4);assert.equal(new Set(q.answers).size,4);
  assert.ok(q.correct>=0&&q.correct<4);assert.ok(q.explanation.length>20);
  assert.ok(existsSync(new URL('../../'+q.image,import.meta.url)));
 }
});
test('50 flow chart conservano scenario, immagini, risposte e spiegazioni',()=>{
 const dataset=JSON.parse(readFileSync(new URL('../../quiz-dataset.json',import.meta.url)));
 const questions=dataset.filter(q=>q.id.startsWith('flow-logic-'));
 assert.equal(questions.length,50);
 for(const q of questions){
  assert.equal(classifyLogicQuestion(q),'flow-chart');assert.ok(q.text.includes('\n\n'));
  assert.equal(q.answers.length,4);assert.ok(q.correct>=0&&q.correct<4);
  assert.ok(q.explanation);assert.ok(existsSync(new URL('../../'+q.image,import.meta.url)));
 }
});
