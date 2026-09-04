import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';

const source = await readFile(new URL('../../app.js', import.meta.url), 'utf8');
const cloudStyles = await readFile(new URL('../../styles-cloud.css', import.meta.url), 'utf8');
const themeStyles = await readFile(new URL('../../styles-theme.css', import.meta.url), 'utf8');
const extraStyles = await readFile(new URL('../../styles-extra.css', import.meta.url), 'utf8');

test('quiz per materia consente di scorrere senza cambiare lo stato delle domande', () => {
  assert.match(source, /data-study-browse="-1"/);
  assert.match(source, /data-study-browse="1"/);
  const functionBody = source.match(/function browseStudyQuestion\(direction\)\{(.+?)\}\nfunction/s)?.[1] || '';
  assert.match(functionBody, /quiz\.index=target/);
  assert.doesNotMatch(functionBody, /progressFor|history\[[^\]]+\]\s*=|rememberSubjectCursor|persist/);
  assert.match(extraStyles, /\.study-question-browser/);
});

test('moderatore vede dashboard e prove ma non i controlli distruttivi', () => {
  assert.match(source, /data-dashboard-nav/);
  assert.match(source, /currentUser\?\.role==='moderator'/);
  assert.match(source, /data-cloud-role-select/);
  assert.match(source, /data-cloud-user-search/);
  assert.match(source, /if\(currentUser\?\.role==='moderator'\)details\.querySelectorAll\('\[data-delete-dashboard-attempt\]'/);
  assert.match(source, /async function refreshCurrentRole\(\)/);
  assert.match(source, /visibilitychange/);
  assert.match(themeStyles, /dashboard-candidate-details\[open\]>summary/);
});

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

test('daily leaderboard does not force a horizontal scrollbar on desktop and tablet', () => {
  assert.match(cloudStyles, /@media \(min-width:700px\)\{\.daily-ranking\{overflow-x:visible\}/);
  assert.match(cloudStyles, /daily-ranking-head\.admin,[^{]+\{[^}]*min-width:0/);
  assert.match(cloudStyles, /daily-cutoff-line\.admin\{min-width:0/);
});

test('admin candidate dropdown exposes daily history and guarded deletion', () => {
  assert.match(source, /dashboard-candidate-details/);
  assert.match(source, /dashboard\/candidates\/\$\{encodeURIComponent\(candidate\.id\)\}\/challenges/);
  assert.match(source, /data-delete-dashboard-attempt/);
  assert.match(source, /Eliminare definitivamente questa prova/);
});
