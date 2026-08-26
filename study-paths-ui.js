import {allStudyResources,studyAssetHref,studyModuleForResource,studyPathById,studyPaths,studyQuizHref,studyResourceById} from './study-paths.js?v=57';
import {renderDigitalStudyContent,renderVisualStudyContent} from './study-content-ui.js?v=57';

const statusLabel=status=>status==='completed'?'Completata':status==='started'?'In corso':'Da iniziare';
const typeLabel=resource=>resource.type==='sheet'?'Scheda rapida':resource.type==='image'?'Schema visuale':resource.type==='test'?'Esercitazione digitalizzata':'Lezione digitale';
const pathResources=path=>path.modules.flatMap(module=>module.resources.map(resource=>({...resource,pathId:path.id,moduleId:module.id})));

function ensureStudyState(state){
 state.studyPaths??={resources:{},lastResourceId:null};
 state.studyPaths.resources??={};
 return state.studyPaths;
}

function visiblePaths(helpers){
 const visibility=helpers.visibility||{};
 return studyPaths.filter(path=>visibility[path.id]!==false);
}

function progressEntry(resource,state){return ensureStudyState(state).resources[resource.id]||null}
function resourceCompleted(resource,state){return progressEntry(resource,state)?.status==='completed'}

function pathProgress(path,state){
 const resources=pathResources(path),completed=resources.filter(resource=>resourceCompleted(resource,state)).length,started=resources.filter(resource=>progressEntry(resource,state)?.status==='started').length;
 return{total:resources.length,completed,started,percent:resources.length?Math.round(completed/resources.length*100):0};
}

function resourceStatusMarkup(resource,state){
 const status=progressEntry(resource,state)?.status||'unstarted';
 return `<span class="study-resource-status ${status}"><i aria-hidden="true">${status==='completed'?'✓':status==='started'?'◐':'○'}</i>${statusLabel(status)}</span>`;
}

function recommendation(helpers,paths){
 const track=helpers.recommendation;
 if(!track)return null;
 const path=paths.find(item=>item.id===track.category);
 if(!path)return null;
 const resources=pathResources(path),exact=resources.find(resource=>resource.topic===track.topic&&!resourceCompleted(resource,helpers.state)),fallback=resources.find(resource=>!resourceCompleted(resource,helpers.state));
 return{track,path,resource:exact||fallback};
}

function resourceCard(resource,state,helpers){
 const path=studyPathById(resource.pathId),module=studyModuleForResource(resource);
 return `<a class="card study-resource-card" href="#study-resource/${helpers.esc(resource.id)}" data-study-search-item data-search="${helpers.esc(`${resource.title} ${path?.title||''} ${module?.title||''} ${resource.description||''}`.toLowerCase())}">
  <div class="study-resource-card-copy"><span class="study-resource-kind">${helpers.esc(typeLabel(resource))}</span><h3>${helpers.esc(resource.title)}</h3>${resource.description?`<p>${helpers.esc(resource.description)}</p>`:''}</div>
  ${resourceStatusMarkup(resource,state)}
 </a>`;
}

export function studyProgressSummary(state,visibility={}){
 const paths=studyPaths.filter(path=>visibility[path.id]!==false),resources=paths.flatMap(pathResources),completed=resources.filter(resource=>resourceCompleted(resource,state)).length,started=resources.filter(resource=>progressEntry(resource,state)?.status==='started').length;
 return{completed,started,total:resources.length,percent:resources.length?Math.round(completed/resources.length*100):0,lastResourceId:ensureStudyState(state).lastResourceId};
}

export function renderStudyPaths(app,pathId,helpers){
 const paths=visiblePaths(helpers),selected=pathId?paths.find(path=>path.id===pathId):null;
 if(pathId&&!selected){app.innerHTML='<div class="notice">Questo percorso non è disponibile.</div>';return}
 if(selected){renderPath(app,selected,helpers);return}
 const summary=studyProgressSummary(helpers.state,helpers.visibility),suggested=recommendation(helpers,paths),last=studyResourceById(summary.lastResourceId),lastVisible=last&&paths.some(path=>path.id===last.pathId),resume=lastVisible&&!resourceCompleted(last,helpers.state)?last:paths.flatMap(pathResources).find(resource=>!resourceCompleted(resource,helpers.state));
 app.innerHTML=`<section class="study-hero"><div><div class="eyebrow">Nuova area di apprendimento</div><h1>Percorsi di studio</h1><p>Lezioni ordinate per argomento con dispense, immagini, formule e verifiche. Il progresso è personale e sincronizzato con il tuo account.</p></div><div class="study-hero-progress"><strong>${summary.percent}%</strong><span>${summary.completed} di ${summary.total} lezioni completate</span><div class="progress"><span style="width:${summary.percent}%"></span></div></div></section>
 ${suggested?.resource?`<section class="card study-recommendation"><div><div class="eyebrow">Consigliato dal Tutor</div><h2>${helpers.esc(suggested.resource.title)}</h2><p>${helpers.esc(suggested.track.label)} è tra le aree che richiedono più attenzione. Studia questo contenuto e passa subito ai quiz mirati.</p></div><a class="button primary" href="#study-resource/${helpers.esc(suggested.resource.id)}">Inizia ora</a></section>`:''}
 <div class="study-toolbar"><label for="studySearch">Cerca nei percorsi</label><input id="studySearch" type="search" placeholder="Es. cinematica, acidi e basi, Excel…" autocomplete="off"></div>
 <div class="study-path-grid">${paths.map(path=>{const progress=pathProgress(path,helpers.state),resources=pathResources(path);return `<article class="card study-path-card" data-study-path-card data-search="${helpers.esc(`${path.title} ${path.description} ${resources.map(item=>item.title).join(' ')}`.toLowerCase())}"><div class="study-path-icon" aria-hidden="true">${path.icon}</div><div class="study-path-copy"><div class="study-path-card-head"><h2>${helpers.esc(path.title)}</h2><span>${resources.length} lezioni</span></div><p>${helpers.esc(path.description)}</p><div class="study-path-stats"><span><b>${progress.completed}</b> completate</span><span><b>${progress.started}</b> in corso</span><span><b>${progress.percent}%</b> avanzamento</span></div><div class="progress"><span style="width:${progress.percent}%"></span></div></div><a class="button primary compact" href="#study-path/${path.id}">${progress.started||progress.completed?'Continua':'Apri'}</a></article>`}).join('')}</div>
 ${resume?`<div class="study-floating-resume"><a class="button secondary" href="#study-resource/${helpers.esc(resume.id)}">Riprendi: ${helpers.esc(resume.title)}</a></div>`:''}`;
 const search=app.querySelector('#studySearch');
 search?.addEventListener('input',()=>{const value=search.value.trim().toLowerCase();app.querySelectorAll('[data-study-path-card]').forEach(card=>card.hidden=Boolean(value)&&!card.dataset.search.includes(value))});
}

function renderPath(app,path,helpers){
 const resources=pathResources(path),progress=pathProgress(path,helpers.state),studyState=ensureStudyState(helpers.state),last=resources.find(resource=>resource.id===studyState.lastResourceId&&!resourceCompleted(resource,helpers.state)),resume=last||resources.find(resource=>!resourceCompleted(resource,helpers.state))||resources[0];
 app.innerHTML=`<a class="back-link" href="#paths">← Tutti i percorsi</a><section class="study-path-header"><div class="study-path-icon large" aria-hidden="true">${path.icon}</div><div><div class="eyebrow">${resources.length} lezioni · ${path.modules.length} moduli</div><h1>${helpers.esc(path.title)}</h1><p>${helpers.esc(path.description)}</p></div><div class="study-path-header-actions"><a class="button primary" href="#study-resource/${helpers.esc(resume.id)}">${progress.completed===resources.length?'Rivedi il percorso':progress.started||progress.completed?'Riprendi':'Inizia'}</a><a class="button ghost" href="#category/${path.quizCategory}">Quiz di ${helpers.esc(path.shortTitle)}</a></div></section>
 <section class="card study-path-overview"><div><b>${progress.completed}/${progress.total}</b><span>lezioni completate</span></div><div><b>${progress.started}</b><span>lezioni in corso</span></div><div><b>${progress.percent}%</b><span>avanzamento</span></div><div class="progress"><span style="width:${progress.percent}%"></span></div></section>
 <div class="study-module-list">${path.modules.map((module,index)=>{const completed=module.resources.filter(resource=>resourceCompleted({...resource,pathId:path.id,moduleId:module.id},helpers.state)).length;return `<details class="card study-module" ${index===0||completed<module.resources.length?'open':''}><summary><span><small>Modulo ${index+1}</small><b>${helpers.esc(module.title.replace(/^\d+\.\s*/,''))}</b><em>${helpers.esc(module.description)}</em></span><span class="study-module-count">${completed}/${module.resources.length}</span></summary><div class="study-module-resources">${module.resources.map(resource=>resourceCard({...resource,pathId:path.id,moduleId:module.id},helpers.state,helpers)).join('')}</div></details>`}).join('')}</div>`;
}

function recordOpen(resource,helpers){
 const state=ensureStudyState(helpers.state),now=new Date().toISOString(),entry=state.resources[resource.id]||{};
 state.resources[resource.id]={...entry,status:entry.status==='completed'?'completed':'started',openedAt:entry.openedAt||now,lastOpenedAt:now,openCount:(Number(entry.openCount)||0)+1};
 state.lastResourceId=resource.id;
 helpers.save();
}

function adjacentResources(resource,helpers){
 const path=visiblePaths(helpers).find(item=>item.id===resource.pathId),resources=path?pathResources(path):[],index=resources.findIndex(item=>item.id===resource.id);
 return{previous:index>0?resources[index-1]:null,next:index>=0&&index<resources.length-1?resources[index+1]:null};
}

export function renderStudyResource(app,resourceId,helpers){
 const resource=studyResourceById(resourceId),path=resource&&visiblePaths(helpers).find(item=>item.id===resource.pathId);
 if(!resource||!path){app.innerHTML='<div class="notice">Lezione non trovata o non disponibile.</div>';return}
 recordOpen(resource,helpers);
 const module=studyModuleForResource(resource),entry=progressEntry(resource,helpers.state),completed=entry?.status==='completed',asset=studyAssetHref(resource.file),adjacent=adjacentResources(resource,helpers),isDocument=['pdf','test'].includes(resource.type);
 app.innerHTML=`<a class="back-link" href="#study-path/${path.id}">← ${helpers.esc(path.title)}</a><section class="study-reader-head"><div><div class="eyebrow">${helpers.esc(module?.title||path.title)} · ${helpers.esc(typeLabel(resource))}</div><h1>${helpers.esc(resource.title)}</h1>${resource.description?`<p>${helpers.esc(resource.description)}</p>`:''}</div><div class="study-reader-actions"><button class="${completed?'secondary':'primary'}" type="button" data-study-complete>${completed?'✓ Completata · segna da rivedere':'Segna come completata'}</button><a class="button ghost" href="${studyQuizHref(resource)}">Metti alla prova</a></div></section>
 <aside class="study-reader-note"><b>Come studiare</b><span>Leggi il contenuto, prova a richiamare i concetti senza guardare e poi usa “Metti alla prova” per esercitarti sullo stesso argomento.</span></aside>
 <div data-study-content-host></div>
 <nav class="study-reader-nav" aria-label="Navigazione tra le lezioni">${adjacent.previous?`<a class="button ghost" href="#study-resource/${helpers.esc(adjacent.previous.id)}">← ${helpers.esc(adjacent.previous.title)}</a>`:'<span></span>'}${adjacent.next?`<a class="button primary" href="#study-resource/${helpers.esc(adjacent.next.id)}">${helpers.esc(adjacent.next.title)} →</a>`:`<a class="button primary" href="#study-path/${path.id}">Percorso completato</a>`}</nav>`;
 requestAnimationFrame(()=>window.scrollTo({top:0,behavior:'instant'}));
 const contentHost=app.querySelector('[data-study-content-host]');
 if(isDocument)renderDigitalStudyContent(contentHost,resource,helpers);else renderVisualStudyContent(contentHost,resource,asset,helpers);
 app.querySelector('[data-study-complete]').onclick=()=>{const state=ensureStudyState(helpers.state),current=state.resources[resource.id]||{};state.resources[resource.id]={...current,status:completed?'started':'completed',completedAt:completed?null:new Date().toISOString()};helpers.save();renderStudyResource(app,resource.id,helpers)};
}
