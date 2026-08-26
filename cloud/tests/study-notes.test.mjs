import test from 'node:test';
import assert from 'node:assert/strict';

import {
  chemistryNotes,
  computerScienceNotes,
  englishNotes,
  kingdomPrimeMinisters,
  kingsOfItaly,
  logicNotes,
  memoryTricks,
  notesSearchIndex,
  periodicElements,
  physicsNotes,
  popes,
  presidents,
  primeMinisters,
  transitionPrimeMinisters
} from '../../study-notes.js';
import {logicTopics} from '../../logic-topics.js';
import {subjectTopics} from '../../subject-topics.js';

test('la tavola periodica contiene i 118 elementi senza duplicati', () => {
  assert.equal(periodicElements.length, 118);
  assert.deepEqual(periodicElements.map(item => item.atomicNumber), Array.from({length: 118}, (_, index) => index + 1));
  assert.equal(new Set(periodicElements.map(item => item.symbol)).size, 118);
  assert.equal(periodicElements.find(item => item.symbol === 'Fe')?.name, 'Ferro');
  assert.equal(periodicElements.at(-1)?.name, 'Oganesson');
});

test('ogni elemento espone le proprietà chimiche richieste', () => {
  assert.ok(periodicElements.every(item => item.atomicMass && item.standardState && Array.isArray(item.valences)));
  const iron = periodicElements.find(item => item.symbol === 'Fe');
  assert.equal(iron.atomicMass, '55.84');
  assert.equal(iron.standardState, 'Solido');
  assert.equal(iron.meltingKelvin, 1811);
  assert.equal(iron.boilingKelvin, 3134);
  assert.deepEqual(iron.valences, [2, 3]);
  assert.equal(iron.oxidationStates, '+3, +2');
  assert.equal(iron.artificial, false);
  assert.equal(periodicElements.find(item => item.symbol === 'Br')?.standardState, 'Liquido');
  assert.equal(periodicElements.find(item => item.symbol === 'Hg')?.standardState, 'Liquido');
  assert.equal(periodicElements.find(item => item.symbol === 'Tc')?.artificial, true);
  assert.equal(periodicElements.find(item => item.symbol === 'Og')?.stateIsPredicted, true);
});

test('le cronologie terminano con le cariche attuali', () => {
  assert.deepEqual(presidents.at(-1), {name:'Sergio Mattarella', years:'2015–oggi', note:'Rieletto nel 2022.', current:true});
  assert.equal(popes.at(-1)?.name, 'Leone XIV');
  assert.equal(popes.at(-1)?.birthName, 'Robert Francis Prevost');
  assert.equal(primeMinisters.at(-1)?.name, 'Giorgia Meloni');
  assert.equal(presidents.filter(item => item.current).length, 1);
  assert.equal(popes.filter(item => item.current).length, 1);
  assert.equal(primeMinisters.filter(item => item.current).length, 1);
  assert.ok(primeMinisters.every(item => item.party && item.area));
  assert.equal(primeMinisters.at(-1)?.party, 'Fratelli d’Italia');
  assert.match(primeMinisters.at(-1)?.area, /Centro-destra/);
  assert.match(primeMinisters.find(item => item.name === 'Carlo Azeglio Ciampi')?.area, /tecnico/);
  assert.match(primeMinisters.find(item => item.name === 'Giuseppe Conte')?.area, /M5S–Lega/);
});

test('la storia copre Re e Presidenti del Consiglio dal 1861', () => {
  assert.equal(kingsOfItaly.length, 4);
  assert.equal(kingsOfItaly[0].name, 'Vittorio Emanuele II');
  assert.equal(kingsOfItaly.at(-1).name, 'Umberto II');
  assert.equal(kingdomPrimeMinisters.length, 27);
  assert.equal(kingdomPrimeMinisters[0].name, 'Camillo Benso di Cavour');
  assert.equal(kingdomPrimeMinisters.at(-1).name, 'Benito Mussolini');
  assert.match(kingdomPrimeMinisters.find(item => item.name === 'Urbano Rattazzi').area, /Sinistra storica/);
  assert.match(kingdomPrimeMinisters.find(item => item.name === 'Marco Minghetti').area, /Destra storica/);
  assert.deepEqual(transitionPrimeMinisters.map(item => item.name), ['Pietro Badoglio','Ivanoe Bonomi','Ferruccio Parri','Alcide De Gasperi']);
});

test('gli appunti seguono i 30 sottoargomenti effettivi del dataset', () => {
  assert.deepEqual(computerScienceNotes.map(item => item.id.replace('informatica-', '')), subjectTopics.informatica.map(item => item.id));
  assert.deepEqual(logicNotes.map(item => item.id.replace('logica-', '')), logicTopics.map(item => item.id));
  assert.deepEqual(englishNotes.map(item => item.id.replace('inglese-', '')), subjectTopics.inglese.map(item => item.id));
  assert.equal(computerScienceNotes.reduce((sum, item) => sum + item.quizCount, 0), 2119);
  assert.equal(logicNotes.reduce((sum, item) => sum + item.quizCount, 0), 5853);
  assert.equal(englishNotes.reduce((sum, item) => sum + item.quizCount, 0), 1551);
  assert.ok([...computerScienceNotes, ...logicNotes, ...englishNotes].every(section => section.items.length >= 8));
});

test('gli appunti coprono concetti, formule e aiuti mnemonici richiesti', () => {
  assert.ok(chemistryNotes.length >= 7);
  assert.ok(physicsNotes.length >= 9);
  assert.ok(chemistryNotes.flatMap(section => section.items).some(item => item.term === 'Legge di Lavoisier'));
  assert.ok(physicsNotes.flatMap(section => section.items).some(item => item.formula === 'V = RI'));
  assert.deepEqual(memoryTricks.map(item => item.id).sort(), ['papi', 'presidenti']);
  assert.ok(notesSearchIndex.some(item => item.title.includes('Archimede')));
  assert.ok(notesSearchIndex.some(item => item.title.includes('Mattarella')));
  assert.ok(notesSearchIndex.some(item => item.title.includes('Meloni') && item.text.includes('Centro-destra')));
  assert.ok(notesSearchIndex.some(item => item.title.includes('Ferro') && item.text.includes('massa atomica')));
  assert.ok(notesSearchIndex.some(item => item.title === 'Phishing'));
  assert.ok(notesSearchIndex.some(item => item.title === 'Contrapposta'));
  assert.ok(notesSearchIndex.some(item => item.title === 'Present perfect'));
  assert.ok(notesSearchIndex.some(item => item.title.includes('Cavour') && item.text.includes('Destra storica')));
  assert.ok(notesSearchIndex.some(item => item.title === 'Umberto II'));
});
