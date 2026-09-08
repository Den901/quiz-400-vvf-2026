import assert from 'node:assert/strict';
import test from 'node:test';
import {additionalQuestionBankId,normalizeAdditionalQuestionBanks,questionAllowedInForty} from '../../additional-banks.js';

const nissolino={id:'simone-history-123',category:'storia'};
const contemporary={id:'modern-history-1990-2026-abc',category:'storia'};
const ordinary={id:'history-standard',category:'storia'};

test('le due banche aggiuntive sono riconosciute separatamente',()=>{
 assert.equal(additionalQuestionBankId(nissolino),'nissolinoHistory');
 assert.equal(additionalQuestionBankId(contemporary),'modernHistory');
 assert.equal(additionalQuestionBankId(ordinary),null);
});

test('gli interruttori filtrano solo le banche richieste nelle prove da 40',()=>{
 const settings=normalizeAdditionalQuestionBanks({nissolinoHistory:false,modernHistory:true});
 assert.equal(questionAllowedInForty(nissolino,settings),false);
 assert.equal(questionAllowedInForty(contemporary,settings),true);
 assert.equal(questionAllowedInForty(ordinary,settings),true);
});

test('le impostazioni mancanti mantengono entrambe le banche attive',()=>{
 assert.deepEqual(normalizeAdditionalQuestionBanks(null),{nissolinoHistory:true,modernHistory:true});
});
