import fs from 'node:fs';
import {classifyLogicQuestion} from '../logic-topics.js';
import {classifySubjectQuestion} from '../subject-topics.js';
const file=new URL('../quiz-dataset.json',import.meta.url),dataset=JSON.parse(fs.readFileSync(file));
for(const q of dataset){
 if(q.id.startsWith('info-pdf-'))q.subjectTopic=classifySubjectQuestion(q);
 if(!q.id.startsWith('logic-pdf-'))continue;
 q.logicTopic=/ingranagg|ruote dentate/i.test(q.text)?'ingranaggi'
  :/LEGGI IL BRANO/i.test(q.text)?'brani'
  :/relazione insiemistica|diagramma/i.test(q.text)?'relazioni'
  :/^Quesito illustrato/.test(q.text)?'verbale'
  :/^[\d\s?]+$/.test(q.text)?'serie':classifyLogicQuestion({...q,logicTopic:undefined});
 if(/^Negare|deduzion|sillogism/i.test(q.text))q.logicTopic='deduzioni';
 else if(/parentela|sorella del|nonno materno/i.test(q.text))q.logicTopic='relazioni';
 else if(q.logicTopic==='mista'&&/quante|quanto|quanti|produzione|peso|percorr|\bkg\b|\bcm\b|minuti|ore|km|pizze/i.test(q.text))q.logicTopic='calcolo';
 else if(q.logicTopic==='mista'&&/brano/i.test(q.text))q.logicTopic='brani';
 else if(q.logicTopic==='mista')q.logicTopic='deduzioni'; // Remaining five reviewed conditional/syllogistic questions.
}
fs.writeFileSync(file,JSON.stringify(dataset,null,2)+'\n');
