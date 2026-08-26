import {classifyLogicQuestion,logicTopics} from './logic-topics.js?v=53';
import {classifySubjectQuestion,subjectTopics,topicDefinition} from './subject-topics.js?v=53';

const categoryNames={chimica:'Chimica',fisica:'Fisica',informatica:'Informatica',inglese:'Lingua inglese',logica:'Logica',storia:'Storia'};
const logicTopicNames=Object.fromEntries(logicTopics.map(topic=>[topic.id,topic.name]));

const whole=value=>Math.max(0,Math.floor(Number(value)||0));
const statusOf=progress=>['known','review','unknown'].includes(progress?.status)?progress.status:'unanswered';

export function tutorTrackForQuestion(question){
 const rawCategory=String(question?.category||''),category=['logica','brani','insiemi'].includes(rawCategory)?'logica':rawCategory;
 if(!categoryNames[category])return null;
 if(category==='logica'){
  const topic=classifyLogicQuestion(question),topicName=logicTopicNames[topic]||'Logica mista';
  return{key:`logica:${topic}`,category,topic,label:`Logica · ${topicName}`,shortLabel:topicName};
 }
 if(subjectTopics[category]){
  const topic=classifySubjectQuestion(question),topicName=topicDefinition(category,topic)?.name||`${categoryNames[category]} generale`;
  return{key:`${category}:${topic}`,category,topic,label:`${categoryNames[category]} · ${topicName}`,shortLabel:topicName};
 }
 return{key:category,category,topic:null,label:categoryNames[category],shortLabel:categoryNames[category]};
}

function strategyFor(track){
 if(track.recentWrong>=3||track.recentAccuracy!==null&&track.recentAccuracy<55)return'Parti da un quiz guidato: leggi la spiegazione dopo ogni risposta. Ripeti poi lo stesso settore a distanza di almeno un giorno.';
 if(track.recentBlank>track.recentWrong&&track.recentBlank>0)return'Lavora sul richiamo: prova a rispondere prima di aprire la spiegazione e usa “Non la so” quando manca la regola di base.';
 if(track.unknown>track.review)return'Ricostruisci le basi con domande guidate brevi. Una risposta corretta consolida subito il percorso, un errore resta nel ripasso.';
 if(track.review>0||track.recentWrong>0)return'Concentrati sulle domande “Da ripetere”, alternandole a domande mai viste per evitare la memorizzazione dell’ordine.';
 if(track.coverage<35)return'Aumenta la copertura: affronta soprattutto domande mai viste e controlla la spiegazione soltanto dopo aver risposto.';
 return'Mantenimento: poche domande miste e distanziate nel tempo per verificare che la conoscenza resti stabile.';
}

export function buildTutorAnalysis(questions,progress={},sessions=[]){
 const questionById=new Map(),tracks=new Map();
 for(const question of questions){
  questionById.set(String(question.id),question);const definition=tutorTrackForQuestion(question);if(!definition)continue;
  const track=tracks.get(definition.key)||{...definition,total:0,known:0,review:0,unknown:0,unanswered:0,attempts:0,correctAttempts:0,wrongAttempts:0,skipped:0,recentCorrect:0,recentWrong:0,recentBlank:0,weightedWrong:0,weightedBlank:0};
  const item=progress[String(question.id)]||progress[question.id]||{},status=statusOf(item);track.total++;track[status]++;track.attempts+=whole(item.attempts);track.correctAttempts+=whole(item.correct);track.wrongAttempts+=whole(item.wrong);track.skipped+=whole(item.skipped);tracks.set(definition.key,track);
 }
 const fortySessions=sessions.filter(session=>['exam','guided-exam'].includes(session?.type)),detailed=fortySessions.filter(session=>Array.isArray(session.review)&&session.review.length).slice(-10),detailCount=Math.max(1,detailed.length);
 detailed.forEach((session,index)=>{const recency=1+(index+1)/detailCount*.5;for(const row of session.review){const question=questionById.get(String(row.id));if(!question)continue;const definition=tutorTrackForQuestion(question),track=definition&&tracks.get(definition.key);if(!track)continue;if(row.blank){track.recentBlank++;track.weightedBlank+=recency}else if(row.correct)track.recentCorrect++;else{track.recentWrong++;track.weightedWrong+=recency}}});
 const ranked=[];
 for(const track of tracks.values()){
  const classified=track.known+track.review+track.unknown,graded=track.correctAttempts+track.wrongAttempts,recentTotal=track.recentCorrect+track.recentWrong,weak=track.review+track.unknown;
  track.coverage=track.total?Math.round(classified/track.total*100):0;track.accuracy=graded?Math.round(track.correctAttempts/graded*100):null;track.recentAccuracy=recentTotal?Math.round(track.recentCorrect/recentTotal*100):null;
  const recentPenalty=track.weightedWrong*12+track.weightedBlank*6,accuracyPenalty=track.recentAccuracy!==null?Math.max(0,80-track.recentAccuracy)*.45:track.accuracy!==null?Math.max(0,75-track.accuracy)*.18:0,weakPenalty=Math.min(30,track.unknown*3+track.review*1.5);
  track.priority=Math.round((recentPenalty+accuracyPenalty+weakPenalty)*10)/10;track.lossPoints=Math.round((track.recentWrong*1.33+track.recentBlank)*100)/100;track.strategy=strategyFor(track);track.tone=track.priority>=75?'danger':track.priority>=40?'warning':'attention';
  if(track.recentWrong||track.recentBlank||weak||track.attempts)ranked.push(track);
 }
 ranked.sort((a,b)=>b.priority-a.priority||b.recentWrong-a.recentWrong||b.wrongAttempts-a.wrongAttempts||a.label.localeCompare(b.label,'it'));
 const recentWindow=fortySessions.slice(-5),scores=recentWindow.map(session=>Number(session.score)).filter(Number.isFinite),correct=recentWindow.reduce((sum,session)=>sum+whole(session.correct),0),wrong=recentWindow.reduce((sum,session)=>sum+whole(session.wrong),0),blank=recentWindow.reduce((sum,session)=>sum+whole(session.blank),0);
 return{tracks:ranked,recentFortyCount:recentWindow.length,detailedFortyCount:detailed.length,averageScore:scores.length?Math.round(scores.reduce((sum,value)=>sum+value,0)/scores.length*100)/100:null,correct,wrong,blank};
}

export function tutorQuestionCount(duration){return Number(duration)===15?15:Number(duration)===60?50:30}

export function buildTutorAllocation(tracks,total){
 const candidates=tracks.slice(0,3),target=whole(total);if(!candidates.length||!target)return[];
 const weights=candidates.length===1?[1]:candidates.length===2?[.6,.4]:[.5,.3,.2],raw=weights.map(weight=>weight*target),counts=raw.map(value=>Math.floor(value));
 for(let remaining=target-counts.reduce((sum,value)=>sum+value,0);remaining>0;remaining--){let best=0;for(let index=1;index<raw.length;index++)if(raw[index]-counts[index]>raw[best]-counts[best])best=index;counts[best]++}
 return candidates.map((track,index)=>({track,count:counts[index]})).filter(item=>item.count>0);
}
