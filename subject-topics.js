const chemistryTopics = [
  {
    id: 'materia',
    name: 'Materia, miscugli e separazioni',
    shortName: 'Materia',
    description: 'Sostanze pure, miscugli, proprietà della materia e tecniche di separazione.'
  },
  {
    id: 'atomo',
    name: 'Atomo e tavola periodica',
    shortName: 'Atomo',
    description: 'Struttura atomica, isotopi, elementi, gruppi e proprietà periodiche.'
  },
  {
    id: 'legami',
    name: 'Legami, formule e composti',
    shortName: 'Legami',
    description: 'Legami chimici, valenza, nomenclatura, formule e classificazione dei composti.'
  },
  {
    id: 'reazioni',
    name: 'Reazioni, leggi e bilanciamenti',
    shortName: 'Reazioni',
    description: 'Equazioni chimiche, bilanciamenti, ossidoriduzioni e leggi ponderali.'
  },
  {
    id: 'moli-soluzioni',
    name: 'Moli, calcoli e soluzioni',
    shortName: 'Moli e soluzioni',
    description: 'Mole, massa molare, concentrazioni, solubilità e calcoli stechiometrici.'
  },
  {
    id: 'acidi-basi',
    name: 'Acidi, basi e pH',
    shortName: 'Acidi e basi',
    description: 'Acidità, basicità, pH, indicatori, sali e neutralizzazioni.'
  },
  {
    id: 'stati-gas',
    name: 'Stati della materia e gas',
    shortName: 'Stati e gas',
    description: 'Passaggi di stato, comportamento dei gas, pressione, temperatura e calore.'
  },
  {
    id: 'organica',
    name: 'Chimica organica',
    shortName: 'Organica',
    description: 'Idrocarburi, gruppi funzionali, polimeri e principali composti organici.'
  },
  {
    id: 'bio-applicata',
    name: 'Biochimica, ambiente e applicazioni',
    shortName: 'Bio e applicata',
    description: 'Biomolecole, processi biologici, ambiente, combustibili e chimica quotidiana.'
  },
  {
    id: 'generale',
    name: 'Chimica generale',
    shortName: 'Generale',
    description: 'Quesiti generali che collegano più aree della chimica.'
  }
];

const physicsTopics = [
  {
    id: 'misure',
    name: 'Grandezze, misure e vettori',
    shortName: 'Misure',
    description: 'Sistema internazionale, unità di misura, conversioni, errori e vettori.'
  },
  {
    id: 'cinematica',
    name: 'Cinematica e moti',
    shortName: 'Cinematica',
    description: 'Spazio, tempo, velocità, accelerazione, caduta e moti rettilinei o circolari.'
  },
  {
    id: 'dinamica',
    name: 'Forze, dinamica e statica',
    shortName: 'Dinamica',
    description: 'Leggi di Newton, equilibrio, attrito, gravità, leve e quantità di moto.'
  },
  {
    id: 'energia',
    name: 'Lavoro, energia e potenza',
    shortName: 'Energia',
    description: 'Lavoro meccanico, energia cinetica e potenziale, potenza e rendimento.'
  },
  {
    id: 'fluidi',
    name: 'Fluidi e pressione',
    shortName: 'Fluidi',
    description: 'Pressione, densità, galleggiamento, idrostatica e principi di Pascal e Archimede.'
  },
  {
    id: 'termologia',
    name: 'Termologia e termodinamica',
    shortName: 'Termologia',
    description: 'Calore, temperatura, dilatazione, gas e principi della termodinamica.'
  },
  {
    id: 'onde-ottica',
    name: 'Onde, suono e ottica',
    shortName: 'Onde e ottica',
    description: 'Onde, acustica, luce, riflessione, rifrazione, specchi e lenti.'
  },
  {
    id: 'elettromagnetismo',
    name: 'Elettricità e magnetismo',
    shortName: 'Elettricità',
    description: 'Cariche, corrente, tensione, circuiti, campo elettrico e magnetico.'
  },
  {
    id: 'atomica',
    name: 'Fisica atomica e nucleare',
    shortName: 'Atomica',
    description: 'Radioattività, struttura nucleare, decadimenti, fissione e fusione.'
  },
  {
    id: 'generale',
    name: 'Fisica generale',
    shortName: 'Generale',
    description: 'Quesiti generali che collegano più aree della fisica.'
  }
];

const computerScienceTopics = [
  {
    id: 'hardware',
    name: 'Hardware, componenti e periferiche',
    shortName: 'Hardware',
    description: 'CPU, memorie, dispositivi di archiviazione, porte, monitor, stampanti e periferiche.'
  },
  {
    id: 'sistemi-file',
    name: 'Sistemi operativi, file e cartelle',
    shortName: 'Sistemi e file',
    description: 'Windows, processi, interfaccia, file system, estensioni, cartelle e gestione delle risorse.'
  },
  {
    id: 'word',
    name: 'Word ed elaborazione testi',
    shortName: 'Word',
    description: 'Documenti, formattazione, stampa, tabelle, intestazioni e comandi di videoscrittura.'
  },
  {
    id: 'excel',
    name: 'Excel e fogli di calcolo',
    shortName: 'Excel',
    description: 'Celle, formule, funzioni, grafici, filtri, ordinamenti e tabelle pivot.'
  },
  {
    id: 'office-dati',
    name: 'Presentazioni, posta e basi di dati',
    shortName: 'Office e dati',
    description: 'PowerPoint, Outlook, Access, presentazioni, posta elettronica e database.'
  },
  {
    id: 'reti',
    name: 'Reti, protocolli e connettività',
    shortName: 'Reti',
    description: 'LAN, WAN, indirizzi IP, protocolli, router, switch, Wi-Fi e trasmissione dei dati.'
  },
  {
    id: 'internet',
    name: 'Internet, Web e servizi digitali',
    shortName: 'Internet e Web',
    description: 'Browser, motori di ricerca, URL, cloud, servizi online, commercio elettronico e comunicazione.'
  },
  {
    id: 'sicurezza',
    name: 'Sicurezza informatica',
    shortName: 'Sicurezza',
    description: 'Malware, phishing, password, firewall, antivirus, backup, privacy e protezione dei dati.'
  },
  {
    id: 'software-dati',
    name: 'Software, dati e rappresentazione',
    shortName: 'Software e dati',
    description: 'Programmi, algoritmi, bit e byte, codifica, licenze e concetti generali di elaborazione.'
  },
  {
    id: 'generale',
    name: 'Informatica generale',
    shortName: 'Generale',
    description: 'Quesiti trasversali che collegano più aree dell’informatica.'
  }
];

const historyTopics = [
  {
    id: 'risorgimento',
    name: 'Risorgimento e Unità d’Italia',
    shortName: 'Risorgimento',
    description: 'Moti, protagonisti, guerre d’indipendenza e formazione dello Stato unitario.'
  },
  {
    id: 'italia-postunitaria',
    name: 'Italia postunitaria e fine Ottocento',
    shortName: 'Italia postunitaria',
    description: 'Destra e Sinistra storica, trasformismo, questione sociale e politica coloniale.'
  },
  {
    id: 'eta-giolittiana',
    name: 'Età giolittiana e primo Novecento',
    shortName: 'Età giolittiana',
    description: 'Governi Giolitti, sviluppo economico, riforme, società e guerra di Libia.'
  },
  {
    id: 'prima-guerra',
    name: 'Prima guerra mondiale',
    shortName: 'Prima guerra',
    description: 'Cause, alleanze, fronte italiano, battaglie e conseguenze della Grande Guerra.'
  },
  {
    id: 'fascismo',
    name: 'Fascismo e regime',
    shortName: 'Fascismo',
    description: 'Nascita del fascismo, dittatura, istituzioni, società ed economia del regime.'
  },
  {
    id: 'seconda-guerra',
    name: 'Seconda guerra mondiale e Resistenza',
    shortName: 'Seconda guerra',
    description: 'Conflitto mondiale, caduta del fascismo, armistizio, Resistenza e Liberazione.'
  },
  {
    id: 'repubblica-primi-anni',
    name: 'Nascita della Repubblica e ricostruzione',
    shortName: 'Repubblica e ricostruzione',
    description: 'Referendum, Costituente, Costituzione, dopoguerra e governi fino agli anni Cinquanta.'
  },
  {
    id: 'repubblica-contemporanea',
    name: 'Italia repubblicana dal 1960',
    shortName: 'Italia dal 1960',
    description: 'Centro-sinistra, movimenti, terrorismo, crisi politiche e trasformazioni recenti.'
  },
  {
    id: 'storia-internazionale',
    name: 'Europa, mondo e società contemporanea',
    shortName: 'Europa e mondo',
    description: 'Rivoluzioni, industrializzazione, potenze europee, relazioni internazionali e Guerra fredda.'
  },
  {
    id: 'generale',
    name: 'Storia e istituzioni generali',
    shortName: 'Generale',
    description: 'Cronologia, istituzioni e quesiti che collegano più periodi storici.'
  }
];

const englishTopics = [
  {
    id: 'tempi-verbali',
    name: 'Tempi verbali',
    shortName: 'Tempi verbali',
    description: 'Present, past, future, perfect e continuous nelle principali forme d’uso.'
  },
  {
    id: 'modali-condizionali',
    name: 'Modali, condizionali e forma passiva',
    shortName: 'Modali e condizionali',
    description: 'Can, may, must, should, periodo ipotetico, passivo e costruzioni correlate.'
  },
  {
    id: 'pronomi',
    name: 'Pronomi, possessivi e relativi',
    shortName: 'Pronomi',
    description: 'Pronomi personali, possessivi, dimostrativi, relativi e indefiniti.'
  },
  {
    id: 'nomi-articoli',
    name: 'Articoli, nomi e quantità',
    shortName: 'Articoli e nomi',
    description: 'Articoli, singolare e plurale, countable, much, many, some e any.'
  },
  {
    id: 'aggettivi-avverbi',
    name: 'Aggettivi, avverbi e comparativi',
    shortName: 'Aggettivi e avverbi',
    description: 'Posizione e forma di aggettivi e avverbi, comparativi e superlativi.'
  },
  {
    id: 'preposizioni',
    name: 'Preposizioni di tempo, luogo e movimento',
    shortName: 'Preposizioni',
    description: 'In, on, at, to, for, since, by e altre preposizioni nelle espressioni comuni.'
  },
  {
    id: 'costruzione-frase',
    name: 'Costruzione della frase e domande',
    shortName: 'Frase e domande',
    description: 'Ordine delle parole, interrogative, negazioni, discorso indiretto e question tags.'
  },
  {
    id: 'phrasal-idioms',
    name: 'Phrasal verbs ed espressioni',
    shortName: 'Phrasal verbs',
    description: 'Verbi frasali, collocazioni, modi di dire ed espressioni d’uso frequente.'
  },
  {
    id: 'vocabolario',
    name: 'Vocabolario e situazioni quotidiane',
    shortName: 'Vocabolario',
    description: 'Professioni, oggetti, luoghi, azioni e comprensione del lessico comune.'
  },
  {
    id: 'generale',
    name: 'Grammatica inglese generale',
    shortName: 'Generale',
    description: 'Quesiti trasversali e costruzioni che coinvolgono più regole grammaticali.'
  }
];

export const subjectTopics = {
  chimica: chemistryTopics,
  fisica: physicsTopics,
  informatica: computerScienceTopics,
  storia: historyTopics,
  inglese: englishTopics
};

export function normalizeSubjectText(value) {
  return String(value ?? '')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function questionText(question, includeAnswers = false) {
  const answers = includeAnswers ? ` ${(question?.answers ?? []).join(' ')}` : '';
  return normalizeSubjectText(`${question?.text ?? ''}${answers}`);
}

function questionCorrectText(question, includeAnswer = false) {
  const answer = includeAnswer && Number.isInteger(question?.correct) ? ` ${question?.answers?.[question.correct] ?? ''}` : '';
  return normalizeSubjectText(`${question?.text ?? ''}${answer}`);
}

function chemistryTopic(question, includeAnswers = false) {
  const text = questionText(question, includeAnswers);

  if (/\b(ph|acid[oaie]|acidita|basic[oaie]|basicita|alcalin|neutralizz|indicatore|cartina tornasole|ione idrogeno|ioni h|ioni oh)\b/.test(text)) return 'acidi-basi';
  if (/\b(idrocarbur|alcan[oi]|alchen[oi]|alchin[oi]|benzene|metano|etano|propano|butano|alcool|alcol|etanolo|metanolo|aldeid|cheton|ester[ei]|eter[ei]|ammid[ei]|ammin[ae]|carbossil|organico|isomer|polimer|monomer|plastica|pvc|gruppo funzionale)\b/.test(text)) return 'organica';
  if (/\b(protein|amminoacid|carboidrat|glucid|zuccher|lipid|grass[oi]|vitamin|enzim|dna|rna|cellul[ae]|metabolism|respirazione cellulare|fotosintes|fermentaz|lievit|clorofill|emoglobin|inquin|ozono|effetto serra|combustibil|carburant|petrolio|carbone|torba|biodegrad|detergent|sapone|disinfett)\b/.test(text)) return 'bio-applicata';
  if (/\b(mol[ei]|massa molare|peso molecolare|numero di avogadro|stechiometri|concentraz|molarita|molalita|soluzion[ei]|solut[oi]|solvent[ei]|solubil|diluizion|osmosi|osmotica|salinita|acqua di mare|percentuale in massa|titolo della soluzione)\b/.test(text)) return 'moli-soluzioni';
  if (/\b(bilancia|bilanciamento|equazione chimica|reazion[ei]|reagent[ei]|prodott[oi] della reazione|ossidoriduz|redox|ossidazion|riduzion|numero di ossidazione|lavoisier|proust|dalton|legge delle proporzioni|legge di conservazione|conservazione della massa|catalizzator|velocita di reazione|equilibrio chimico|elettrolisi|combustione|comburente|esotermic|endotermic)\b/.test(text)) return 'reazioni';
  if (/\b(atomo|atomic[oaie]|nucleo|proton[ei]|elettron[ei]|neutron[ei]|isotop|element[oi]|simbolo chimico|numero di massa|numero atomico|tavola periodica|sistema periodico|gruppo [ivx0-9]|periodo [ivx0-9]|metall[oi]|non metall[oi]|lantanoid|attinoid|gas nobil[ei]|alogen[oi]|calcogen[oi]|elettronegativ|energia di ionizzazione|orbitale|numeri quantici|configurazione elettronica)\b/.test(text)) return 'atomo';
  if (/\b(legame|covalent|ionic[oaie]|metallic[oaie]|valenz[ae]|molecol[ae]|formula|compost[oi]|nomenclatura|ion[ei]|cation[ei]|anion[ei]|ossid[oi]|anidrid[ei]|idrossid[oi]|idrur[oi]|clorur[oi]|solfur[oi]|nitrato|nitrito|fosfato|carbonato|bicarbonato|sale binario|sali binari)\b/.test(text)) return 'legami';
  if (/\b(stato solido|stato liquido|stato gassoso|stati di aggregazione|solidi|liquidi|aeriform[ei]|vapor[ei]|gas ideale|gas perfetto|pressione parziale|volume molare|passaggio di stato|passaggio di fase|fusione|solidificazione|ebollizione|evaporazione|condensazione|sublimazione|brinamento|dilatazione termica|temperatura critica|calore latente|legge di boyle|gay lussac|charles)\b/.test(text)) return 'stati-gas';
  if (/\b(materia|sostanza pura|miscugli[oa]?|miscel[ae]|lega metallica|acciaio|diamante|omogene[oa]|eterogene[oa]|filtrazion|distillazion|cromatograf|centrifugazion|decantazion|separazion|densita|proprieta fisic|trasformazione fisica)\b/.test(text)) return 'materia';
  return includeAnswers ? 'generale' : chemistryTopic(question, true);
}

function physicsTopic(question, includeAnswers = false) {
  const text = questionText(question, includeAnswers);

  if (/\b(radioattiv|decadimento|particella alfa|particella beta|raggi gamma|radiazione ionizzante|fissione|fusione nucleare|nucleo atomico|atomo|proton[ei]|elettron[ei]|neutron[ei]|energia nucleare|isotop|emivita|tempo di dimezzamento|becquerel|sievert)\b/.test(text)) return 'atomica';
  if (/\b(elettric|elettrostatic|carica elettrica|corrente|tensione|differenza di potenziale|resistenz|resistivita|conduttor[ei]|isolant[ei]|circuit[oi]|legge di ohm|coulomb|voltmetro|amperometro|capacitor|condensatore|campo magnetico|magnet[ei]|elettromagnet|induzione|faraday|trasformatore)\b/.test(text)) return 'elettromagnetismo';
  if (/\b(lasciat[oa] cadere|cade |cadono |caduta libera|cascata|precipit[ae] da|tocca il suolo|profond[oa] il pozzo)\b/.test(text)) return 'cinematica';
  if (/\b(onda|ondulatori|suono|acustic|rumore|decibel|ultrasuon|infrasuon|luce|luminos|ottic|riflession|rifrazion|indice di rifrazione|specchi[oa]?|lent[ei]|prisma|diffrazion|interferenz|lunghezza d onda|spettro elettromagnetico)\b/.test(text)) return 'onde-ottica';
  if (/\b(calore|temperatura|termic|termodinamic|entropia|calorimetr|dilatazion|conduzione|convezione|irraggiamento|celsius|kelvin|fahrenheit|gas perfetto|gas ideale|equazione di stato|sistema isolato|sistema chiuso|sistema aperto|stati della materia|stati di aggregazione|passaggio di stato|fusione|ghiaccio|solidificazione|ebollizione|evaporazione|condensazione|calore specifico|calore latente)\b/.test(text)) return 'termologia';
  if (/\b(fluid[oi]|pressione|densita|peso specifico|galleggia|spinta di archimede|archimede|principio di pascal|idrostatic|idraulic|portata|viscosita|manometro|barometro|torchio|vasi comunicanti|tensione superficiale|capillarita|bernoul)\b/.test(text)) return 'fluidi';
  if (/\b(lavoro|energia cinetica|energia potenziale|energia meccanica|energia di attivazione|energia libera|conservazione dell energia|potenza|rendimento|joule|wattora|chilowattora)\b/.test(text)) return 'energia';
  if (/\b(forza|legge di newton|principio della dinamica|dinamica|equilibrio|attrito|peso |forza peso|gravita|gravitazionale|quantita di moto|impulso|momento di una forza|momento torcente|leva|fulcro|asta omogenea|incernierat|molla|costante elastica|dinamometro|legge di hooke|forza centripeta|forza centrifuga)\b/.test(text)) return 'dinamica';
  if (/\b(moto |moto$|muoversi|velocita|decelerazion|accelerazion|spazio percorso|distanza percorsa|traiettoria|pendolo|oscillazion|periodo|frequenza|moto rettilineo|moto circolare|moto uniforme|moto uniformemente accelerato|velocita angolare|frequenza di rotazione|periodo di rotazione|gittata)\b/.test(text)) return 'cinematica';
  if (/\b(unita di misura|sistema internazionale|sistema cgs|grandezza |grandezze |grandezza fisica|grandezza scalare|grandezza vettoriale|estensiva|intensiva|vettore|prodotto scalare|somma di due vettori|errore assoluto|errore relativo|accuratezza|precisione di una misura|sensibilita dello strumento|strumento di misura|misurazione|cifre significative|notazione esponenziale|proporzional|valore medio|conversione|corrisponde a|equivalgono|equivale|micrometro|nanometro|millimetri|millilitro|chilogrammo|metro al secondo|dimensionale|dimensioni fisiche)\b/.test(text)) return 'misure';
  return includeAnswers ? 'generale' : physicsTopic(question, true);
}

function computerScienceTopic(question, includeAnswers = false) {
  const text = questionCorrectText(question, includeAnswers);

  if (/\b(virus|antivirus|malware|trojan|worm|spyware|ransomware|adware|phishing|spam|firewall|password|credenzial|autenticazion|crittograf|cifratur|firma digitale|certificato digitale|sicurezza informatica|attacco informatico|hacker|backup|back up|copia di sicurezza|protezione dei dati|privacy)\b/.test(text)) return 'sicurezza';
  if (/\b(microsoft word|ms word|word(?: 20)?|winword|elaboratore di testi|elaborazione testi|videoscrittura|documento word|file doc|estensione doc|estensione dot|intestazione|pie di pagina|stampa unione|wordart|formattazione del testo|formattare un testo|formattazione.+paragrafo|formato del carattere|apice|pedice|salva con nome|barra della formattazione)\b/.test(text)) return 'word';
  if (/\b(microsoft excel|ms excel|excel(?: 20)?|fogli? di calcolo|foglio elettronico|cartella di lavoro|cella [a-z][0-9]|formula |funzione somma|funzione media|tabella pivot|riferimento assoluto|riferimento relativo|formato celle|barra della formula)\b/.test(text)) return 'excel';
  if (/\b(powerpoint|power point|presentazion|diapositiv|slide show|layout.+diapositiva|outlook|posta elettronica|e mail|email|messaggio di posta|access |microsoft access|database|base di dati|rdbms|record |query |tabella relazionale|pps|ppt|mdb)\b/.test(text)) return 'office-dati';
  if (/\b(rete |reti |lan |wan |man |pan |vpn|router|switch|hub |modem|ethernet|wi fi|wireless|bluetooth|indirizzo ip|protocollo|tcp|udp|dns|dhcp|ftp|http|https|qos|larghezza di banda|topologia|client server|peer to peer|nas |server |intranet|extranet|scheda di rete|fibra ottica|fibre ottiche|telefonia mobile|umts)\b/.test(text)) return 'reti';
  if (/\b(internet|world wide web|www|sito web|pagina web|pagine web|html|dominio|browser|motore di ricerca|url|link |collegamento ipertestuale|home page|homepage|google|street view|social network|chat |videochiamata|google meet|zoom|blog|forum|e commerce|commercio elettronico|home banking|cloud computing|servizio cloud|cloud storage|spid|identita digitale|telelavoro|smart working|provider|isp |portale web|cookie)\b/.test(text)) return 'internet';
  if (/\b(sistema operativo|windows|linux|unix|android|ios |macos|dos |file |files |cartella|directory|estensione |exe |bat |cmd |taskbar|barra delle applicazioni|pannello di controllo|cestino|desktop|gestione risorse|processo |processi |memoria virtuale|clipboard|appunti|prompt dei comandi|avvio del computer|deframmentazione|partizione|formattazione.+disco|virtual machine)\b/.test(text)) return 'sistemi-file';
  if (/\b(cpu|processore|microprocessore|unit[a-z]* centrale|scheda madre|motherboard|ram |rom |cache |memoria centrale|memoria di massa|hard disk|disco rigido|ssd |cd rom|dvd |blu ray|chiavetta|pen drive|usb|periferica|scanner|stampante|monitor|schermo|tastiera|mouse|touchpad|webcam|plotter|pixel|risoluzione dello schermo|porta seriale|porta parallela|hardware|notebook|laptop|computer portatile|mainframe|smartphone|masterizzatore|gigabyte|megabyte|terabyte|kilobyte|registri? di memoria|input |output |bios|uefi|ocr|altoparlante)\b/.test(text)) return 'hardware';
  if (/\b(software|programma|applicazione|algoritmo|programmazione|linguaggio di programmazione|codice sorgente|compilatore|interprete|bug |debug|open source|freeware|shareware|licenza|bit |byte|binario|esadecimale|ascii|unicode|codifica|informazione digitale|compressione|formato digitale|testo digitale|ipertesto|tecnologie dell informazione|acronimo tic|array|overloading|istruzione break)\b/.test(text)) return 'software-dati';
  return includeAnswers ? 'generale' : computerScienceTopic(question, true);
}

function historyTopic(question, includeAnswers = false) {
  const text = questionCorrectText(question, includeAnswers);

  if (/\b(seconda guerra mondiale|secondo conflitto mondiale|campagna di russia|guerra mondiale del 1939|resistenza|resistent[ei]|partigian|liberazione|25 aprile|8 settembre|armistizio|repubblica sociale|repubblica di salo|linea gotica|linea gustav|alleati|sbarco in sicilia|monte cassino|cln |comitato di liberazione|badoglio|deportazion|olocausto|shoah|foss[ae] ardeatine|via rasella|marzabotto|cef[au]lonia)\b/.test(text)) return 'seconda-guerra';
  if (/\b(fascis|mussolini|duce |marcia su roma|matteotti|leggi fascistissime|gran consiglio|ovra|camicie nere|squadris|corporativ|patti lateranensi|leggi razziali|confino|partito nazionale fascista|regime fascista|aventino|bonifica integrale|battaglia del grano|quota novanta|istituto luce|biennio rosso|italo balbo|patto d acciaio)\b/.test(text)) return 'fascismo';
  if (/\b(prima guerra mondiale|primo conflitto mondiale|grande guerra|caporetto|vittorio veneto|piave|isonzo|triplice intesa|neutralis|interventis|trincea|strafexpedition|spedizione punitiva|patto di londra|armando diaz|luigi cadorna)\b/.test(text)) return 'prima-guerra';
  if (/\b(giolitti|giolittian|guerra di libia|impresa di libia|patto gentiloni|suffragio universale|settimana rossa)\b/.test(text)) return 'eta-giolittiana';
  if (/\b(risorgimento|restaurazione|congresso di vienna|unita d italia|regno d italia|regno di sardegna|regno delle due sicilie|lombardo veneto|quadrilatero|garibald|mazzini|cavour|vittorio emanuele ii|carlo pisacane|fratelli bandiera|mameli|pio ix|gioberti|cesare balbo|massimo d azeglio|cattaneo|spedizione dei mille|mille |guerra d indipendenza|prima guerra d indipendenza|seconda guerra d indipendenza|terza guerra d indipendenza|guerra di crimea|carbonar|giovine italia|repubblica romana|cinque giornate|porta pia|breccia di porta pia|plebiscit|statuto albertino|neoguelfis|moti del 182|moti del 183|moti del 184|villafranca|solferino|san martino|teano|aspromonte|mentana|calatafimi|caprera|quarto|marsala)\b/.test(text)) return 'risorgimento';
  if (/\b(destra storica|sinistra storica|depretis|crispi|minghetti|quintino sella|rudini|pelloux|zanardelli|umberto i|margherita di savoia|trasformismo|brigantaggio|questione meridionale|tassa sul macinato|corso forzoso|legge delle guarentigie|non expedit|triplice alleanza|adua|dogali|etiopia|eritrea|somalia|colonial|scandalo della banca romana)\b/.test(text)) return 'italia-postunitaria';
  if (/\b(referendum istituzionale|assemblea costituente|costituente|costituzione italiana|repubblica italiana|2 giugno|de gasperi|togliatti|einaudi|ferruccio parri|umberto ii|uomo qualunque|ugo la malfa|elezioni del 1948|piano marshall|ricostruzione|centrismo|miracolo economico|cassa per il mezzogiorno|anni cinquanta|emigrazione)\b/.test(text)) return 'repubblica-primi-anni';
  if (/\b(tambroni|moro |andreotti|craxi|berlinguer|pertini|leone |cossiga|scalfaro|ciampi|napolitano|nilde iotti|spadolini|karol wojtyla|giovanni paolo|partito repubblicano|partito radicale|pentapartito|democrazia cristiana|partito comunista italiano|centro sinistra|compromesso storico|anni di piombo|brigate rosse|terrorismo|gruppo terrorista|nar |lupi grigi|strategia della tensione|piazza fontana|italicus|stazione di bologna|p2 |tangentopoli|mani pulite|sessantotto|movimento del settantasette|mafia|borsellino|falcone|dalla chiesa)\b/.test(text)) return 'repubblica-contemporanea';
  if (/\b(rivoluzione industriale|rivoluzione francese|stati uniti|guerra civile americana|guerra di secessione|impero austro ungarico|impero ottomano|germania|francia|inghilterra|gran bretagna|russia|unione sovietica|urss|guerra fredda|nato |patto di varsavia|onu |societa delle nazioni|colonialismo|imperialismo|bismarck|napoleone|marx|lenin|stalin|kennedy|europa)\b/.test(text)) return 'storia-internazionale';
  const years = [...text.matchAll(/\b(1[789]\d{2}|20\d{2})\b/g)].map(match => Number(match[1]));
  if (years.some(year => year >= 1939 && year <= 1945)) return 'seconda-guerra';
  if (years.some(year => year >= 1919 && year <= 1938)) return 'fascismo';
  if (years.some(year => year >= 1914 && year <= 1918)) return 'prima-guerra';
  if (years.some(year => year >= 1900 && year <= 1913)) return 'eta-giolittiana';
  if (years.some(year => year >= 1861 && year <= 1899)) return 'italia-postunitaria';
  if (years.some(year => year >= 1789 && year <= 1860)) return 'risorgimento';
  if (years.some(year => year >= 1946 && year <= 1959)) return 'repubblica-primi-anni';
  if (years.some(year => year >= 1960)) return 'repubblica-contemporanea';
  return includeAnswers ? 'generale' : historyTopic(question, true);
}

function normalizedAnswers(question) {
  return (question?.answers ?? []).map(answer => normalizeSubjectText(answer));
}

function englishTopic(question, includeAnswers = false) {
  const text = questionCorrectText(question, includeAnswers), answers = normalizedAnswers(question), correctAnswer = Number.isInteger(question?.correct) ? answers[question.correct] ?? '' : '', answerLine = answers.join(' '), answerCount = pattern => answers.filter(answer => pattern.test(answer)).length, threshold = Math.max(2,Math.ceil(answers.length*.6));

  if (/\b(phrasal verb|idiom|expression|look forward|look after|look for|give up|turn on|turn off|take off|put on|get up|get along|get in touch|carry on|find out|pick up|run out|set up|break down|come across|deal with|move in|wake up|go straight|turn left|turn right|according to|in spite of|as soon as)\b/.test(text)||/\b(look(?:ing)? forward to|look after|look for|give up|turn on|turn off|take off|put on|get up|get along|carry on|find out|pick up|run out|set up|break down|come across|deal with|move in|wake up|straight on)\b/.test(correctAnswer)) return 'phrasal-idioms';
  if (/\b(preposition|preposizione)\b/.test(text)||answers.length>=2&&answers.every(answer=>/^(at|in|on|to|from|for|since|by|with|without|about|above|across|after|against|along|among|around|before|behind|below|beside|between|during|into|near|of|off|over|through|towards|under|until|up|within)( the)?$/.test(answer))||/^(at|in|on|to|from|for|since|by|with|without|about|above|across|after|against|along|among|around|before|behind|below|beside|between|close to|during|into|near|of|off|over|through|towards|under|until|up|within)( the| tv| two weeks)?$/.test(correctAnswer)) return 'preposizioni';
  if (/\b(comparative|superlative|adjective|adverb|comparativo|superlativo)\b/.test(text)||/\b(more |most |less |least |better|best|worse|worst|than )\b/.test(answerLine)) return 'aggettivi-avverbi';
  if (/\b(pronoun|possessive|relative pronoun|personal pronoun|demonstrative|whose|whom)\b/.test(text)||answerCount(/^(i|me|my|mine|myself|you|you all|your|yours|yourself|he|him|his|himself|she|her|hers|herself|it|its|itself|we|we all|us|our|ours|ourselves|they|they all|them|their|theirs|themselves|who|whom|whose|which|that|this|these|those|someone|anyone|everyone|nobody|nothing|one|ones)$/)>=threshold) return 'pronomi';
  if (/\b(article|plural|singular|countable|uncountable|noun |much |many |some |any |few |little |a lot of|how much|how many)\b/.test(text)||answerCount(/^(a|an|the|a the|an the|some|any|much|many|few|a few|little|a little|no|none)$/)>=threshold) return 'nomi-articoli';
  if (/\b(question tag|reported speech|direct speech|indirect speech|same meaning|sentence that is correct|correct sentence|word order|interrogative|negative form|ask a question|question form|short answer|too |enough |so that|such a|same .+ as|either |neither |both |although |though |because |despite |while |there is|there are|let s|so do i|yes i|no i)\b/.test(text)||/^(do|does|did|is|are|was|were|have|has|had|can|could|will|would|where|when|why|how|what|who)\b.+_{2,}/.test(text)||answerCount(/^(because|although|though|but|so|and|or|since|while|whereas|however|therefore|neither|either|both|too|enough)$/)>=threshold||/^(do i|did i|am i|have i|can i|could i|will i|would i|yes|no)\b/.test(correctAnswer)) return 'costruzione-frase';
  if (/\b(conditional|passive|active voice|if clause|periodo ipotetico|modal verb)\b/.test(text)||/\b(if|unless|would have|could have|should have|must have|can|could|may|might|must|should|would|ought to|have to|has to|had to)\b/.test(correctAnswer)) return 'modali-condizionali';
  if (/\b(present simple|present continuous|present perfect|past simple|past continuous|past perfect|future simple|future perfect|verb tense|correct tense|forma verbale|tempo verbale|ago |yesterday|last night|last week|since |for two|for three|already|yet |just |ever |never |recently|now |today|tomorrow|every day|usually|often|always|at the moment|while |when i |when he |when she |by the time)\b/.test(text)||/\b(have been|has been|had been|will have|was |were |did |has |have |had |will )\b/.test(correctAnswer)||/\b(am|is|are|was|were|been|being|do|does|did|done|have|has|had|will|shall|going to|ing|ed)\b/.test(correctAnswer)) return 'tempi-verbali';
  if (/\b(what do you call|is called|means|meaning|synonym|opposite|right translation|traduz|odd one out|what do you do|what time is it|which month|profession|job |works in|works at|serves you|person who|place where|animal|food|clothes|weather|body|house|family|airport|restaurant|hospital|school|office|musical instrument|tail |traffic lights|promotion|debt |cheap |expensive)\b/.test(text)) return 'vocabolario';
  return includeAnswers ? 'generale' : englishTopic(question, true);
}

export function classifySubjectQuestion(question) {
  if (question?.category === 'chimica') return chemistryTopic(question);
  if (question?.category === 'fisica') return physicsTopic(question);
  if (question?.category === 'informatica') return computerScienceTopic(question);
  if (question?.category === 'storia') return historyTopic(question);
  if (question?.category === 'inglese') return englishTopic(question);
  return null;
}

export function topicDefinition(category, topicId) {
  return subjectTopics[category]?.find(topic => topic.id === topicId) ?? null;
}
