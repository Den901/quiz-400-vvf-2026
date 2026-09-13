import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../../app.js',import.meta.url),'utf8');
test('Vai a raggiunge il numero richiesto senza segnare domande saltate',()=>{
 const context=vm.createContext({quiz:{kind:'study',pool:[{id:'a'},{id:'b'},{id:'c'}],index:0,history:{c:{choice:2}},selected:null},renderQuestion(){},notify(){}});
 vm.runInContext(source.split('\n').find(line=>line.startsWith('function goToStudyQuestion(')),context);
 assert.equal(context.goToStudyQuestion('3'),true);assert.equal(context.quiz.index,2);assert.equal(context.quiz.selected,2);
 assert.equal(Object.keys(context.quiz.history).length,1);
 for(const invalid of ['0','4','1.5','', 'abc']){assert.equal(context.goToStudyQuestion(invalid),false);assert.equal(context.quiz.index,2)}
 assert.equal(context.goToStudyQuestion('1'),true);assert.equal(context.quiz.selected,null);
 context.quiz.kind='exam';assert.equal(context.goToStudyQuestion('2'),false);
});
