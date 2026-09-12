import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const questions=JSON.parse(readFileSync(new URL('../../quiz-dataset.json',import.meta.url),'utf8'));

test('le spiegazioni di Fisica e Chimica non contengono simboli persi',()=>{
 const damaged=questions.filter(question=>['fisica','chimica'].includes(question.category)&&(question.explanation?.includes('?')||question.explanation?.includes('\\')));
 assert.deepEqual(damaged.map(question=>question.id),[]);
});

test('ogni spiegazione scientifica resta sostanziale dopo la revisione',()=>{
 const tooShort=questions.filter(question=>['fisica','chimica'].includes(question.category)&&question.explanation&&question.explanation.length<100);
 assert.deepEqual(tooShort.map(question=>question.id),[]);
});
