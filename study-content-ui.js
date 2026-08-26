import {studyQuizHref} from './study-paths.js?v=57';

const contentCache=new Map();

const contentHref=resource=>`./study-content/${encodeURIComponent(resource.id)}.json?v=57`;
const visualHref=value=>`./${String(value).split('/').map(encodeURIComponent).join('/')}`;

async function loadContent(resource){
 if(contentCache.has(resource.id))return contentCache.get(resource.id);
 const request=fetch(contentHref(resource),{cache:'no-cache'}).then(response=>{if(!response.ok)throw Error('Lezione digitale non disponibile');return response.json()});
 contentCache.set(resource.id,request);
 try{return await request}catch(error){contentCache.delete(resource.id);throw error}
}

function blockMarkup(block,esc){
 if(block.type==='heading')return`<h3>${esc(block.text)}</h3>`;
 if(block.type==='list')return`<ul>${(block.items||[]).map(item=>`<li>${esc(item)}</li>`).join('')}</ul>`;
 if(block.type==='table')return`<div class="study-content-table" role="region" aria-label="Tabella della lezione" tabindex="0"><table><thead><tr>${(block.headers||[]).map(header=>`<th scope="col">${esc(header)}</th>`).join('')}</tr></thead><tbody>${(block.rows||[]).map(row=>`<tr>${row.map(cell=>`<td>${esc(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
 return`<p>${esc(block.text||'')}</p>`;
}

function articleMarkup(content,resource,helpers){
 const esc=helpers.esc,sections=content.sections||[];
 return`<div class="study-digital-overview"><div><span>Lezione digitalizzata</span><strong>${Number(content.wordCount||0).toLocaleString('it')} parole</strong></div><div><span>Sezioni</span><strong>${sections.length}</strong></div><div><span>Schemi ed esempi</span><strong>${Number(content.visualCount||0)}</strong></div></div>
 <div class="study-digital-layout"><details class="study-digital-toc" open><summary>Indice della lezione</summary><nav>${sections.map((section,index)=>`<button type="button" data-study-section-target="lesson-${esc(resource.id)}-${index+1}"><span>${index+1}</span>${esc(section.title)}</button>`).join('')}</nav></details>
 <article class="study-digital-article"><div class="study-digital-intro"><div class="eyebrow">Contenuto nativo del portale</div><p>Testo organizzato per la lettura su schermo. Gli schemi originali utili al ragionamento sono inseriti accanto ai concetti a cui si riferiscono.</p></div>${sections.map((section,index)=>`<section class="study-digital-section" id="lesson-${esc(resource.id)}-${index+1}"><div class="study-section-number">${String(index+1).padStart(2,'0')}</div><div class="study-section-copy"><h2>${esc(section.title)}</h2>${(section.blocks||[]).map(block=>blockMarkup(block,esc)).join('')}${section.visual?`<figure class="study-digital-visual"><a href="${visualHref(section.visual)}" target="_blank" rel="noopener"><img src="${visualHref(section.visual)}" alt="${esc(section.visualAlt||section.title)}" loading="lazy"></a><figcaption>Esempio visuale della lezione · tocca per ingrandire</figcaption></figure>`:''}</div></section>`).join('')}</article></div>`;
}

function bindTableOfContents(host){
 host.querySelectorAll('[data-study-section-target]').forEach(button=>button.addEventListener('click',()=>{
  host.querySelector(`#${button.dataset.studySectionTarget}`)?.scrollIntoView({behavior:'smooth',block:'start'});
 }));
}

function answerFeedback(question,row,esc){
 const correctText=question.answers?.[question.correct]??'';
 return`<div class="study-check-feedback ${row.correct?'correct':row.blank?'blank':'wrong'}"><strong>${row.correct?'Risposta corretta':row.blank?'Domanda non risposta':'Risposta errata'}</strong><p>La risposta corretta è <b>${String.fromCharCode(65+question.correct)}. ${esc(correctText)}</b></p>${question.explanation?`<details><summary>Mostra la spiegazione</summary><p>${esc(question.explanation)}</p></details>`:'<p class="meta">Per questo quesito non è disponibile una spiegazione aggiuntiva.</p>'}</div>`;
}

function checkpointShell(resource,helpers){
 const previous=helpers.state.studyPaths?.checkpoints?.[resource.id]?.lastResult;
 return`<section class="card study-checkpoint" data-study-checkpoint><div class="study-checkpoint-head"><div><div class="eyebrow">Verifica di fine capitolo</div><h2>Controlla subito ciò che hai studiato</h2><p>Fino a 5 quesiti reali selezionati sul contenuto specifico di questa lezione. Hanno priorità le domande non fatte, non note o da ripetere.</p></div><div class="study-checkpoint-score">${previous?`<strong>${previous.correct}/${previous.total}</strong><span>ultimo risultato</span>`:'<strong>≤5</strong><span>domande mirate</span>'}</div></div><div class="quiz-actions"><button class="primary" type="button" data-checkpoint-start>${previous?'Nuova verifica':'Inizia la verifica'}</button><a class="button ghost" href="${studyQuizHref(resource)}">Allenamento completo</a></div></section>`;
}

function bindCheckpoint(host,resource,helpers){
 const shell=host.querySelector('[data-study-checkpoint]');if(!shell)return;
 shell.querySelector('[data-checkpoint-start]')?.addEventListener('click',()=>{
  const questions=helpers.checkpointQuestions(resource,5);
  if(!questions.length){shell.innerHTML=`<div class="notice">Non ci sono ancora quesiti compatibili con questo capitolo.</div><a class="button ghost" href="${studyQuizHref(resource)}">Apri i quiz della materia</a>`;return}
  let index=0,selected=null,rows=[];
  const renderQuestion=()=>{
   const question=questions[index],row=rows[index],locked=Boolean(row),last=index===questions.length-1;
   shell.innerHTML=`<div class="study-check-progress"><div><span>Verifica di fine capitolo</span><b>Domanda ${index+1} di ${questions.length}</b></div><div class="study-check-dots">${questions.map((_,dot)=>`<i class="${dot<rows.length?'done':dot===index?'current':''}"></i>`).join('')}</div></div><h2 class="study-check-question">${helpers.esc(question.text)}</h2>${question.image?`<img class="question-image study-check-image" src="${helpers.esc(question.image)}" alt="Figura del quesito">`:''}<div class="study-check-answers">${question.answers.map((answer,answerIndex)=>`<button type="button" class="answer ${selected===answerIndex?'picked':''} ${locked?(answerIndex===question.correct?'correct':answerIndex===row.choice?'wrong':''):''}" data-check-answer="${answerIndex}" ${locked?'disabled':''}><span class="letter">${String.fromCharCode(65+answerIndex)}</span><span>${helpers.esc(answer)}</span></button>`).join('')}</div>${locked?answerFeedback(question,row,helpers.esc):''}<div class="quiz-actions nav-actions">${!locked?'<button class="ghost" type="button" data-check-skip>Non rispondo</button><button class="primary" type="button" data-check-confirm disabled>Conferma risposta</button>':`<button class="primary" type="button" data-check-next>${last?'Concludi verifica':'Continua →'}</button>`}</div>`;
   shell.querySelectorAll('[data-check-answer]').forEach(button=>button.onclick=()=>{selected=Number(button.dataset.checkAnswer);shell.querySelectorAll('[data-check-answer]').forEach(item=>item.classList.toggle('picked',item===button));shell.querySelector('[data-check-confirm]').disabled=false});
   shell.querySelector('[data-check-confirm]')?.addEventListener('click',()=>{if(selected===null)return;rows[index]={q:question,choice:selected,blank:false,correct:selected===question.correct};renderQuestion()});
   shell.querySelector('[data-check-skip]')?.addEventListener('click',()=>{rows[index]={q:question,choice:null,blank:true,correct:false};renderQuestion()});
   shell.querySelector('[data-check-next]')?.addEventListener('click',()=>{if(last){const session=helpers.finishCheckpoint(resource,rows),total=rows.length,correct=rows.filter(row=>row.correct).length,wrong=rows.filter(row=>!row.correct&&!row.blank).length,blank=rows.filter(row=>row.blank).length;shell.innerHTML=`<div class="study-check-result"><div class="eyebrow">Verifica completata</div><h2>${correct}/${total} risposte corrette</h2><div><span class="correct"><b>${correct}</b> giuste</span><span class="wrong"><b>${wrong}</b> sbagliate</span><span class="blank"><b>${blank}</b> non risposte</span></div><p>Le risposte corrette sono state aggiunte a “Le so”; gli errori sono passati automaticamente in “Da ripetere”.</p><div class="quiz-actions"><button class="primary" type="button" data-check-again>Nuovi quesiti</button><a class="button ghost" href="#session/${helpers.esc(session.id)}">Rivedi le risposte</a></div></div>`;shell.querySelector('[data-check-again]').onclick=()=>{shell.outerHTML=checkpointShell(resource,helpers);bindCheckpoint(host,resource,helpers)}}else{index++;selected=null;renderQuestion()}});
  };
  renderQuestion();
 });
}

export async function renderDigitalStudyContent(host,resource,helpers){
 host.innerHTML='<div class="card study-digital-loading"><span></span><div><b>Preparazione della lezione digitale…</b><p>Organizzo testo, formule e schemi per la lettura.</p></div></div>';
 try{const content=await loadContent(resource);host.innerHTML=articleMarkup(content,resource,helpers)+checkpointShell(resource,helpers);bindTableOfContents(host);bindCheckpoint(host,resource,helpers)}catch(error){host.innerHTML=`<div class="notice"><b>Non riesco a caricare la lezione digitale.</b><span>${helpers.esc(error.message)}</span></div>`}
}

export function renderVisualStudyContent(host,resource,asset,helpers){
 host.innerHTML=`<figure class="study-image-frame"><img src="${asset}" alt="${helpers.esc(resource.title)}" loading="eager"><figcaption>${helpers.esc(resource.description||'Schema visuale del percorso di studio.')}</figcaption></figure>${checkpointShell(resource,helpers)}`;
 bindCheckpoint(host,resource,helpers);
}
