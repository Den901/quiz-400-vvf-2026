import {classifyLogicQuestion,normalizedQuestionText} from './logic-topics.js?v=57';
import {classifySubjectQuestion} from './subject-topics.js?v=57';

const LOGIC_CATEGORIES=new Set(['logica','brani','insiemi']);
const RESOURCE_TOPICS={
 'chimica-acidi-redox':['acidi-basi','reazioni'],
 'chimica-generale':['materia','atomo','legami','moli-soluzioni'],
 'informatica-base':['hardware','sistemi-file','software-dati','generale'],
 'informatica-scheda':['hardware','sistemi-file','software-dati'],
};

const focus=(ids,include,exclude=null)=>({ids:new Set(ids),include,exclude});
const FOCUS_RULES=[
 focus(['storia-unita-scheda','storia-unita'],/\b(risorgimento|unita d italia|regno d italia|regno di sardegna|regno delle due sicilie|garibaldi|mazzini|cavour|vittorio emanuele ii|carlo alberto|spedizione dei mille|guerra d indipendenza|carbonar|giovine italia|repubblica romana|cinque giornate|porta pia|statuto albertino|teano|calatafimi|marsala)\b/),
 focus(['storia-italia-prima-guerra'],/\b(italia|italian|caporetto|vittorio veneto|piave|isonzo|cadorna|diaz|patto di londra|neutralis|interventis|strafexpedition)\b/),
 focus(['storia-primo-dopoguerra'],/\b(primo dopoguerra|biennio rosso|vittoria mutilata|fiume|d annunzio|fasci di combattimento|partito popolare|partito socialista|trattato di rapallo)\b/),
 focus(['storia-crisi-1929'],/\b(1929|wall street|new deal|roosevelt|grande depressione|crisi economica|nazismo|hitler|stalin|totalitari)\b/),
 focus(['storia-fascismo'],/\b(fascis|mussolini|duce|marcia su roma|matteotti|leggi fascistissime|gran consiglio|ovra|camicie nere|squadris|corporativ|patti lateranensi|leggi razziali|aventino)\b/),
 focus(['storia-seconda-guerra'],/\b(seconda guerra mondiale|secondo conflitto mondiale|guerra mondiale|hitler|germania|polonia|stalingrado|el alamein|sbarco in sicilia|normandia|pearl harbor|hiroshima|nagasaki|asse roma berlino|patto d acciaio)\b/,/\b(resistenza|partigian|cln|repubblica sociale|repubblica di salo)\b/),
 focus(['storia-resistenza'],/\b(resistenza|partigian|liberazione|25 aprile|8 settembre|armistizio|repubblica sociale|repubblica di salo|cln|comitato di liberazione|linea gotica|linea gustav|foss[ae] ardeatine|via rasella|marzabotto)\b/,/\b(villa giusti|1918)\b/),
 focus(['storia-secondo-dopoguerra'],/\b(secondo dopoguerra|guerra fredda|nato|patto di varsavia|piano marshall|urss|unione sovietica|ricostruzione|blocco occidentale|blocco sovietico)\b/),
 focus(['storia-repubblicana'],/\b(referendum istituzionale|assemblea costituente|costituzione italiana|repubblica italiana|2 giugno|de gasperi|togliatti|einaudi|elezioni del 1948|centrismo|miracolo economico)\b/),
 focus(['storia-anni-piombo'],/\b(anni di piombo|brigate rosse|terrorismo|strategia della tensione|piazza fontana|italicus|stazione di bologna|rapimento moro|sessantotto|movimento del settantasette)\b/),
 focus(['storia-1980-oggi'],/\b(craxi|tangentopoli|mani pulite|seconda repubblica|berlusconi|prodi|scalfaro|ciampi|napolitano|pentapartito|lega nord)\b/),
 focus(['storia-malavita'],/\b(mafia|cosa nostra|camorra|ndrangheta|falcone|borsellino|dalla chiesa|antimafia|capaci|via d amelio|buscetta|riina)\b/),

 focus(['logica-sinonimi-1','logica-sinonimi-2'],/\b(sinonim\w*|contrar\w*|sostituire la parola|stesso significato|significato opposto|vocabolo)\b/),
 focus(['logica-anagrammi-1','logica-anagrammi-2'],/\b(anagramm\w*|riordinando le lettere|lettere della parola)\b/),
 focus(['logica-semantica'],/\b(significat\w*|analogia verbale|associabile|parola da scartare|termine da scartare|non attinente|classificazion\w*)\b/),
 focus(['logica-sillogismi'],/\b(sillog\w*|premess\w*|conclusion\w*|tutti gli|tutte le|nessun|alcuni|alcune)\b/),
 focus(['logica-operazioni'],/\b(somma|sottraz\w*|differenza|prodotto|quoziente|moltiplic\w*|division\w*|operazion\w*|quanto vale)\b/),
 focus(['logica-mcm-mcd'],/\b(massimo comune divisore|minimo comune multiplo|mcd|mcm|divisori|multipli comuni)\b/),
 focus(['logica-frazioni'],/\b(frazion\w*|numeratore|denominatore)\b/),
 focus(['logica-frazioni-proporzioni'],/\b(frazion\w*|proporzion\w*|rapporto)\b/),
 focus(['logica-proporzioni'],/\b(proporzion\w*|direttamente proporz\w*|inversamente proporz\w*|rapporto)\b/),
 focus(['logica-percentuali'],/\b(percent\w*|per cento|sconto|aumento percentuale|diminuzione percentuale)\b/),
 focus(['logica-equivalenze','logica-equivalenze-2','test-logica-equivalenze'],/\b(equival\w*|convert\w*|trasformare in|corrisponde a|quanti (?:metri|centimetri|millimetri|litri|grammi|chilogrammi))\b/),
 focus(['logica-multipli-sottomultipli','logica-multipli-sottomultipli-2'],/\b(multipli|sottomultipli|kilo|etto|deca|deci|centi|milli)\b/),
 focus(['logica-misure-schema','logica-lunghezze-schema'],/\b(lunghezz\w*|metro|chilometr\w*|centimetr\w*|millimetr\w*|conversion\w*|equival\w*)\b/),
 focus(['logica-superfici-schema'],/\b(superficie|area|quadrat|ettaro)\b/),
 focus(['logica-volumi-schema'],/\b(volume|cubo|cubic|litro|capacita)\b/),
 focus(['logica-grafici-tabelle','logica-rappresentazioni'],/\b(grafico|tabella|diagramma|istogramma|rappresentazione|asse delle|coordinate)\b/),
 focus(['logica-equazioni','logica-trasformazioni'],/\b(equazion\w*|incognita|uguaglianza|trasformazione simbolica)\b/),
 focus(['logica-probabilita-svolta','logica-probabilita'],/\b(probabilit\w*|evento certo|evento impossibile|casi favorevoli|casi possibili)\b/),
 focus(['logica-combinatorio','logica-combinatorio-schema'],/\b(calcolo combinatorio|combinazion\w*|permutazion\w*|disposizion\w*|quanti modi|raggruppamenti)\b/),
 focus(['logica-sequenze'],/\b(completare correttamente (?:la seguente )?(?:successione|sequenza)|numero mancante|lettera mancante|prosegue.*successione|integrare la serie)\b/),
 focus(['logica-configurazioni'],/\b(figura che completa|completa correttamente la serie|pedina mancante|numero deve logicamente integrare la struttura|matrice figur|configurazione)\b/),
 focus(['logica-attenzione'],/\b(individuare (?:la successione|la sequenza|l elemento|la figura) (?:identica|uguale)|quante volte.*elemento|attenzione|precisione)\b/),

 focus(['fisica-dinamica'],/\b(legge di newton|principio della dinamica|inerzia|massa|accelerazione|quantita di moto|impulso)\b/),
 focus(['fisica-forze'],/\b(forza di attrito|attrito|forza elastica|molla|forza peso|gravitaz|centripeta)\b/),
 focus(['fisica-statica'],/\b(equilibrio|momento di una forza|leva|fulcro|baricentro|corpo rigido|rotazione)\b/),

 focus(['chimica-acidi-redox'],/\b(acid|bas[ei]|ph|ossid|riduz|redox)\b/),
 focus(['chimica-redox'],/\b(ossid|riduz|redox|numero di ossidazione|agente ossidante|agente riducente)\b/),
 focus(['chimica-nomenclatura','chimica-nomenclatura-scheda'],/\b(nomenclatura|nome del composto|formula chimica|ossido|anidride|idrossido|idruro|sale binario)\b/),

 focus(['informatica-access'],/\b(microsoft access|ms access|database|base di dati|record|query|tabella relazionale|chiave primaria|rdbms|mdb)\b/,/\b(access point|posta elettronica|e mail|email|outlook)\b/),
 focus(['informatica-powerpoint'],/\b(powerpoint|power point|presentazion|diapositiv|slide|ppt|pps)\b/),
 focus(['informatica-stampanti'],/\b(stampante|stampa|plotter|inkjet|getto d inchiostro|toner)\b/),
 focus(['informatica-stampanti-laser'],/\b(stampante laser|laser|toner|tamburo|fotoconduttore)\b/),
];

function questionText(question){
 return normalizedQuestionText(`${question?.text??question?.domanda??''} ${(question?.answers??[]).join(' ')}`);
}

export function studyQuestionTopics(resource){
 return [...new Set(RESOURCE_TOPICS[resource?.id]??[resource?.topic].filter(Boolean))];
}

export function checkpointQuestionPool(resource,questions=[]){
 const topics=new Set(studyQuestionTopics(resource));
 if(!topics.size)return[];
 const candidates=resource?.pathId==='logica'
  ?questions.filter(question=>LOGIC_CATEGORIES.has(question?.category)&&topics.has(classifyLogicQuestion(question)))
  :questions.filter(question=>question?.category===resource?.pathId&&topics.has(classifySubjectQuestion(question)));
 const rule=FOCUS_RULES.find(item=>item.ids.has(resource?.id));
 if(!rule)return candidates;
 const focused=candidates.filter(question=>{const text=questionText(question);return rule.include.test(text)&&(!rule.exclude||!rule.exclude.test(text))});
 return focused;
}

export function checkpointTopicSummary(resource){
 return studyQuestionTopics(resource).join(', ');
}
