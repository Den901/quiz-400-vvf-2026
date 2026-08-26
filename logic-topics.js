export const logicTopics=[
 {id:'deduzioni',name:'Deduzioni e condizioni',shortName:'Deduzioni',description:'Condizioni, conseguenze, negazioni e conclusioni necessarie.'},
 {id:'serie',name:'Serie e sequenze',shortName:'Serie',description:'Serie numeriche, alfabetiche, simboliche e completamenti.'},
 {id:'verbale',name:'Logica verbale',shortName:'Verbale',description:'Sinonimi, contrari, analogie, lessico e parole da scartare.'},
 {id:'calcolo',name:'Problemi e calcolo logico',shortName:'Calcolo',description:'Problemi numerici, percentuali, probabilità e operazioni.'},
 {id:'figure',name:'Figure e simboli',shortName:'Figure',description:'Figure, rotazioni, tasselli, dadi e ragionamento visivo.'},
 {id:'insiemi',name:'Insiemi e diagrammi',shortName:'Insiemi',description:'Diagrammi insiemistici, appartenenze, intersezioni e relazioni tra gruppi.'},
 {id:'relazioni',name:'Relazioni e classificazioni',shortName:'Relazioni',description:'Relazioni logiche, analogie tra elementi e classificazioni.'},
 {id:'ordinamenti',name:'Ordinamenti e posizioni',shortName:'Ordinamenti',description:'Ordini, posti, confronti, calendari e relazioni spaziali.'},
 {id:'brani',name:'Comprensione dei brani',shortName:'Brani',description:'Quesiti basati sulla lettura e comprensione di un testo.'},
 {id:'mista',name:'Logica mista',shortName:'Mista',description:'Quesiti logici non riconducibili a una sola tipologia.'}
];

const topicIds=new Set(logicTopics.map(topic=>topic.id));

export function cleanQuestionText(value){
 return String(value??'')
  .replace(/\u0080/g,'€').replace(/[\u0082\u0091\u0092]/g,"'").replace(/[\u0093\u0094]/g,'"')
  .replace(/\u0095/g,'•').replace(/\u0096/g,'–').replace(/\u0097/g,'—')
  .replace(/\u00a0/g,' ').replace(/\s+/g,' ').trim();
}

export function normalizedQuestionText(value){
 return cleanQuestionText(value).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
}

export function isLongLogicPassage(question){
 const text=cleanQuestionText(question?.text??question?.domanda);
 const normalized=normalizedQuestionText(text);
 return /^(leggere|leggi|si legga|dopo aver letto) (il |la |lo |i |le |un |una )?(brano|testo|passo)/.test(normalized)
  || normalized.includes('rispondere al quesito solo in base alle informazioni contenute')
  || text.length>700;
}

export function classifyLogicQuestion(question){
 if(question?.category==='brani')return'brani';
 if(question?.category==='insiemi')return'insiemi';
 if(topicIds.has(question?.logicTopic))return question.logicTopic;
 const text=normalizedQuestionText(`${question?.text??question?.domanda??''} ${(question?.answers??[]).join(' ')}`);
 const image=String(question?.image??question?.url_img??'');
 if(/diagramm|relazione insiem|insiemistic|cerchi di eulero|insiemi rappresentati|intersezione|appartiene all insieme/.test(text))return'relazioni';
 if(image||/figura|disegno|immagine|tassell|dado|facce visibili|specchio|ruotat|simbolo mancante|matrice figur/.test(text))return'figure';
 if(/serie|sequenz|numero mancante|lettera mancante|completa.*successione|prosegue.*successione|integrare la serie|analogia con la serie|simbolo deve essere inserito/.test(text))return'serie';
 if(/sinonim|contrari|significato|parola da scartare|termine da scartare|non attinente|attinente alla parola|analogia verbale|completano correttamente la frase|vocabolo|lessical|anagramm|ordine alfabetico/.test(text))return'verbale';
 if(/negazione|dedurre|deduzione|necessariamente|certamente vera|certamente falsa|puo essere vera|puo essere falso|se .* allora|affermazion|conclusione|implica|condizione sufficiente|condizione necessaria|sillogism/.test(text))return'deduzioni';
 if(/probabilit|percent|quanto vale|calcolare|calcolo|operazione|prezzo|spesa|guadagn|perdita|eta |anni ha|velocit|distanza|tempo impiega|media aritmetica|frazione|proporzione|equazione|somma|prodotto|differenza|quoziente/.test(text))return'calcolo';
 if(/precede|segue immediatamente|prima di|dopo di|a destra|a sinistra|posizione|classifica|ordine corretto|piu alto|piu basso|giorno della settimana|posti a sedere|fila|graduatoria/.test(text))return'ordinamenti';
 return'mista';
}

export function defaultLogicPlan(total=0){
 const count=Math.max(0,Math.floor(Number(total)||0)),weights=['deduzioni','serie','verbale','calcolo','figure','insiemi','relazioni','ordinamenti','brani','mista'],plan=Object.fromEntries(weights.map(id=>[id,0]));
 for(let index=0;index<count;index++)plan[weights[index%weights.length]]++;
 return plan;
}

export function normalizeLogicPlan(plan,total=0){
 const wanted=Math.max(0,Math.floor(Number(total)||0));
 if(!plan||typeof plan!=='object')return defaultLogicPlan(wanted);
 const normalized=Object.fromEntries(logicTopics.map(topic=>[topic.id,Math.max(0,Math.floor(Number(plan[topic.id])||0))]));
 return Object.values(normalized).reduce((sum,value)=>sum+value,0)===wanted?normalized:defaultLogicPlan(wanted);
}

export const logicPlanTotal=plan=>logicTopics.reduce((sum,topic)=>sum+(Math.max(0,Math.floor(Number(plan?.[topic.id])||0))),0);

export function selectLogicQuestionsByPlan(questions,plan,picker){
 const selected=[];
 for(const topic of logicTopics){
  const count=Math.max(0,Math.floor(Number(plan?.[topic.id])||0));
  if(!count)continue;
  const source=questions.filter(question=>classifyLogicQuestion(question)===topic.id),picked=picker(source,count,topic);
  if(!Array.isArray(picked)||picked.length!==count)throw Error(`Non ci sono abbastanza domande in ${topic.name}`);
  selected.push(...picked);
 }
 return selected;
}
