import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

import {allStudyResources,studyPaths} from '../../study-paths.js';
import {studyProgressSummary} from '../../study-paths-ui.js';

test('catalogo percorsi contiene tutti i materiali consegnati',()=>{
 assert.equal(studyPaths.length,5);
 assert.equal(allStudyResources.length,98);
 assert.equal(new Set(allStudyResources.map(resource=>resource.id)).size,98);
 for(const path of studyPaths){
  assert.ok(path.modules.length>0,path.id);
  assert.ok(path.modules.every(module=>module.resources.length>0),path.id);
 }
 for(const resource of allStudyResources){
  assert.ok(resource.topic,resource.id);
  assert.ok(fs.existsSync(new URL(`../../${resource.file}`,import.meta.url)),resource.file);
 }
});

test('avanzamento percorsi resta personale',()=>{
 const state={studyPaths:{resources:{
  [allStudyResources[0].id]:{status:'completed'},
  [allStudyResources[1].id]:{status:'started'}
 }}};
 const summary=studyProgressSummary(state,{});
 assert.equal(summary.total,98);
 assert.equal(summary.completed,1);
 assert.equal(summary.started,1);
});

test('visibilita amministratore riduce il catalogo senza perdere i dati',()=>{
 const state={studyPaths:{resources:{[allStudyResources[0].id]:{status:'completed'}}}};
 const summary=studyProgressSummary(state,{logica:false,fisica:false,chimica:false,informatica:false});
 assert.equal(summary.total,17);
 assert.equal(summary.completed,1);
});
