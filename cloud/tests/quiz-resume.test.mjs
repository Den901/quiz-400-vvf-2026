import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';

const source = await readFile(new URL('../../app.js', import.meta.url), 'utf8');

test('daily challenge saves a selected answer immediately', () => {
  const functionBody = source.match(/function dailySelectAnswer\(choice\)\{([^}]+)\}/)?.[1] || '';
  assert.match(functionBody, /dailyCommitCurrent\(\)/);
  assert.match(functionBody, /saveDailyChallengeDraft\(\)/);
});

test('page exit preserves both daily and regular forty-question quizzes', () => {
  assert.match(source, /function preserveQuizBeforePageExit\(\)/);
  assert.match(source, /keepalive:true/);
  assert.match(source, /if\(isTimedFortyQuiz\(\)\)saveActiveQuiz\(\)/);
  assert.match(source, /window\.addEventListener\('pagehide',preserveQuizBeforePageExit\)/);
});

test('daily leaderboard separates candidates below the configured cutoff', () => {
  assert.match(source, /board\?\.theoreticalCutoff/);
  assert.match(source, /Number\(entry\.score\)<cutoff/);
  assert.match(source, /daily-cutoff-line/);
  assert.match(source, /Sotto lo sbarramento/);
});
