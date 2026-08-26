import {createHash} from 'node:crypto';
import {copyFile,mkdir,readFile,readdir,unlink,writeFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {classifyLogicQuestion,cleanQuestionText,isLongLogicPassage,normalizedQuestionText} from '../logic-topics.js';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const sourcePath=path.resolve(process.argv[2]||path.join(root,'tmp','vvf-2026-bank-decoded.json'));
const sourceImages=path.resolve(process.argv[3]||path.join(root,'tmp','vvf-2026-assets'));
const datasetPath=path.join(root,'quiz-dataset.json');
const imageDirectory=path.join(root,'quiz-images','logic-2026');
const reportPath=path.join(root,'logic-import-report.json');

const source=JSON.parse(await readFile(sourcePath,'utf8')).filter(row=>/logico-deduttivi/i.test(String(row.materia_uff)));
const dataset=JSON.parse(await readFile(datasetPath,'utf8')).filter(question=>!String(question.id).startsWith('logic-2026-'));
for(const question of dataset)if(question.category==='logica')question.logicTopic=classifyLogicQuestion(question);
const hash=value=>createHash('sha256').update(value).digest('hex');
const fileHash=async file=>hash(await readFile(file));
const existingImageHashes=new Map();
for(const question of dataset.filter(item=>item.image)){
 const file=path.join(root,String(question.image).replaceAll('/',path.sep));
 if(existsSync(file))existingImageHashes.set(await fileHash(file),true);
}
const existingText=new Set(dataset.filter(item=>!item.image).map(item=>normalizedQuestionText(item.text)));
const existingSignatures=new Set(dataset.map(item=>`${normalizedQuestionText(item.text)}|${(item.answers||[]).map(normalizedQuestionText).sort().join('|')}|`));
const seenSource=new Set(),added=[],topicCounts={},missingImages=[];
let excludedPassages=0,duplicates=0;
await mkdir(imageDirectory,{recursive:true});

for(const row of source){
 if(isLongLogicPassage(row)){excludedPassages++;continue}
 const answers=Array.from({length:Number(row.num_risp)||5},(_,index)=>cleanQuestionText(row[`risp${index+1}`])).filter(Boolean);
 const text=cleanQuestionText(row.domanda),correct=Math.max(0,Number(row.risp)-1),sourceImage=row.url_img?path.join(sourceImages,path.basename(row.url_img)):null;
 if(sourceImage&&!existsSync(sourceImage)){
  try{
   const response=await fetch(`https://www.concorsando.it/files/q_pics/${encodeURIComponent(path.basename(sourceImage))}`);
   if(response.ok)await writeFile(sourceImage,new Uint8Array(await response.arrayBuffer()));
  }catch{}
 }
 let visualKey='';
 if(sourceImage&&existsSync(sourceImage))visualKey=await fileHash(sourceImage);
 const textKey=normalizedQuestionText(text),signature=`${textKey}|${answers.map(normalizedQuestionText).sort().join('|')}|${visualKey}`;
 if(seenSource.has(signature)||existingSignatures.has(signature)||(!visualKey&&existingText.has(textKey))||(visualKey&&existingImageHashes.has(visualKey)&&dataset.some(item=>normalizedQuestionText(item.text)===textKey))){duplicates++;continue}
 seenSource.add(signature);existingSignatures.add(signature);if(!visualKey)existingText.add(textKey);
 const logicTopic=classifyLogicQuestion({text,answers,image:sourceImage?row.url_img:''}),id=`logic-2026-${hash(`${row.id}|${signature}`).slice(0,16)}`;
 let image=null;
 if(sourceImage){
  if(existsSync(sourceImage)){
   const extension=path.extname(sourceImage).toLowerCase()||'.png',name=`logic-${visualKey.slice(0,24)}${extension}`;
   if(!existsSync(path.join(imageDirectory,name)))await copyFile(sourceImage,path.join(imageDirectory,name));
   image=`quiz-images/logic-2026/${name}`;
  }else missingImages.push(String(row.url_img));
 }
 const correctText=answers[correct]||'';
 added.push({id,category:'logica',logicTopic,text,answers,correct,explanation:`Soluzione verificata: la risposta corretta è “${correctText}”.`,image});
 topicCounts[logicTopic]=(topicCounts[logicTopic]||0)+1;
}

const next=[...dataset,...added];
const usedImages=new Set(added.map(question=>question.image&&path.basename(question.image)).filter(Boolean));
for(const filename of await readdir(imageDirectory))if(!usedImages.has(filename))await unlink(path.join(imageDirectory,filename));
await writeFile(datasetPath,`${JSON.stringify(next,null,2)}\n`,'utf8');
const report={generatedAt:new Date().toISOString(),sourceQuestions:source.length,excludedLongPassages:excludedPassages,duplicatesSkipped:duplicates,questionsAdded:added.length,totalQuestions:next.length,topicCounts,missingImages:[...new Set(missingImages)].sort()};
await writeFile(reportPath,`${JSON.stringify(report,null,2)}\n`,'utf8');
console.log(JSON.stringify(report,null,2));
