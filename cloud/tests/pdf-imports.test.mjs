import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {classifyLogicQuestion} from '../../logic-topics.js';
import {classifySubjectQuestion} from '../../subject-topics.js';
const bank=JSON.parse(readFileSync(new URL('../../quiz-dataset.json',import.meta.url)));
test('PDF: importati solo nuovi quesiti con risposte e caratteri leggibili',()=>{
 const logic=bank.filter(q=>q.id.startsWith('logic-pdf-')),info=bank.filter(q=>q.id.startsWith('info-pdf-'));
 assert.equal(logic.length,334);assert.equal(info.length,429);
 assert.equal(logic.filter(q=>q.logicTopic==='ingranaggi').length,8);
 assert.equal(info.filter(q=>q.image).length,12);
 for(const q of [...logic,...info]){
  assert.ok(q.text);assert.ok(!/\uFFFD|[\u0000-\u0008]/.test(q.text));
  assert.ok(q.answers.length>=3&&q.answers.length<=5);assert.ok(q.correct>=0&&q.correct<q.answers.length);
  if(q.image)assert.ok(existsSync(new URL('../../'+q.image,import.meta.url)));
  if(q.category==='logica')assert.equal(classifyLogicQuestion(q),q.logicTopic);
  else assert.equal(classifySubjectQuestion(q),q.subjectTopic);
 }
});
test('le immagini si possono aprire con zoom senza inviare risposte',()=>{
 const app=readFileSync(new URL('../../app.js',import.meta.url),'utf8');
 assert.ok(app.includes("event.target.closest('img.question-image')"));
 assert.ok(app.includes('dialog.showModal()'));assert.ok(app.includes('Math.min(300,scale+delta)'));
});
