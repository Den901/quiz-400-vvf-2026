import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';

const source=readFileSync(new URL('../../app.js',import.meta.url),'utf8');
const code=source.slice(source.indexOf('const questionRatingCache='),source.indexOf('function questionReportButtonMarkup('));
function run(kind,mode=null){
  const context=vm.createContext({Map,cloudMode:true,currentUser:{id:'u1'},quiz:{kind,mode},disabledQuestionIds:new Set(),esc:String,app:{},notify(){},cloudApi(){}});
  vm.runInContext(code,context);
  return vm.runInContext(`questionRatingMarkup({id:'q1'})`,context);
}
test('la scala appare nel quiz ordinato e guidato per materia',()=>{
  assert.match(run('study'),/Facile/);
  assert.match(run('guided'),/Media/);
  assert.match(run('guided'),/Difficile/);
});
test('la scala non appare in sfida, simulazioni, prova guidata 40 o Tutor',()=>{
  assert.equal(run('daily-challenge','daily-challenge'),'');
  assert.equal(run('exam'),'');
  assert.equal(run('guided','guided-exam'),'');
  assert.equal(run('guided','tutor'),'');
});
test('le soglie della media comunitaria sono coerenti',()=>{
  const context=vm.createContext({Map,cloudMode:true,currentUser:{id:'u1'},quiz:{kind:'study'},disabledQuestionIds:new Set(),esc:String,app:{},notify(){},cloudApi(){}});
  vm.runInContext(code,context);
  assert.equal(vm.runInContext('ratingDifficultyLabel(1.5)',context),'Facile');
  assert.equal(vm.runInContext('ratingDifficultyLabel(2)',context),'Media');
  assert.equal(vm.runInContext('ratingDifficultyLabel(2.6)',context),'Difficile');
});
test('una risposta corretta per materia assegna automaticamente Facile',()=>{
  const context=vm.createContext({Map,cloudMode:true,currentUser:{id:'u1'},quiz:{kind:'study'},disabledQuestionIds:new Set(),esc:String,app:{},notify(){},cloudApi(){}});
  vm.runInContext(code,context);
  assert.equal(vm.runInContext("shouldAutoRateEasy({id:'q1',correct:2},2)",context),true);
  assert.equal(vm.runInContext("shouldAutoRateEasy({id:'q1',correct:2},1)",context),false);
  vm.runInContext("quiz={kind:'daily-challenge',mode:'daily-challenge'}",context);
  assert.equal(vm.runInContext("shouldAutoRateEasy({id:'q1',correct:2},2)",context),false);
});
