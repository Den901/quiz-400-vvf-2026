const pdf=(id,title,file,pages,topic,description='')=>({id,title,type:'pdf',file:`study-materials/pdfs/${file}`,pages,topic,description});
const test=(id,title,file,pages,topic='mista')=>({id,title,type:'test',file:`study-materials/pdfs/${file}`,pages,topic,description:'Esercitazione riepilogativa con quesiti e soluzioni evidenziate nel documento.'});
const sheet=(id,title,file,topic,description='')=>({id,title,type:'sheet',file:`study-materials/images/summaries/${file}.jpg`,source:`study-materials/pages/${file}.pages`,pages:1,topic,description});
const image=(id,title,file,topic,description='')=>({id,title,type:'image',file:`study-materials/images/${file}`,pages:1,topic,description});

export const studyPaths=[
 {
  id:'storia',title:'Storia d’Italia',shortTitle:'Storia',icon:'◫',quizCategory:'storia',
  description:'Dall’Unità d’Italia alla Repubblica contemporanea, in ordine cronologico e con schede di sintesi.',
  modules:[
   {id:'unita',title:'1. Risorgimento e Stato unitario',description:'Le premesse dell’unificazione, il nuovo Regno e i primi schieramenti politici.',resources:[
    sheet('storia-unita-scheda','Unità d’Italia · scheda rapida',"1 - Unita d'Italia",'risorgimento','Bignami visuale sui passaggi essenziali dell’unificazione.'),
    pdf('storia-unita','Unità d’Italia (1848-1861)',"1 Unita d'Italia.pdf",9,'risorgimento'),
    sheet('storia-destra-scheda','Destra e Sinistra storica · scheda rapida','2- Destra e Sinistra','italia-postunitaria','Confronto sintetico tra i due schieramenti.'),
    pdf('storia-destra-sinistra','Destra e Sinistra storica','2 Destra e Sinistra storica.pdf',5,'italia-postunitaria'),
    pdf('storia-giolitti','Età giolittiana','3 Eta Giolittiana.pdf',5,'eta-giolittiana')
   ]},
   {id:'guerre-regimi',title:'2. Guerre mondiali e regimi',description:'Dalla Grande Guerra alla Liberazione, seguendo la successione degli eventi.',resources:[
    pdf('storia-prima-guerra','Prima guerra mondiale','4 Prima Guerra Mondiale.pdf',4,'prima-guerra'),
    pdf('storia-italia-prima-guerra','L’Italia nella Prima guerra mondiale',"5 L'italia nella Prima Guerra Mondiale.pdf",4,'prima-guerra'),
    pdf('storia-primo-dopoguerra','Primo dopoguerra','6 Primo Dopoguerra.pdf',4,'fascismo'),
    pdf('storia-crisi-1929','Crisi del 1929 e regimi totalitari','10 Crisi del 1929 e Regimi Totalitari.pdf',5,'fascismo'),
    pdf('storia-fascismo','Italia fascista','7 Italia fascista.pdf',6,'fascismo'),
    pdf('storia-seconda-guerra','Seconda guerra mondiale','8 Seconda Guerra Mondiale.pdf',9,'seconda-guerra'),
    pdf('storia-resistenza','Resistenza in Italia','9 Resistenza in Italia.pdf',4,'seconda-guerra')
   ]},
   {id:'repubblica',title:'3. Repubblica e Italia contemporanea',description:'Ricostruzione, Guerra fredda, anni di piombo e trasformazioni politiche recenti.',resources:[
    pdf('storia-secondo-dopoguerra','Secondo dopoguerra e Guerra fredda','11 Secondo Dopoguerra-Guerra Fredda.pdf',6,'repubblica-primi-anni'),
    pdf('storia-repubblicana','L’Italia repubblicana',"12 L'italia Repubblicana.pdf",6,'repubblica-primi-anni'),
    pdf('storia-anni-piombo','Crisi energetica e anni di piombo','13 Crisi Energetica e gli Anni di Piombo.pdf',13,'repubblica-contemporanea'),
    pdf('storia-1980-oggi','Sviluppi politici e sociali dal 1980 a oggi','15 Gli svillupi Politici e Sociali in Italia dal 1980 ad Oggi.pdf',10,'repubblica-contemporanea'),
    pdf('storia-malavita','Malavita organizzata e protagonisti dell’antimafia',"16 La Malavita Organizzata e i protagonisti che l'hanno combattuta.pdf",7,'repubblica-contemporanea')
   ]}
  ]
 },
 {
  id:'logica',title:'Logica e matematica di base',shortTitle:'Logica',icon:'⌘',quizCategory:'logica',
  description:'Strategie verbali, calcolo rapido, sequenze, probabilità, grafici e prove riepilogative.',
  modules:[
   {id:'verbale',title:'1. Logica verbale',description:'Lessico, significati, classificazioni e deduzioni.',resources:[
    pdf('logica-sinonimi-1','Sinonimi e contrari','1 Sinomi e Contrari.pdf',7,'verbale'),
    pdf('logica-sinonimi-2','Sinonimi, contrari e classificazioni concettuali','2 Sinonimi, Contrari e Classificazioni Concettuali.pdf',5,'verbale'),
    pdf('logica-anagrammi-1','Anagrammi','3 Anagrammi.pdf',6,'verbale'),
    pdf('logica-anagrammi-2','Anagrammi · seconda parte','4 Anagrammi 2.pdf',1,'verbale'),
    pdf('logica-semantica','Nozioni di semantica','5 Nozioni di Semantica.pdf',5,'verbale'),
    pdf('logica-sillogismi','Sillogismi','6 Sillogismi.pdf',9,'deduzioni')
   ]},
   {id:'calcolo',title:'2. Calcolo, frazioni e proporzioni',description:'Le basi numeriche da applicare rapidamente nei quesiti.',resources:[
    pdf('logica-operazioni','Le quattro operazioni','1 Le Quattro Operazioni.pdf',8,'calcolo'),
    pdf('logica-mcm-mcd','m.c.m. e M.C.D.','2 mcm e MCD.pdf',2,'calcolo'),
    pdf('logica-frazioni','Frazioni','3 Frazioni.pdf',2,'calcolo'),
    pdf('logica-frazioni-proporzioni','Frazioni e proporzioni','4 Frazioni e Proporzioni.pdf',2,'calcolo'),
    pdf('logica-proporzioni','Proporzioni','5 Proporzioni.pdf',4,'calcolo'),
    pdf('logica-percentuali','Frazioni generatrici e percentuali','6 Frazioni Generatrici e Percentuali.pdf',4,'calcolo'),
    pdf('logica-equivalenze','Equivalenze','7 Equivalenze.pdf',3,'calcolo'),
    pdf('logica-equivalenze-2','Equivalenze · approfondimento','8 Equivalenze 2.pdf',7,'calcolo'),
    pdf('logica-multipli-sottomultipli','Multipli e sottomultipli · schema','Multipli e sottomultipli.pdf',1,'calcolo'),
    pdf('logica-multipli-sottomultipli-2','Multipli e sottomultipli · secondo schema','Multipli e sottomultipli 2.pdf',1,'calcolo'),
    image('logica-misure-schema','Misure di lunghezza, peso e capacità','beecc296eff1766e5cea2ce38c83635b.png','calcolo','Schema visuale delle conversioni decimali.'),
    image('logica-superfici-schema','Conversioni delle superfici','conversione-chilometro-quadrato.png','calcolo','Promemoria per le unità di superficie.'),
    image('logica-volumi-schema','Conversioni dei volumi','images.png','calcolo','Promemoria per le unità cubiche.'),
    image('logica-lunghezze-schema','Scala delle lunghezze','maxresdefault.jpg.jpeg','calcolo','Schema a contrasto elevato per moltiplicazioni e divisioni per dieci.')
   ]},
   {id:'sequenze',title:'3. Sequenze, grafici e trasformazioni',description:'Riconoscere regole, configurazioni e rappresentazioni senza affidarsi alla memoria.',resources:[
    pdf('logica-sequenze','Sequenze e serie particolari','9 Sequenze e Serie particolari.pdf',12,'serie'),
    pdf('logica-relazioni-insiemistiche','Relazioni insiemistiche · guida pratica','7 Relazioni insiemistiche.pdf',17,'insiemi'),
    pdf('logica-configurazioni','Serie nelle configurazioni grafico-geometriche','10 Serie nelle configurazioni Grafico-Geometriche.pdf',6,'figure'),
    pdf('logica-serie-tabelle','Serie e tabelle','11 Serie e Tabelle.pdf',5,'serie'),
    pdf('logica-grafici-tabelle','Grafici e tabelle','12 Grafici e Tabelle.pdf',4,'calcolo'),
    pdf('logica-rappresentazioni','Rappresentazioni grafiche','13 Rappresentazioni Grafiche.pdf',5,'calcolo'),
    pdf('logica-attenzione','Attenzione e precisione','14 Attenzione e Precisione.pdf',7,'figure'),
    pdf('logica-equazioni','Equazioni','15 Equazioni.pdf',3,'calcolo'),
    pdf('logica-trasformazioni','Equazioni e trasformazioni simboliche','16 Equazioni e Trasformazioni simboliche.pdf',1,'calcolo')
   ]},
   {id:'probabilita',title:'4. Probabilità e calcolo combinatorio',description:'Regole, esempi svolti e schemi di riepilogo.',resources:[
    pdf('logica-probabilita-svolta','Calcolo delle probabilità con esercizi svolti','17 Calcolo della Probabilita con esercizi svolti.pdf',3,'calcolo'),
    pdf('logica-probabilita','Probabilità','18 Probabilita.pdf',1,'calcolo'),
    pdf('logica-combinatorio','Calcolo combinatorio','19 Calcolo Combinatorio.pdf',9,'calcolo'),
    pdf('logica-combinatorio-schema','Schema del calcolo combinatorio','20 Schema Calcolo Combinatorio.pdf',1,'calcolo')
   ]},
   {id:'prove',title:'5. Prove riepilogative',description:'Test datati e ordinati per ripassare le strategie affrontate nei moduli.',resources:[
    test('test-logica-2024-06-21','Test del 21 giugno 2024','1 Test 21 giugno 2024.pdf',1,'calcolo'),
    test('test-logica-verbale-2024-07-19','Test di logica verbale del 19 luglio 2024','1 Test Logica Verbale 19 luglio 2024.pdf',4,'verbale'),
    test('test-logica-equivalenze','Test sulle equivalenze','1 Test sulle Equivalenze.pdf',1,'calcolo'),
    test('test-logica-2024-07-12','Test del 12 luglio 2024','2 Test 12 luglio 2024.pdf',2),
    test('test-logica-2024-08-02','Test del 2 agosto 2024','3 Test 2 agosto 2024.pdf',6),
    test('test-logica-2024-08-27','Test del 27 agosto 2024','4 Test 27 agosto 2024.pdf',2),
    test('test-logica-2024-08-28','Test del 28 agosto 2024','5 Test 28 agosto 2024.pdf',3),
    test('test-logica-2024-08-30','Test del 30 agosto 2024','6 Test 30 agosto 2024.pdf',3),
    test('test-logica-2024-09-02','Test del 2 settembre 2024','7 Test 2 settembre 2024.pdf',2),
    test('test-logica-2024-09-04','Test del 4 settembre 2024','8 Test 4 settembre 2024.pdf',2),
    test('test-logica-2024-09-11','Test dell’11 settembre 2024','9 Test 11 settembre 2024.pdf',3),
    test('test-logica-2024-09-13','Test del 13 settembre 2024','10 Test 13 settembre 2024.pdf',3),
    test('test-logica-2024-09-16','Test del 16 settembre 2024','11 Test 16 settembre 2024.pdf',3),
    test('test-logica-2024-09-20','Test del 20 settembre 2024','12 Test 20 settembre 2024.pdf',3),
    test('test-logica-2024-09-25','Test del 25 settembre 2024','13 Test 25 settembre 2024.pdf',3),
    test('test-logica-2024-09-27','Test del 27 settembre 2024 · relazioni insiemistiche','14 Test 27 settembre 2024.pdf',6,'insiemi')
   ]}
  ]
 },
 {
  id:'fisica',title:'Fisica',shortTitle:'Fisica',icon:'↯',quizCategory:'fisica',
  description:'Dalle grandezze fisiche alla termodinamica, con formule, diagrammi ed esempi.',
  modules:[
   {id:'meccanica',title:'1. Misure, moto e forze',description:'Fondamenti della meccanica in ordine progressivo.',resources:[
    pdf('fisica-grandezze','Grandezze scalari e vettoriali','2 grandezze scalari vettoriali.pdf',16,'misure'),
    pdf('fisica-cinematica','Cinematica','3 Cinematica.pdf',34,'cinematica'),
    pdf('fisica-dinamica','Dinamica','4 Dinamica.pdf',12,'dinamica'),
    pdf('fisica-forze','Altri tipi di forze','5 Dinamica altri tipi di Forze.pdf',6,'dinamica'),
    pdf('fisica-lavoro-energia','Lavoro ed energia','6 Lavoro ed energia.pdf',11,'energia'),
    pdf('fisica-statica','Dinamica del corpo rigido e statica','7 Dinamiche di un corpo rigido (statica).pdf',12,'dinamica')
   ]},
   {id:'fluidi-calore',title:'2. Fluidi e termodinamica',description:'Pressione, comportamento dei fluidi, calore ed energia.',resources:[
    pdf('fisica-fluidi','Fluidi','8 Fluidi.pdf',16,'fluidi'),
    pdf('fisica-termodinamica','Termodinamica','9 Termodinamica.pdf',35,'termologia')
   ]}
  ]
 },
 {
  id:'chimica',title:'Chimica',shortTitle:'Chimica',icon:'⚗',quizCategory:'chimica',
  description:'Schede essenziali e dispense illustrate dalla materia alla chimica organica.',
  modules:[
   {id:'bignami',title:'1. Bignami essenziale',description:'Sei schede ad alta densità per fissare definizioni, regole e formule.',resources:[
    sheet('chimica-sostanze','Sostanze e proprietà','1 - SOSTANZE','materia'),
    sheet('chimica-atomo','Atomo e modelli atomici','2 - ATOMO','atomo'),
    sheet('chimica-legami','Configurazione elettronica e legami','3 - CONF-LEGAMI-TABELLA','legami'),
    sheet('chimica-acidi-redox','Acidi, basi e redox','4 - ACIDI BASI e REDOX','acidi-basi'),
    sheet('chimica-nomenclatura-scheda','Nomenclatura · scheda rapida','5 - NOMENCLATURA','legami'),
    sheet('chimica-termodinamica-scheda','Termodinamica e cinetica · scheda rapida','6 - TERMODINAMICA CINETICA','stati-gas')
   ]},
   {id:'generale',title:'2. Chimica generale e reazioni',description:'Dalla struttura della materia alle reazioni e agli equilibri.',resources:[
    pdf('chimica-generale','Chimica generale','x Chimica.pdf',44,'generale'),
    pdf('chimica-nomenclatura','Nomenclatura chimica','x Nomenclatura Chimica.pdf',46,'legami'),
    pdf('chimica-reazioni','Reazioni chimiche e bilanciamento','Reazioni Chimiche e Bilanciamento.pdf',30,'reazioni'),
    pdf('chimica-redox','Reazioni di ossidoriduzione','x Reazioni di Ossidoriduzione.pdf',13,'reazioni'),
    pdf('chimica-acidi-basi','Acidi e basi','x Acidi e Basi .pdf',31,'acidi-basi'),
    pdf('chimica-termodinamica','Termodinamica, cinetica ed equilibrio chimico','x Termodinamica Chimica, Cinetica Chimica ed Equilibrio Chimico.pdf',38,'stati-gas')
   ]},
   {id:'organica',title:'3. Chimica organica',description:'Carbonio, idrocarburi e gruppi funzionali.',resources:[
    pdf('chimica-organica-1','Chimica organica · prima parte','Chimica Organica prima parte.pdf',30,'organica'),
    pdf('chimica-organica-2','Chimica organica · gruppi funzionali','Chimica Organica seconda parte (Gruppi Funzionali).pdf',20,'organica')
   ]}
  ]
 },
 {
  id:'informatica',title:'Informatica',shortTitle:'Informatica',icon:'⌨',quizCategory:'informatica',
  description:'Hardware, applicativi Office, reti, sicurezza e periferiche, con dispense complete.',
  modules:[
   {id:'fondamenti',title:'1. Fondamenti e strumenti',description:'Le basi del sistema informatico e gli applicativi più richiesti.',resources:[
    sheet('informatica-scheda','Sistema informatico · scheda rapida','INFORMATICA','hardware'),
    pdf('informatica-base','Elementi di informatica di base','1 Informatica di Base.pdf',53,'hardware'),
    pdf('informatica-word','Word','2 Dispensa Word.pdf',60,'word'),
    pdf('informatica-excel','Excel','3 Dispensa Excel.pdf',50,'excel'),
    pdf('informatica-access','Access','4 Dispensa Access.pdf',22,'office-dati'),
    pdf('informatica-powerpoint','PowerPoint','5 Power Point.pdf',51,'office-dati')
   ]},
   {id:'reti-sicurezza',title:'2. Reti, sicurezza e periferiche',description:'Connettività, protezione dei dati e funzionamento delle stampanti.',resources:[
    pdf('informatica-sicurezza','Sicurezza informatica','6 Sicurezza informatica.pdf',15,'sicurezza'),
    pdf('informatica-reti','Reti informatiche','7 Reti Informatiche.pdf',34,'reti'),
    pdf('informatica-stampanti','Approfondimento sulle stampanti','Approfondimento sulle stampanti.pdf',4,'hardware'),
    pdf('informatica-stampanti-laser','Come funziona una stampante laser','Approfondimento stampanti laser.pdf',6,'hardware')
   ]}
  ]
 }
];

export const allStudyResources=studyPaths.flatMap(path=>path.modules.flatMap(module=>module.resources.map(resource=>({...resource,pathId:path.id,moduleId:module.id}))));
export const studyPathById=id=>studyPaths.find(path=>path.id===id)||null;
export const studyResourceById=id=>allStudyResources.find(resource=>resource.id===id)||null;
export const studyModuleForResource=resource=>studyPathById(resource?.pathId)?.modules.find(module=>module.id===resource?.moduleId)||null;
export const studyAssetHref=file=>`./${String(file).split('/').map(encodeURIComponent).join('/')}`;
export const studyQuizHref=resource=>resource?.pathId==='logica'?`#logic-topic/${resource.topic||'mista'}`:`#subject-topic/${resource?.pathId}:${resource?.topic||'generale'}`;
export function studyCoveredTopics(resource){
 return resource?.topic?[resource.topic]:[];
}
