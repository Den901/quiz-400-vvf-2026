import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source=readFileSync(new URL('../../app.js',import.meta.url),'utf8');
test('i quesiti disattivati hanno comandi distinti per correggere e riattivare',()=>{
 const fn=source.split('\n').find(line=>line.startsWith('function disabledQuestionCardMarkup('));
 const context=vm.createContext({esc:String,catName:String});
 vm.runInContext(fn,context);
 const html=context.disabledQuestionCardMarkup({questionId:'q123',question:{text:'Domanda',category:'storia'}});
 assert.ok(html.includes('data-correct-question="q123"'));
 assert.ok(html.includes('data-enable-question="q123"'));
 assert.ok(html.includes('Modifica risposta corretta'));
});
test('la revisione consente di modificare tutte le risposte',()=>{
 assert.ok(source.includes('name="answer"'));
 assert.ok(source.includes("answers:values.getAll('answer').map(String)"));
});
test('le impostazioni sono organizzate in sezioni a tendina esclusive',()=>{
 assert.ok(source.includes("details.className='settings-accordion-item'"));
 assert.ok(source.includes("if(other!==details)other.open=false"));
 assert.ok(source.includes('organizeSettingsAsAccordion()'));
});
test('gestione utenti lascia riepilogo e creazione visibili, con schede personali a tendina',()=>{
 assert.ok(source.includes('cloud-user-search-prominent'));
 assert.ok(source.includes('<form class="card admin-form cloud-create-user"'));
 assert.ok(source.includes('<section class="cloud-users-summary">'));
 assert.ok(source.includes('data-cloud-user-card'));
 assert.ok(source.includes('bindCloudUserAccordions()'));
 assert.ok(source.includes('data-generate-password'));
 assert.ok(source.includes('data-copy-temporary-password'));
 assert.ok(source.includes('data-cloud-challenge-required'));
 assert.ok(source.includes('daily_challenge_required:input.checked'));
});
test('correzione diretta è inclusa nelle segnalazioni e usa un pulsante compatto',()=>{
 assert.ok(source.includes('${directQuestionCorrectionMarkup()}'));
 assert.ok(source.includes('class="primary compact" type="submit">Apri quesito'));
 assert.equal((source.match(/<h2>Correzione risposte dei quesiti<\/h2>/g)||[]).length,0);
});
test('le tendine impostazioni non mostrano etichette numeriche generiche',()=>{
 assert.ok(source.includes("['[data-question-moderation-panel]','Segnalazioni quesiti']"));
 assert.ok(source.includes("['.cloud-settings','Portale, privacy e servizi cloud']"));
 assert.ok(!source.includes('`Sezione ${index+1}`'));
});
test('la cronologia rende tutti i risultati, anche oltre gli ultimi otto',()=>{
 const fn=source.split('\n').find(line=>line.startsWith('function sessionHistoryMarkup('));
 const context=vm.createContext({esc:String,sessionTypeLabel:String,catName:String});
 vm.runInContext(fn,context);
 const rows=Array.from({length:31},(_,i)=>({id:`s${i}`,type:`quiz-${i}`,at:'2026-09-12',score:i,correct:i,review:i>=26?[{}]:undefined}));
 const html=context.sessionHistoryMarkup(rows);
 assert.equal((html.match(/<article/g)||[]).length,31);
 assert.equal((html.match(/Rivedi domande/g)||[]).length,5);
 assert.ok(html.indexOf('quiz-30')<html.indexOf('quiz-0'));
});
test('le correzioni non mutano i quesiti originali o le prove già avviate',()=>{
 const context=vm.createContext({official:[{id:'q1',correct:0}],imported:[],questionCorrections:{q1:{correct:2,explanation:'Verificata'}}});
 const fn=source.split('\n').find(line=>line.startsWith('const allStoredQuestions='));
 vm.runInContext(fn+';globalThis.getQuestions=allStoredQuestions;',context);
 assert.equal(context.getQuestions()[0].correct,2);
 assert.equal(context.official[0].correct,0);
 const active=context.getQuestions()[0];
 context.questionCorrections.q1={correct:3};
 assert.equal(active.correct,2);
 assert.equal(context.getQuestions()[0].correct,3);
});
