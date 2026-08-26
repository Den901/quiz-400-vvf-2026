import assert from 'node:assert/strict';
import test from 'node:test';
import {buildTutorAllocation,buildTutorAnalysis,tutorQuestionCount,tutorTrackForQuestion} from '../../tutor.js';

const questions=[
 {id:'c1',category:'chimica',text:'Bilanciare la seguente equazione chimica',answers:['A','B'],correct:0},
 {id:'c2',category:'chimica',text:'La legge di conservazione della massa',answers:['A','B'],correct:0},
 {id:'f1',category:'fisica',text:'Un corpo si muove a velocità costante',answers:['A','B'],correct:0},
 {id:'s1',category:'storia',text:'La spedizione dei Mille di Garibaldi',answers:['A','B'],correct:0},
 {id:'i1',category:'informatica',text:'Un indirizzo IP in una rete LAN',answers:['A','B'],correct:0},
 {id:'e1',category:'inglese',text:'Choose the correct preposition',answers:['A','B'],correct:0}
];

test('Tutor riconosce materia e sottosettore delle domande',()=>{
 assert.equal(tutorTrackForQuestion(questions[0]).key,'chimica:reazioni');
 assert.equal(tutorTrackForQuestion(questions[2]).key,'fisica:cinematica');
 assert.equal(tutorTrackForQuestion(questions[3]).key,'storia:risorgimento');
 assert.equal(tutorTrackForQuestion(questions[4]).key,'informatica:reti');
 assert.equal(tutorTrackForQuestion(questions[5]).key,'inglese:preposizioni');
});

test('gli errori recenti delle prove da 40 determinano la priorità',()=>{
 const progress={c1:{status:'review',attempts:2,correct:0,wrong:2},c2:{status:'unknown',attempts:1,correct:0,wrong:1},f1:{status:'known',attempts:2,correct:2,wrong:0}};
 const sessions=[{type:'exam',score:35,correct:36,wrong:3,blank:1,review:[{id:'c1',correct:false,blank:false},{id:'c2',correct:false,blank:false},{id:'f1',correct:true,blank:false}]}];
 const analysis=buildTutorAnalysis(questions,progress,sessions);
 assert.equal(analysis.tracks[0].key,'chimica:reazioni');
 assert.equal(analysis.tracks[0].recentWrong,2);
 assert.equal(analysis.averageScore,35);
 assert.match(analysis.tracks[0].strategy,/quiz guidato/i);
});

test('durata e distribuzione del piano Tutor restano esatte',()=>{
 assert.equal(tutorQuestionCount(15),15);
 assert.equal(tutorQuestionCount(30),30);
 assert.equal(tutorQuestionCount(60),50);
 const tracks=[{key:'a'},{key:'b'},{key:'c'}],allocation=buildTutorAllocation(tracks,30);
 assert.deepEqual(allocation.map(item=>item.count),[15,9,6]);
 assert.equal(allocation.reduce((sum,item)=>sum+item.count,0),30);
});
