import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import {classifySubjectQuestion,subjectTopics,topicDefinition} from '../../subject-topics.js';

const dataset=JSON.parse(await readFile(new URL('../../quiz-dataset.json',import.meta.url),'utf8'));
const expectedCounts={
 chimica:{materia:25,atomo:405,legami:360,reazioni:195,'moli-soluzioni':153,'acidi-basi':186,'stati-gas':65,organica:84,'bio-applicata':25,generale:179},
 fisica:{misure:183,cinematica:302,dinamica:333,energia:155,fluidi:179,termologia:316,'onde-ottica':112,elettromagnetismo:183,atomica:64,generale:177},
 informatica:{hardware:274,'sistemi-file':318,word:258,excel:214,'office-dati':201,reti:211,internet:183,sicurezza:122,'software-dati':156,generale:182},
 storia:{risorgimento:139,'italia-postunitaria':399,'eta-giolittiana':84,'prima-guerra':95,fascismo:143,'seconda-guerra':85,'repubblica-primi-anni':111,'repubblica-contemporanea':195,'storia-internazionale':32,generale:163},
 inglese:{'tempi-verbali':388,'modali-condizionali':63,pronomi:83,'nomi-articoli':105,'aggettivi-avverbi':64,preposizioni:159,'costruzione-frase':73,'phrasal-idioms':23,vocabolario:79,generale:514}
};

test('every supported subject question belongs to one selectable topic',()=>{
 for(const category of Object.keys(expectedCounts)){
  const questions=dataset.filter(question=>question.category===category),validIds=new Set(subjectTopics[category].map(topic=>topic.id));
  assert.equal(subjectTopics[category].length,10);
  for(const question of questions)assert.ok(validIds.has(classifySubjectQuestion(question)),`${question.id} has no valid ${category} topic`);
 }
});

test('the authorized history export is imported cleanly and without duplicates',()=>{
 const imported=dataset.filter(question=>String(question.id).startsWith('simone-history-'));
 assert.equal(imported.length,356);
 assert.equal(new Set(imported.map(question=>question.id)).size,imported.length);
 for(const question of imported){
  assert.equal(question.category,'storia');
  assert.ok(question.text.length>0);
  assert.ok(Array.isArray(question.answers)&&question.answers.length>=2);
  assert.ok(Number.isInteger(question.correct)&&question.correct>=0&&question.correct<question.answers.length);
  assert.doesNotMatch(`${question.text} ${question.answers.join(' ')} ${question.explanation}`,/<\/?[a-z][^>]*>|&(?:#\d+|#x[\da-f]+|\w+);|\uFFFD/i);
 }
});

test('topic counts cover the existing banks without changing any question',()=>{
 for(const category of Object.keys(expectedCounts)){
  const questions=dataset.filter(question=>question.category===category),counts=Object.fromEntries(subjectTopics[category].map(topic=>[topic.id,questions.filter(question=>classifySubjectQuestion(question)===topic.id).length]));
  assert.deepEqual(counts,expectedCounts[category]);
  assert.equal(Object.values(counts).reduce((sum,count)=>sum+count,0),questions.length);
 }
});

test('representative questions are routed to the requested areas',()=>{
 assert.equal(classifySubjectQuestion({category:'chimica',text:'Bilanciare la seguente equazione chimica',answers:[]}), 'reazioni');
 assert.equal(classifySubjectQuestion({category:'chimica',text:'Una soluzione ha pH uguale a 2',answers:[]}), 'acidi-basi');
 assert.equal(classifySubjectQuestion({category:'fisica',text:'Un corpo si muove a velocità costante',answers:[]}), 'cinematica');
 assert.equal(classifySubjectQuestion({category:'fisica',text:'La legge di Ohm descrive un circuito elettrico',answers:[]}), 'elettromagnetismo');
 assert.equal(classifySubjectQuestion({category:'informatica',text:'In Microsoft Excel quale formula somma le celle?',answers:[]}), 'excel');
 assert.equal(classifySubjectQuestion({category:'informatica',text:'Che cosa indica un indirizzo IP in una rete LAN?',answers:[]}), 'reti');
 assert.equal(classifySubjectQuestion({category:'storia',text:'Quale episodio concluse la spedizione dei Mille di Garibaldi?',answers:[]}), 'risorgimento');
 assert.equal(classifySubjectQuestion({category:'storia',text:'Quando avvenne il referendum istituzionale del 2 giugno?',answers:[]}), 'repubblica-primi-anni');
 assert.equal(classifySubjectQuestion({category:'inglese',text:'Choose the correct present perfect verb tense',answers:[]}), 'tempi-verbali');
 assert.equal(classifySubjectQuestion({category:'inglese',text:'Choose the correct preposition',answers:[]}), 'preposizioni');
 assert.equal(topicDefinition('chimica','reazioni')?.name,'Reazioni, leggi e bilanciamenti');
 assert.equal(topicDefinition('informatica','sicurezza')?.name,'Sicurezza informatica');
 assert.equal(topicDefinition('storia','prima-guerra')?.name,'Prima guerra mondiale');
 assert.equal(topicDefinition('inglese','phrasal-idioms')?.name,'Phrasal verbs ed espressioni');
});
