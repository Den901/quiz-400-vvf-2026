import assert from 'node:assert/strict';
import test from 'node:test';

import {
  applyLearningOutcome,
  selectAdaptiveQuestions,
  selectRotatingQuestions
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
