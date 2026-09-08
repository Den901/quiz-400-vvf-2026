import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';

function isAllCaps(value) {
  const letters = [...String(value || '')].filter(character => /\p{L}/u.test(character));
  if (letters.length < 8) return false;
  const uppercase = letters.filter(character =>
    character === character.toLocaleUpperCase('it-IT') &&
    character !== character.toLocaleLowerCase('it-IT')
  );
  return uppercase.length / letters.length > 0.9;
}

test('le domande di Storia importate non sono interamente in maiuscolo', async () => {
  const dataset = JSON.parse(await readFile(new URL('../../quiz-dataset.json', import.meta.url), 'utf8'));
  const importedHistory = dataset.filter(question =>
    question.category === 'storia' && String(question.id || '').startsWith('simone-history-')
  );

  assert.equal(importedHistory.length, 356);
  assert.deepEqual(importedHistory.filter(question => isAllCaps(question.text)), []);
  assert.deepEqual(importedHistory.flatMap(question => question.answers).filter(isAllCaps), []);
});
