import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';

const source=readFileSync(new URL('../../app.js',import.meta.url),'utf8');
const functions=source.slice(source.indexOf('let questionReplyTimer='),source.indexOf('function moderationReportCardMarkup('));
function fixture(){
  const buttons=new Map();let popup=null;
  const document={visibilityState:'visible',activeElement:null,querySelector:()=>popup,
    createElement:()=>({dataset:{},querySelector(selector){if(!buttons.has(selector))buttons.set(selector,{focus(){},disabled:false,textContent:''});return buttons.get(selector)},remove(){popup=null}}),
    body:{append(node){popup=node}}};
  const calls=[];
  const report={id:'report-1',questionId:'q1',status:'dismissed',reply:'<script>bad</script>',question:{category:'storia',text:'Domanda originale',answers:['A','B'],correct:0,explanation:'Spiegazione'}};
  const context=vm.createContext({currentUser:{id:'u1'},cloudMode:true,quiz:null,document,Date,
    setInterval:()=>1,clearInterval:()=>{},catName:x=>x,esc:x=>String(x).replaceAll('<','&lt;').replaceAll('>','&gt;'),questionAnswerListMarkup:()=>'<ol>Risposte</ol>',
    cloudApi:async(url,options)=>{calls.push({url,options});return {replies:[report]}}});
  vm.runInContext(functions,context);
  return {context,calls,buttons,report,get popup(){return popup},run:()=>vm.runInContext('checkQuestionReplies()',context)};
}
test('il popup attende la fine del quiz e non interroga il server senza utente',async()=>{
  const f=fixture();f.context.quiz={finished:false};await f.run();assert.equal(f.calls.length,0);
  f.context.quiz=null;f.context.currentUser=null;await f.run();assert.equal(f.calls.length,0);
});
test('il popup mostra domanda, esito e risposta come testo sicuro',async()=>{
  const f=fixture();await f.run();assert.match(f.popup.innerHTML,/Domanda originale/);assert.match(f.popup.innerHTML,/Quesito verificato: è corretto/);assert.match(f.popup.innerHTML,/&lt;script&gt;/);assert.doesNotMatch(f.popup.innerHTML,/<script>/);
});
test('una segnalazione accolta avverte che la vecchia soluzione può essere errata',async()=>{
  const f=fixture();f.report.status='resolved';await f.run();assert.match(f.popup.innerHTML,/Segnalazione accolta/);assert.match(f.popup.innerHTML,/potrebbe essere errata/);
});
test('più tardi non segna la risposta come letta e sospende i popup',async()=>{
  const f=fixture();await f.run();f.buttons.get('[data-reply-later]').onclick();await f.run();assert.equal(f.popup,null);assert.equal(f.calls.length,1);
});
test('un cambio utente durante il caricamento non espone la risposta precedente',async()=>{
  const f=fixture();f.context.cloudApi=async()=>{f.context.currentUser={id:'u2'};return {replies:[f.report]}};await f.run();assert.equal(f.popup,null);
});
test('errore nella conferma di lettura lascia il popup aperto e permette di riprovare',async()=>{
  const f=fixture();await f.run();f.context.cloudApi=async()=>{throw Error('Rete non disponibile')};const button=f.buttons.get('[data-reply-read]');await button.onclick({currentTarget:button});assert.ok(f.popup);assert.equal(button.disabled,false);assert.equal(f.buttons.get('[data-reply-error]').textContent,'Rete non disponibile');
});
