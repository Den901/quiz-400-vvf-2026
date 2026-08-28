import assert from 'node:assert/strict';
import test from 'node:test';

import {italyChallengeReminderMoment,normalizeChallengeReminderHistory,shouldShowChallengeReminder} from '../../challenge-reminders.js';

test('le tre fasce giornaliere seguono l ora italiana',()=>{
  assert.equal(italyChallengeReminderMoment('2026-08-28T04:00:00Z').slot,'morning');
  assert.equal(italyChallengeReminderMoment('2026-08-28T09:59:00Z').slot,'morning');
  assert.equal(italyChallengeReminderMoment('2026-08-28T10:00:00Z').slot,'midday');
  assert.equal(italyChallengeReminderMoment('2026-08-28T15:59:00Z').slot,'midday');
  assert.equal(italyChallengeReminderMoment('2026-08-28T16:00:00Z').slot,'evening');
  assert.equal(italyChallengeReminderMoment('2026-08-28T21:59:00Z').slot,'evening');
  assert.equal(italyChallengeReminderMoment('2026-08-28T03:59:00Z'),null);
});

test('la memoria conserva una sola visualizzazione per fascia e solo per oggi',()=>{
  const history=normalizeChallengeReminderHistory({'2026-08-27':['evening'],'2026-08-28':['morning','morning','invalid']},'2026-08-28');
  assert.deepEqual(history,{'2026-08-28':['morning']});
});

test('il promemoria è riservato a chi non ha completato la sfida',()=>{
  const moment={date:'2026-08-28',slot:'midday'};
  assert.equal(shouldShowChallengeReminder({status:'not_started',date:'2026-08-28',moment}),true);
  assert.equal(shouldShowChallengeReminder({status:'active',date:'2026-08-28',moment}),true);
  assert.equal(shouldShowChallengeReminder({status:'completed',date:'2026-08-28',moment}),false);
  assert.equal(shouldShowChallengeReminder({status:'not_started',date:'2026-08-28',moment,seenSlots:['midday']}),false);
  assert.equal(shouldShowChallengeReminder({status:'not_started',date:'2026-08-28',moment,completedDates:['2026-08-28']}),false);
  assert.equal(shouldShowChallengeReminder({status:'not_started',date:'2026-08-27',moment}),false);
});
