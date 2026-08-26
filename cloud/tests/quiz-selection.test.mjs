import assert from 'node:assert/strict';
import test from 'node:test';

import {
  applyLearningOutcome,
  ensureGuidedPendingAnswers,
  guidedPendingAnswerAt,
  guidedResultRows,
  selectAdaptiveQuestions,
  selectOrderedQuestions,
  selectPersonalizedQuestions,
  selectRotatingQuestions,
  setGuidedPendingAnswer
} from '../../quiz-selection.js';

const questions = count => Array.from({length: count}, (_, index) => ({id: `q-${index + 1}`}));

test('la rotazione ordinaria non ripete domande prima di esaurire il gruppo', () => {
  const source = questions(100);
  let rotation = {};
  const served = new Set();

  for (let attempt = 0; attempt < 10; attempt += 1) {
    const result = selectRotatingQuestions(source, 10, rotation, `exam-${attempt}`);
    rotation = result.rotation;
    assert.equal(result.selected.length, 10);
    for (const question of result.selected) {
      assert.equal(served.has(question.id), false, `${question.id} è stata ripetuta prima della fine del ciclo`);
      served.add(question.id);
    }
  }

  assert.equal(served.size, 100);
});

test('il ripasso adattivo usa prima non note, ripetere e da fare', () => {
  const source = questions(40);
  const statuses = new Map(source.map((question, index) => [
    question.id,
    index < 5 ? 'unknown' : index < 15 ? 'review' : index < 30 ? 'unanswered' : 'known'
  ]));

  const result = selectAdaptiveQuestions(source, 10, {}, {}, 'priority', question => statuses.get(question.id));
  const selectedStatuses = result.selected.map(question => statuses.get(question.id));
  assert.equal(selectedStatuses.filter(status => status === 'unknown').length, 5);
  assert.equal(selectedStatuses.filter(status => status === 'review').length, 5);
  assert.equal(selectedStatuses.includes('known'), false);
});

test('con 900 domande note, le altre vengono ruotate senza ripetersi subito', () => {
  const source = questions(1000);
  const statuses = new Map(source.map((question, index) => [question.id, index < 900 ? 'known' : 'review']));
  let bucket = {};
  let knownRotation = {};
  const weakServed = new Set();

  for (let attempt = 0; attempt < 12; attempt += 1) {
    const result = selectAdaptiveQuestions(source, 8, bucket, knownRotation, `history-${attempt}`, question => statuses.get(question.id));
    bucket = result.bucket;
    knownRotation = result.knownRotation;
    assert.equal(result.selection.weak, 8);
    for (const question of result.selected) {
      assert.equal(weakServed.has(question.id), false, `${question.id} è ricomparsa troppo presto`);
      weakServed.add(question.id);
    }
  }

  assert.equal(weakServed.size, 96);
});

test('una risposta corretta passa subito a Le so e un errore a Da ripetere', () => {
  const progress = {attempts: 3, correct: 1, wrong: 2, skipped: 0, status: 'review'};
  applyLearningOutcome(progress, {correct: true}, true, '2026-08-17T10:00:00.000Z');
  assert.equal(progress.status, 'known');
  assert.equal(progress.correct, 2);

  applyLearningOutcome(progress, {correct: false}, true, '2026-08-17T10:01:00.000Z');
  assert.equal(progress.status, 'review');
  assert.equal(progress.wrong, 3);
});

test('simulazione e guidata condividono la stessa memoria anti-ripetizione', () => {
  const source = questions(1000);
  const statuses = new Map(source.map((question, index) => [question.id, index < 900 ? 'known' : 'unanswered']));
  const alreadyShown = source.slice(900, 908).map(question => question.id);
  let exposure = {version: 3, cycle: 1, seen: alreadyShown};

  const official = selectPersonalizedQuestions(source, 8, exposure, 'official', question => statuses.get(question.id), {adaptive: true});
  exposure = official.exposure;
  const guided = selectPersonalizedQuestions(source, 8, exposure, 'guided', question => statuses.get(question.id), {adaptive: true});

  const firstIds = new Set([...alreadyShown, ...official.selected.map(question => question.id)]);
  assert.equal(official.selection.weak, 8);
  assert.equal(guided.selection.weak, 8);
  assert.equal(guided.selected.some(question => firstIds.has(question.id)), false);
});

test('una domanda diventata Le so resta esclusa dal ciclo corrente', () => {
  const source = questions(120);
  const statuses = new Map(source.map(question => [question.id, 'review']));
  const first = selectPersonalizedQuestions(source, 12, {}, 'first', question => statuses.get(question.id), {adaptive: true});
  first.selected.forEach(question => statuses.set(question.id, 'known'));
  const second = selectPersonalizedQuestions(source, 12, first.exposure, 'second', question => statuses.get(question.id), {adaptive: true});
  const firstIds = new Set(first.selected.map(question => question.id));

  assert.equal(second.selected.some(question => firstIds.has(question.id)), false);
  assert.equal(second.selection.weak, 12);
});

test('il filtro per materia riprende dalla domanda successiva mantenendo l ordine', () => {
  const source = questions(8);
  const statuses = new Map(source.map((question, index) => [question.id, index % 2 ? 'review' : 'known']));
  const selected = selectOrderedQuestions(
    source,
    {version: 2, lastId: 'q-4', position: 3},
    question => statuses.get(question.id) === 'review'
  );

  assert.deepEqual(selected.map(question => question.id), ['q-6', 'q-8', 'q-2', 'q-4']);
});

test('il cursore per materia resta valido se la domanda ha cambiato stato', () => {
  const source = questions(6);
  const selected = selectOrderedQuestions(
    source,
    {version: 2, lastId: 'q-3', position: 2},
    question => ['q-1', 'q-4', 'q-5'].includes(question.id)
  );

  assert.deepEqual(selected.map(question => question.id), ['q-4', 'q-5', 'q-1']);
});

test('la prova guidata conserva una scelta provvisoria distinta per ogni domanda', () => {
  const pool = [
    {id: 'g-1', answers: ['A', 'B', 'C'], correct: 1},
    {id: 'g-2', answers: ['A', 'B', 'C'], correct: 0},
    {id: 'g-3', answers: ['A', 'B', 'C'], correct: 2}
  ];
  const state = {mode: 'guided-exam', pool, index: 0, history: {}, selected: null};

  setGuidedPendingAnswer(state, 0, 1);
  setGuidedPendingAnswer(state, 1, 2);

  assert.equal(guidedPendingAnswerAt(state, 0), 1);
  assert.equal(guidedPendingAnswerAt(state, 1), 2);
  assert.equal(guidedPendingAnswerAt(state, 2), null);
});

test('le scelte provvisorie vengono conteggiate alla consegna senza sovrascrivere quelle confermate', () => {
  const pool = [
    {id: 'g-1', answers: ['A', 'B'], correct: 1},
    {id: 'g-2', answers: ['A', 'B'], correct: 0},
    {id: 'g-3', answers: ['A', 'B'], correct: 1}
  ];
  const confirmed = {choice: 0, blank: false, correct: true, q: pool[1]};
  const state = {mode: 'guided-exam', pool, index: 2, history: {'g-2': confirmed}, selected: null};
  setGuidedPendingAnswer(state, 0, 1);
  setGuidedPendingAnswer(state, 1, 1);

  const rows = guidedResultRows(state);
  assert.deepEqual(rows.map(row => ({choice: row.choice, correct: row.correct, blank: row.blank})), [
    {choice: 1, correct: true, blank: false},
    {choice: 0, correct: true, blank: false},
    {choice: null, correct: false, blank: true}
  ]);
});

test('una prova guidata salvata dalla versione precedente recupera la scelta aperta', () => {
  const state = {
    mode: 'guided-exam',
    pool: [{id: 'old-1', answers: ['A', 'B'], correct: 0}],
    index: 0,
    history: {},
    selected: 1
  };

  assert.deepEqual(ensureGuidedPendingAnswers(state), [1]);
});
