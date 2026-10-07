import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../../app.js',import.meta.url),'utf8');
const fn=source.slice(source.indexOf('function globalChallengeRankingMarkup('),source.indexOf('async function openGlobalChallengeRanking('));
const context=vm.createContext({esc:s=>String(s).replaceAll('<','&lt;'),fmtMetric:n=>String(n)});
vm.runInContext(fn,context);
test('classifica globale mostra fasce, soglia, posizione e nessun comando amministrativo',()=>{
 const html=context.globalChallengeRankingMarkup({participants:2,currentUser:{rank:2,averageScore:12},entries:[{rank:1,displayName:'A',username:'a',avatarUrl:'x',role:'admin',averageScore:32,attempts:10,band:'excellent'},{rank:2,displayName:'<B>',username:'b',avatarUrl:'x',role:'user',averageScore:12,attempts:11,band:'improving',isCurrentUser:true}],theoreticalCutoff:14.71});
 assert.ok(html.includes('Ottima preparazione'));assert.ok(html.includes('Da rafforzare'));assert.ok(html.includes('&lt;B>'));
 assert.equal((html.match(/global-ranking-cutoff/g)||[]).length,1);
 assert.ok(html.includes('La tua posizione'));assert.ok(!html.includes('Apri prova'));assert.ok(!html.includes('Elimina'));
});
test('sotto dieci prove compare il numero mancante anche a classifica vuota',()=>{
 const html=context.globalChallengeRankingMarkup({participants:0,currentUser:null,currentUserAttempts:9,entries:[],theoreticalCutoff:14.71});
 assert.ok(html.includes('ne mancano 1'));assert.ok(html.includes('Nessun candidato'));assert.ok(html.includes('14.71'));
 assert.ok(source.includes("button.textContent='Visualizza classifica globale'"));
});
