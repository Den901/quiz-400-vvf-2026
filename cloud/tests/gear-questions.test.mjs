import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {classifyLogicQuestion} from '../../logic-topics.js';
test('50 quesiti sulle ruote hanno figure, quattro risposte e soluzioni valide',()=>{
 const dataset=JSON.parse(readFileSync(new URL('../../quiz-dataset.json',import.meta.url)));
 const questions=dataset.filter(q=>q.id.startsWith('gear-logic-'));
 assert.equal(questions.length,50);
 for(const q of questions){
  assert.equal(q.category,'logica');assert.equal(classifyLogicQuestion(q),'figure');
  assert.equal(q.answers.length,4);assert.equal(new Set(q.answers).size,4);
  assert.ok(q.correct>=0&&q.correct<4);assert.ok(q.explanation.length>20);
  assert.ok(existsSync(new URL('../../'+q.image,import.meta.url)));
 }
});
