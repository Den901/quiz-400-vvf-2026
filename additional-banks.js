export const DEFAULT_ADDITIONAL_QUESTION_BANKS={
 nissolinoHistory:true,
 modernHistory:true
};

export function normalizeAdditionalQuestionBanks(value){
 return Object.fromEntries(Object.entries(DEFAULT_ADDITIONAL_QUESTION_BANKS).map(([key,enabled])=>[key,typeof value?.[key]==='boolean'?value[key]:enabled]));
}

export function additionalQuestionBankId(question){
 const id=String(question?.id??'');
 if(id.startsWith('simone-history-'))return'nissolinoHistory';
 if(id.startsWith('modern-history-1990-2026-'))return'modernHistory';
 return null;
}

export function questionAllowedInForty(question,settings){
 const bank=additionalQuestionBankId(question);
 return !bank||normalizeAdditionalQuestionBanks(settings)[bank];
}
