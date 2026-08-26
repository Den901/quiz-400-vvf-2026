import {elementPropertiesByAtomicNumber} from './element-properties.js?v=53';
import {computerScienceNotes, englishNotes, logicNotes} from './practice-notes.js?v=53';

export {computerScienceNotes, englishNotes, logicNotes};

const note = (term, definition, formula = '', tip = '') => ({term, definition, formula, tip});

export const chemistryNotes = [
  {
    id: 'materia-atomo',
    title: 'Materia, sostanze e atomo',
    summary: 'Le definizioni da riconoscere subito nei quesiti.',
    items: [
      note('Materia', 'Tutto ciò che ha massa e occupa spazio.'),
      note('Sostanza pura', 'Materia con composizione definita. Può essere un elemento o un composto.'),
      note('Miscuglio', 'Insieme di più sostanze. È omogeneo se presenta una sola fase, eterogeneo se ne presenta più di una.'),
      note('Elemento', 'Sostanza formata da atomi con lo stesso numero atomico Z.'),
      note('Composto', 'Sostanza formata da elementi diversi uniti in rapporti definiti.'),
      note('Atomo', 'È formato da un nucleo con protoni e neutroni e da elettroni distribuiti attorno al nucleo.'),
      note('Numero atomico Z', 'Numero di protoni. In un atomo neutro coincide con il numero di elettroni.', 'Z = protoni'),
      note('Numero di massa A', 'Somma di protoni e neutroni nel nucleo.', 'A = Z + N'),
      note('Isotopi', 'Atomi dello stesso elemento con uguale Z ma diverso numero di neutroni e quindi diverso A.'),
      note('Ione', 'Atomo o gruppo con carica: perde elettroni e diventa catione positivo; acquista elettroni e diventa anione negativo.')
    ]
  },
  {
    id: 'tavola-andamenti',
    title: 'Tavola periodica e proprietà',
    summary: 'Gruppi, periodi e principali andamenti periodici.',
    items: [
      note('Gruppo', 'Colonna della tavola. Gli elementi dello stesso gruppo hanno spesso proprietà chimiche simili.'),
      note('Periodo', 'Riga della tavola. Indica il livello energetico principale occupato dagli elettroni più esterni.'),
      note('Metalli', 'In genere buoni conduttori, lucenti, malleabili e tendono a perdere elettroni.'),
      note('Non metalli', 'In genere cattivi conduttori e tendono ad acquistare o condividere elettroni.'),
      note('Raggio atomico', 'In generale aumenta scendendo in un gruppo e diminuisce andando da sinistra a destra in un periodo.', '', 'Immagina una freccia verso il basso e verso sinistra.'),
      note('Elettronegatività', 'Tendenza ad attirare gli elettroni di legame. In generale aumenta verso destra e verso l’alto.', '', 'Il fluoro è l’elemento più elettronegativo.'),
      note('Energia di ionizzazione', 'Energia necessaria per rimuovere un elettrone da un atomo isolato. In generale aumenta verso destra e verso l’alto.'),
      note('Gas nobili', 'Elementi del gruppo 18, poco reattivi perché hanno il livello elettronico esterno completo.')
    ]
  },
  {
    id: 'legami',
    title: 'Legami e forze intermolecolari',
    summary: 'Come e perché gli atomi si uniscono.',
    items: [
      note('Legame ionico', 'Attrazione tra ioni di carica opposta, tipica tra un metallo e un non metallo dopo trasferimento di elettroni.'),
      note('Legame covalente', 'Due atomi condividono una o più coppie di elettroni.'),
      note('Covalente polare', 'La coppia elettronica è condivisa in modo diseguale per la diversa elettronegatività degli atomi.'),
      note('Legame metallico', 'I cationi metallici sono tenuti insieme da elettroni delocalizzati; spiega conducibilità e malleabilità.'),
      note('Legame a idrogeno', 'Attrazione intermolecolare intensa quando H è legato a F, O o N.'),
      note('Polarità della molecola', 'Dipende dalla polarità dei legami e dalla geometria: legami polari possono compensarsi in una molecola simmetrica.')
    ]
  },
  {
    id: 'mole-soluzioni',
    title: 'Mole, massa e soluzioni',
    summary: 'Le relazioni numeriche più frequenti.',
    items: [
      note('Mole', 'Quantità di sostanza che contiene esattamente 6,02214076 × 10²³ entità elementari.', 'N = n · Nₐ'),
      note('Massa molare', 'Massa di una mole di sostanza, espressa normalmente in g/mol.', 'n = m / M'),
      note('Soluzione', 'Miscuglio omogeneo formato da solvente e uno o più soluti.'),
      note('Concentrazione molare', 'Moli di soluto presenti in un litro di soluzione.', 'c = n / V'),
      note('Percentuale in massa', 'Rapporto percentuale tra massa del soluto e massa della soluzione.', '% m/m = m soluto / m soluzione · 100'),
      note('Diluizione', 'Le moli di soluto restano costanti quando si aggiunge soltanto solvente.', 'c₁V₁ = c₂V₂')
    ]
  },
  {
    id: 'reazioni',
    title: 'Reazioni e bilanciamento',
    summary: 'Conservazione della massa, coefficienti e tipi di reazione.',
    items: [
      note('Legge di Lavoisier', 'In una reazione chimica la massa totale dei reagenti è uguale alla massa totale dei prodotti.', 'massa reagenti = massa prodotti'),
      note('Bilanciamento', 'Si modificano soltanto i coefficienti davanti alle formule, mai gli indici dentro le formule.'),
      note('Sintesi', 'Più reagenti formano un solo prodotto generale.', 'A + B → AB'),
      note('Decomposizione', 'Un composto si divide in sostanze più semplici.', 'AB → A + B'),
      note('Scambio semplice', 'Un elemento sostituisce un altro in un composto.', 'A + BC → AC + B'),
      note('Doppio scambio', 'Due composti si scambiano ioni o gruppi.', 'AB + CD → AD + CB'),
      note('Ossidazione', 'Perdita di elettroni e aumento del numero di ossidazione.'),
      note('Riduzione', 'Acquisto di elettroni e diminuzione del numero di ossidazione.', '', 'Ossidante si riduce; riducente si ossida.')
    ]
  },
  {
    id: 'acidi-basi',
    title: 'Acidi, basi e pH',
    summary: 'Definizioni essenziali e scala del pH.',
    items: [
      note('Acido di Brønsted', 'Specie che cede protoni H⁺.'),
      note('Base di Brønsted', 'Specie che accetta protoni H⁺.'),
      note('pH', 'Misura logaritmica legata alla concentrazione degli ioni H₃O⁺.', 'pH = −log₁₀[H₃O⁺]'),
      note('Scala a 25 °C', 'Una soluzione è acida se pH < 7, neutra se pH = 7, basica se pH > 7.'),
      note('Neutralizzazione', 'Reazione tra acido e base che produce in genere sale e acqua.'),
      note('Acido o base forte', 'In acqua si ionizza quasi completamente; “forte” non significa necessariamente “concentrato”.')
    ]
  },
  {
    id: 'stati-gas',
    title: 'Stati della materia e gas',
    summary: 'Passaggi di stato e relazioni fondamentali.',
    items: [
      note('Fusione / solidificazione', 'Passaggio solido → liquido / liquido → solido.'),
      note('Vaporizzazione / condensazione', 'Passaggio liquido → gas / gas → liquido.'),
      note('Sublimazione / brinamento', 'Passaggio diretto solido → gas / gas → solido.'),
      note('Temperatura assoluta', 'La temperatura in kelvin si ottiene sommando 273,15 alla temperatura in gradi Celsius.', 'T(K) = t(°C) + 273,15'),
      note('Gas ideale', 'Modello in cui particelle puntiformi non interagiscono se non tramite urti elastici.', 'pV = nRT'),
      note('Legge di Boyle', 'A temperatura costante, pressione e volume di una quantità fissa di gas sono inversamente proporzionali.', 'p₁V₁ = p₂V₂')
    ]
  }
];

export const physicsNotes = [
  {
    id: 'si-misure',
    title: 'SI, misure e grandezze',
    summary: 'Le sette unità fondamentali e le grandezze derivate più usate.',
    items: [
      note('Lunghezza', 'Grandezza fondamentale; unità SI metro.', 'm'),
      note('Massa', 'Grandezza fondamentale; unità SI chilogrammo.', 'kg'),
      note('Tempo', 'Grandezza fondamentale; unità SI secondo.', 's'),
      note('Corrente elettrica', 'Grandezza fondamentale; unità SI ampere.', 'A'),
      note('Temperatura termodinamica', 'Grandezza fondamentale; unità SI kelvin.', 'K'),
      note('Quantità di sostanza', 'Grandezza fondamentale; unità SI mole.', 'mol'),
      note('Intensità luminosa', 'Grandezza fondamentale; unità SI candela.', 'cd'),
      note('Forza', 'Unità derivata newton.', '1 N = 1 kg·m/s²'),
      note('Energia e lavoro', 'Unità derivata joule.', '1 J = 1 N·m'),
      note('Potenza', 'Unità derivata watt.', '1 W = 1 J/s'),
      note('Pressione', 'Unità derivata pascal.', '1 Pa = 1 N/m²'),
      note('Prefissi utili', 'kilo k = 10³; centi c = 10⁻²; milli m = 10⁻³; micro µ = 10⁻⁶; nano n = 10⁻⁹.')
    ]
  },
  {
    id: 'cinematica',
    title: 'Cinematica',
    summary: 'Descrive il moto senza studiarne le cause.',
    items: [
      note('Velocità media', 'Rapporto tra spostamento e intervallo di tempo.', 'vₘ = Δs / Δt'),
      note('Accelerazione media', 'Variazione della velocità nell’unità di tempo.', 'aₘ = Δv / Δt'),
      note('Moto rettilineo uniforme', 'Velocità costante e accelerazione nulla.', 's = s₀ + vt'),
      note('Moto uniformemente accelerato', 'Accelerazione costante.', 'v = v₀ + at; s = s₀ + v₀t + ½at²'),
      note('Caduta libera', 'Moto accelerato dalla gravità trascurando l’aria.', 'g ≈ 9,81 m/s²'),
      note('Moto circolare uniforme', 'Il modulo della velocità è costante, ma la direzione cambia.', 'a꜀ = v²/r')
    ]
  },
  {
    id: 'dinamica',
    title: 'Dinamica e leggi di Newton',
    summary: 'Le cause del moto e le forze.',
    items: [
      note('Prima legge · inerzia', 'Un corpo mantiene quiete o moto rettilineo uniforme se la risultante delle forze è nulla.', 'ΣF = 0 ⇒ a = 0'),
      note('Seconda legge', 'La risultante delle forze è uguale al prodotto di massa e accelerazione.', 'ΣF = ma'),
      note('Terza legge', 'A ogni forza esercitata da un corpo su un altro corrisponde una forza uguale e opposta esercitata dal secondo sul primo.'),
      note('Peso', 'Forza gravitazionale esercitata dalla Terra su un corpo.', 'P = mg'),
      note('Attrito', 'Forza che si oppone al moto relativo o alla sua tendenza.', 'Fₐ ≤ μₛN; Fₐ = μdN'),
      note('Equilibrio', 'Per l’equilibrio traslazionale la somma vettoriale delle forze deve essere zero; per quello rotazionale anche la somma dei momenti deve essere zero.')
    ]
  },
  {
    id: 'energia',
    title: 'Lavoro, energia e potenza',
    summary: 'Relazioni tra forze, movimento e trasformazioni energetiche.',
    items: [
      note('Lavoro di una forza costante', 'Prodotto scalare tra forza e spostamento.', 'L = Fs cosθ'),
      note('Energia cinetica', 'Energia associata al movimento.', 'E꜀ = ½mv²'),
      note('Energia potenziale gravitazionale', 'Vicino alla superficie terrestre dipende da massa e altezza.', 'Eₚ = mgh'),
      note('Teorema dell’energia cinetica', 'Il lavoro totale compiuto su un corpo è uguale alla variazione della sua energia cinetica.', 'Ltot = ΔE꜀'),
      note('Conservazione dell’energia', 'In un sistema isolato l’energia totale non si crea né si distrugge, ma si trasforma.'),
      note('Potenza', 'Rapidità con cui viene compiuto lavoro o trasferita energia.', 'P = L/Δt')
    ]
  },
  {
    id: 'fluidi',
    title: 'Fluidi',
    summary: 'Densità, pressione e principi fondamentali.',
    items: [
      note('Densità', 'Rapporto tra massa e volume.', 'ρ = m/V'),
      note('Pressione', 'Forza perpendicolare distribuita su una superficie.', 'p = F/S'),
      note('Pressione idrostatica', 'Aumenta con densità del fluido e profondità.', 'p = p₀ + ρgh'),
      note('Principio di Pascal', 'Una variazione di pressione applicata a un fluido confinato si trasmette inalterata a ogni punto del fluido.'),
      note('Principio di Archimede', 'Un corpo immerso riceve una spinta verso l’alto uguale al peso del fluido spostato.', 'Fₐ = ρfluido·g·Vimmerso'),
      note('Portata volumica', 'Volume di fluido che attraversa una sezione nell’unità di tempo.', 'Q = V/t = Sv')
    ]
  },
  {
    id: 'termologia',
    title: 'Calore e termodinamica',
    summary: 'Temperatura, scambi di calore e trasformazioni.',
    items: [
      note('Temperatura', 'Misura legata allo stato termico; non coincide con il calore.'),
      note('Calore', 'Energia trasferita tra corpi per differenza di temperatura.'),
      note('Calore sensibile', 'Energia necessaria a variare la temperatura senza passaggio di stato.', 'Q = mcΔT'),
      note('Calore latente', 'Energia assorbita o ceduta durante un passaggio di stato a temperatura costante.', 'Q = mλ'),
      note('Primo principio', 'La variazione di energia interna è il calore fornito al sistema meno il lavoro compiuto dal sistema.', 'ΔU = Q − L'),
      note('Trasmissione del calore', 'Conduzione: contatto; convezione: movimento del fluido; irraggiamento: onde elettromagnetiche.')
    ]
  },
  {
    id: 'onde-ottica',
    title: 'Onde, suono e ottica',
    summary: 'Le relazioni essenziali per fenomeni ondulatori e luce.',
    items: [
      note('Onda', 'Propagazione di una perturbazione che trasporta energia senza trasporto netto di materia.'),
      note('Velocità dell’onda', 'Prodotto tra lunghezza d’onda e frequenza.', 'v = λf'),
      note('Frequenza', 'Numero di oscillazioni al secondo; si misura in hertz.', '1 Hz = 1 s⁻¹'),
      note('Suono', 'Onda meccanica: necessita di un mezzo materiale e non si propaga nel vuoto.'),
      note('Riflessione', 'L’angolo di riflessione è uguale all’angolo di incidenza.'),
      note('Rifrazione', 'Cambiamento di direzione e velocità quando l’onda passa tra mezzi diversi.', 'n₁ sinθ₁ = n₂ sinθ₂')
    ]
  },
  {
    id: 'elettricita',
    title: 'Elettricità e circuiti',
    summary: 'Carica, tensione, corrente, resistenza e potenza.',
    items: [
      note('Corrente', 'Quantità di carica che attraversa una sezione nell’unità di tempo.', 'I = ΔQ/Δt'),
      note('Differenza di potenziale', 'Lavoro per unità di carica necessario a spostare una carica tra due punti.', 'V = L/Q'),
      note('Legge di Ohm', 'Per un conduttore ohmico tensione, corrente e resistenza sono legate.', 'V = RI'),
      note('Potenza elettrica', 'Energia elettrica trasferita nell’unità di tempo.', 'P = VI = RI² = V²/R'),
      note('Resistenze in serie', 'Sono attraversate dalla stessa corrente e le resistenze si sommano.', 'Rₑq = R₁ + R₂ + …'),
      note('Resistenze in parallelo', 'Hanno la stessa tensione e si sommano i reciproci.', '1/Rₑq = 1/R₁ + 1/R₂ + …'),
      note('Effetto Joule', 'L’energia elettrica dissipata si trasforma in calore.', 'Q = RI²t')
    ]
  },
  {
    id: 'definizioni',
    title: 'Definizioni trasversali',
    summary: 'Parole che cambiano il significato di un quesito.',
    items: [
      note('Scalare', 'Grandezza definita da un valore e un’unità, per esempio massa, tempo e temperatura.'),
      note('Vettore', 'Grandezza con modulo, direzione e verso, per esempio spostamento, velocità e forza.'),
      note('Massa e peso', 'La massa misura l’inerzia ed è in kg; il peso è una forza e si misura in N.'),
      note('Precisione', 'Grado di concordanza tra misure ripetute.'),
      note('Accuratezza', 'Vicinanza del risultato al valore di riferimento.'),
      note('Errore assoluto e relativo', 'L’errore assoluto ha l’unità della misura; quello relativo è il rapporto tra errore assoluto e valore misurato.')
    ]
  }
];

const elementRows = [
  '1|H|Idrogeno|1|1','2|He|Elio|18|1',
  '3|Li|Litio|1|2','4|Be|Berillio|2|2','5|B|Boro|13|2','6|C|Carbonio|14|2','7|N|Azoto|15|2','8|O|Ossigeno|16|2','9|F|Fluoro|17|2','10|Ne|Neon|18|2',
  '11|Na|Sodio|1|3','12|Mg|Magnesio|2|3','13|Al|Alluminio|13|3','14|Si|Silicio|14|3','15|P|Fosforo|15|3','16|S|Zolfo|16|3','17|Cl|Cloro|17|3','18|Ar|Argon|18|3',
  '19|K|Potassio|1|4','20|Ca|Calcio|2|4','21|Sc|Scandio|3|4','22|Ti|Titanio|4|4','23|V|Vanadio|5|4','24|Cr|Cromo|6|4','25|Mn|Manganese|7|4','26|Fe|Ferro|8|4','27|Co|Cobalto|9|4','28|Ni|Nichel|10|4','29|Cu|Rame|11|4','30|Zn|Zinco|12|4','31|Ga|Gallio|13|4','32|Ge|Germanio|14|4','33|As|Arsenico|15|4','34|Se|Selenio|16|4','35|Br|Bromo|17|4','36|Kr|Kripton|18|4',
  '37|Rb|Rubidio|1|5','38|Sr|Stronzio|2|5','39|Y|Ittrio|3|5','40|Zr|Zirconio|4|5','41|Nb|Niobio|5|5','42|Mo|Molibdeno|6|5','43|Tc|Tecnezio|7|5','44|Ru|Rutenio|8|5','45|Rh|Rodio|9|5','46|Pd|Palladio|10|5','47|Ag|Argento|11|5','48|Cd|Cadmio|12|5','49|In|Indio|13|5','50|Sn|Stagno|14|5','51|Sb|Antimonio|15|5','52|Te|Tellurio|16|5','53|I|Iodio|17|5','54|Xe|Xeno|18|5',
  '55|Cs|Cesio|1|6','56|Ba|Bario|2|6','57|La|Lantanio||6','58|Ce|Cerio||6','59|Pr|Praseodimio||6','60|Nd|Neodimio||6','61|Pm|Promezio||6','62|Sm|Samario||6','63|Eu|Europio||6','64|Gd|Gadolinio||6','65|Tb|Terbio||6','66|Dy|Disprosio||6','67|Ho|Olmio||6','68|Er|Erbio||6','69|Tm|Tulio||6','70|Yb|Itterbio||6','71|Lu|Lutezio||6','72|Hf|Afnio|4|6','73|Ta|Tantalio|5|6','74|W|Tungsteno|6|6','75|Re|Renio|7|6','76|Os|Osmio|8|6','77|Ir|Iridio|9|6','78|Pt|Platino|10|6','79|Au|Oro|11|6','80|Hg|Mercurio|12|6','81|Tl|Tallio|13|6','82|Pb|Piombo|14|6','83|Bi|Bismuto|15|6','84|Po|Polonio|16|6','85|At|Astato|17|6','86|Rn|Radon|18|6',
  '87|Fr|Francio|1|7','88|Ra|Radio|2|7','89|Ac|Attinio||7','90|Th|Torio||7','91|Pa|Protoattinio||7','92|U|Uranio||7','93|Np|Nettunio||7','94|Pu|Plutonio||7','95|Am|Americio||7','96|Cm|Curio||7','97|Bk|Berkelio||7','98|Cf|Californio||7','99|Es|Einsteinio||7','100|Fm|Fermio||7','101|Md|Mendelevio||7','102|No|Nobelio||7','103|Lr|Laurenzio||7','104|Rf|Rutherfordio|4|7','105|Db|Dubnio|5|7','106|Sg|Seaborgio|6|7','107|Bh|Bohrio|7|7','108|Hs|Hassio|8|7','109|Mt|Meitnerio|9|7','110|Ds|Darmstadtio|10|7','111|Rg|Roentgenio|11|7','112|Cn|Copernicio|12|7','113|Nh|Nihonio|13|7','114|Fl|Flerovio|14|7','115|Mc|Moscovio|15|7','116|Lv|Livermorio|16|7','117|Ts|Tennesso|17|7','118|Og|Oganesson|18|7'
];

const sets = {
  alkali: new Set(['Li','Na','K','Rb','Cs','Fr']),
  alkaline: new Set(['Be','Mg','Ca','Sr','Ba','Ra']),
  metalloid: new Set(['B','Si','Ge','As','Sb','Te']),
  nonmetal: new Set(['H','C','N','O','P','S','Se']),
  halogen: new Set(['F','Cl','Br','I','At','Ts']),
  noble: new Set(['He','Ne','Ar','Kr','Xe','Rn','Og']),
  post: new Set(['Al','Ga','In','Sn','Tl','Pb','Bi','Po','Nh','Fl','Mc','Lv'])
};

const categoryFor = (z, symbol) => {
  if (z >= 57 && z <= 71) return 'lanthanide';
  if (z >= 89 && z <= 103) return 'actinide';
  for (const key of ['alkali','alkaline','metalloid','nonmetal','halogen','noble','post']) if (sets[key].has(symbol)) return key;
  return 'transition';
};

export const periodicElements = elementRows.map((row) => {
  const [atomicNumber, symbol, name, group, period] = row.split('|');
  const z = Number(atomicNumber);
  return {atomicNumber: z, symbol, name, group: group ? Number(group) : null, period: Number(period), category: categoryFor(z, symbol), ...(elementPropertiesByAtomicNumber.get(z) || {})};
});

export const elementCategories = [
  {id:'alkali', label:'Metalli alcalini'},
  {id:'alkaline', label:'Alcalino-terrosi'},
  {id:'transition', label:'Metalli di transizione'},
  {id:'post', label:'Metalli post-transizione'},
  {id:'metalloid', label:'Semimetalli'},
  {id:'nonmetal', label:'Non metalli'},
  {id:'halogen', label:'Alogeni'},
  {id:'noble', label:'Gas nobili'},
  {id:'lanthanide', label:'Lantanidi'},
  {id:'actinide', label:'Attinidi'}
];

export const kingsOfItaly = [
  {name:'Vittorio Emanuele II', years:'1861–1878', party:'Casa Savoia', area:'Primo Re d’Italia', note:'Proclamato Re d’Italia il 17 marzo 1861.'},
  {name:'Umberto I', years:'1878–1900', party:'Casa Savoia', area:'Secondo Re d’Italia', note:'Ucciso a Monza il 29 luglio 1900.'},
  {name:'Vittorio Emanuele III', years:'1900–1946', party:'Casa Savoia', area:'Terzo Re d’Italia', note:'Abdicò il 9 maggio 1946 in favore del figlio Umberto.'},
  {name:'Umberto II', years:'9 maggio–13 giugno 1946', party:'Casa Savoia', area:'Quarto e ultimo Re d’Italia', note:'Conosciuto come “Re di maggio”; lasciò l’Italia dopo il referendum istituzionale.'}
];

export const kingdomPrimeMinisters = [
  {name:'Camillo Benso di Cavour', years:'1861', party:'Destra storica', area:'Liberale moderato · Destra storica', note:'Primo Presidente del Consiglio del Regno d’Italia.'},
  {name:'Bettino Ricasoli', years:'1861–1862; 1866–1867', party:'Destra storica', area:'Liberale moderato · Destra storica'},
  {name:'Urbano Rattazzi', years:'1862; 1867', party:'Sinistra storica', area:'Liberale progressista · Sinistra storica'},
  {name:'Luigi Carlo Farini', years:'1862–1863', party:'Destra storica', area:'Liberale moderato · Destra storica'},
  {name:'Marco Minghetti', years:'1863–1864; 1873–1876', party:'Destra storica', area:'Liberale moderato · Destra storica', note:'Il suo ultimo governo cadde con la “rivoluzione parlamentare” del 1876.'},
  {name:'Alfonso La Marmora', years:'1864–1866', party:'Destra storica', area:'Liberale moderato · Destra storica'},
  {name:'Luigi Federico Menabrea', years:'1867–1869', party:'Destra storica', area:'Liberale conservatore · Destra storica'},
  {name:'Giovanni Lanza', years:'1869–1873', party:'Destra storica', area:'Liberale moderato · Destra storica'},
  {name:'Agostino Depretis', years:'1876–1878; 1878–1879; 1881–1887', party:'Sinistra storica', area:'Sinistra storica · trasformismo'},
  {name:'Benedetto Cairoli', years:'1878; 1879–1881', party:'Sinistra storica', area:'Sinistra storica'},
  {name:'Francesco Crispi', years:'1887–1891; 1893–1896', party:'Sinistra storica', area:'Sinistra storica · liberal-nazionale'},
  {name:'Antonio Starabba di Rudinì', years:'1891–1892; 1896–1898', party:'Destra storica', area:'Liberale conservatore'},
  {name:'Giovanni Giolitti', years:'1892–1893; 1903–1905; 1906–1909; 1911–1914; 1920–1921', party:'Area liberale', area:'Liberale · centro giolittiano'},
  {name:'Luigi Pelloux', years:'1898–1900', party:'Area liberale', area:'Liberale conservatore · militare'},
  {name:'Giuseppe Saracco', years:'1900–1901', party:'Area liberale', area:'Liberale'},
  {name:'Giuseppe Zanardelli', years:'1901–1903', party:'Area liberale', area:'Liberale progressista'},
  {name:'Tommaso Tittoni', years:'1905', party:'Area liberale', area:'Liberale conservatore'},
  {name:'Alessandro Fortis', years:'1905–1906', party:'Area liberale', area:'Liberale'},
  {name:'Sidney Sonnino', years:'1906; 1909–1910', party:'Area liberale', area:'Liberale conservatore'},
  {name:'Luigi Luzzatti', years:'1910–1911', party:'Area liberale', area:'Liberale'},
  {name:'Antonio Salandra', years:'1914–1916', party:'Area liberale', area:'Liberale conservatore'},
  {name:'Paolo Boselli', years:'1916–1917', party:'Area liberale', area:'Coalizione di unità nazionale'},
  {name:'Vittorio Emanuele Orlando', years:'1917–1919', party:'Area liberale', area:'Liberale · unità nazionale'},
  {name:'Francesco Saverio Nitti', years:'1919–1920', party:'Partito Radicale Italiano / area liberale', area:'Liberale-radicale'},
  {name:'Ivanoe Bonomi', years:'1921–1922', party:'Partito Socialista Riformista Italiano', area:'Socialista riformista'},
  {name:'Luigi Facta', years:'1922', party:'Area liberale', area:'Liberale'},
  {name:'Benito Mussolini', years:'1922–1943', party:'Partito Nazionale Fascista', area:'Fascismo · dittatura dal 1925', note:'Nominato dopo la marcia su Roma; il regime divenne dittatoriale con le leggi fascistissime.'}
];

export const transitionPrimeMinisters = [
  {name:'Pietro Badoglio', years:'1943–1944', party:'Militare / indipendente', area:'Governo monarchico di transizione'},
  {name:'Ivanoe Bonomi', years:'1944–1945', party:'Democrazia del Lavoro', area:'Coalizione del Comitato di Liberazione Nazionale'},
  {name:'Ferruccio Parri', years:'1945', party:'Partito d’Azione', area:'Coalizione del Comitato di Liberazione Nazionale'},
  {name:'Alcide De Gasperi', years:'1945–1946', party:'Democrazia Cristiana', area:'Unità nazionale · transizione alla Repubblica'}
];

export const presidents = [
  {name:'Enrico De Nicola', years:'1946–1948', note:'Capo provvisorio dello Stato dal 1946; Presidente della Repubblica dal 1° gennaio 1948.'},
  {name:'Luigi Einaudi', years:'1948–1955'},
  {name:'Giovanni Gronchi', years:'1955–1962'},
  {name:'Antonio Segni', years:'1962–1964'},
  {name:'Giuseppe Saragat', years:'1964–1971'},
  {name:'Giovanni Leone', years:'1971–1978'},
  {name:'Sandro Pertini', years:'1978–1985'},
  {name:'Francesco Cossiga', years:'1985–1992'},
  {name:'Oscar Luigi Scalfaro', years:'1992–1999'},
  {name:'Carlo Azeglio Ciampi', years:'1999–2006'},
  {name:'Giorgio Napolitano', years:'2006–2015', note:'Primo Presidente rieletto per un secondo mandato.'},
  {name:'Sergio Mattarella', years:'2015–oggi', note:'Rieletto nel 2022.', current:true}
];

export const popes = [
  {name:'Pio IX', birthName:'Giovanni Maria Mastai Ferretti', years:'1846–1878', note:'Papa al momento dell’Unità d’Italia del 1861.'},
  {name:'Leone XIII', birthName:'Vincenzo Gioacchino Pecci', years:'1878–1903'},
  {name:'Pio X', birthName:'Giuseppe Melchiorre Sarto', years:'1903–1914'},
  {name:'Benedetto XV', birthName:'Giacomo della Chiesa', years:'1914–1922'},
  {name:'Pio XI', birthName:'Achille Ratti', years:'1922–1939'},
  {name:'Pio XII', birthName:'Eugenio Pacelli', years:'1939–1958'},
  {name:'Giovanni XXIII', birthName:'Angelo Giuseppe Roncalli', years:'1958–1963'},
  {name:'Paolo VI', birthName:'Giovanni Battista Montini', years:'1963–1978'},
  {name:'Giovanni Paolo I', birthName:'Albino Luciani', years:'1978', note:'Pontificato di 33 giorni.'},
  {name:'Giovanni Paolo II', birthName:'Karol Wojtyła', years:'1978–2005'},
  {name:'Benedetto XVI', birthName:'Joseph Ratzinger', years:'2005–2013'},
  {name:'Francesco', birthName:'Jorge Mario Bergoglio', years:'2013–2025'},
  {name:'Leone XIV', birthName:'Robert Francis Prevost', years:'2025–oggi', current:true}
];

export const primeMinisters = [
  {name:'Alcide De Gasperi', years:'1946–1953', party:'Democrazia Cristiana', area:'Centro · cattolico-democratico', note:'Era già Presidente del Consiglio dal dicembre 1945; guida i primi governi della Repubblica.'},
  {name:'Giuseppe Pella', years:'1953–1954', party:'Democrazia Cristiana', area:'Centro'},
  {name:'Amintore Fanfani', years:'1954; 1958–1959; 1960–1963; 1982–1983; 1987', party:'Democrazia Cristiana', area:'Centro / centro-sinistra'},
  {name:'Mario Scelba', years:'1954–1955', party:'Democrazia Cristiana', area:'Centro'},
  {name:'Antonio Segni', years:'1955–1957; 1959–1960', party:'Democrazia Cristiana', area:'Centro'},
  {name:'Adone Zoli', years:'1957–1958', party:'Democrazia Cristiana', area:'Centro'},
  {name:'Fernando Tambroni', years:'1960', party:'Democrazia Cristiana', area:'Centro · governo con appoggio esterno del MSI'},
  {name:'Giovanni Leone', years:'1963; 1968', party:'Democrazia Cristiana', area:'Centro'},
  {name:'Aldo Moro', years:'1963–1968; 1974–1976', party:'Democrazia Cristiana', area:'Centro-sinistra'},
  {name:'Mariano Rumor', years:'1968–1970; 1973–1974', party:'Democrazia Cristiana', area:'Centro / centro-sinistra'},
  {name:'Emilio Colombo', years:'1970–1972', party:'Democrazia Cristiana', area:'Centro-sinistra'},
  {name:'Giulio Andreotti', years:'1972–1973; 1976–1979; 1989–1992', party:'Democrazia Cristiana', area:'Centro · coalizioni variabili'},
  {name:'Francesco Cossiga', years:'1979–1980', party:'Democrazia Cristiana', area:'Centro'},
  {name:'Arnaldo Forlani', years:'1980–1981', party:'Democrazia Cristiana', area:'Centro'},
  {name:'Giovanni Spadolini', years:'1981–1982', party:'Partito Repubblicano Italiano', area:'Centro / centro-sinistra'},
  {name:'Bettino Craxi', years:'1983–1987', party:'Partito Socialista Italiano', area:'Centro-sinistra'},
  {name:'Giovanni Goria', years:'1987–1988', party:'Democrazia Cristiana', area:'Centro'},
  {name:'Ciriaco De Mita', years:'1988–1989', party:'Democrazia Cristiana', area:'Centro'},
  {name:'Giuliano Amato', years:'1992–1993; 2000–2001', party:'Partito Socialista Italiano / indipendente', area:'Centro-sinistra'},
  {name:'Carlo Azeglio Ciampi', years:'1993–1994', party:'Indipendente', area:'Governo tecnico / di transizione'},
  {name:'Silvio Berlusconi', years:'1994–1995; 2001–2006; 2008–2011', party:'Forza Italia / Popolo della Libertà', area:'Centro-destra'},
  {name:'Lamberto Dini', years:'1995–1996', party:'Indipendente', area:'Governo tecnico · poi sostenuto dal centro-sinistra'},
  {name:'Romano Prodi', years:'1996–1998; 2006–2008', party:'Indipendente / L’Ulivo', area:'Centro-sinistra'},
  {name:'Massimo D’Alema', years:'1998–2000', party:'Partito Democratico della Sinistra / Democratici di Sinistra', area:'Centro-sinistra'},
  {name:'Mario Monti', years:'2011–2013', party:'Indipendente', area:'Governo tecnico / centro'},
  {name:'Enrico Letta', years:'2013–2014', party:'Partito Democratico', area:'Centro-sinistra · larghe intese'},
  {name:'Matteo Renzi', years:'2014–2016', party:'Partito Democratico', area:'Centro-sinistra'},
  {name:'Paolo Gentiloni', years:'2016–2018', party:'Partito Democratico', area:'Centro-sinistra'},
  {name:'Giuseppe Conte', years:'2018–2021', party:'Indipendente', area:'Coalizioni differenti: M5S–Lega; poi M5S–PD–LeU'},
  {name:'Mario Draghi', years:'2021–2022', party:'Indipendente', area:'Unità nazionale / governo tecnico'},
  {name:'Giorgia Meloni', years:'2022–oggi', party:'Fratelli d’Italia', area:'Centro-destra · destra conservatrice', current:true}
];

export const memoryTricks = [
  {
    id:'presidenti',
    title:'Presidenti della Repubblica',
    initials:'D E G S S · L P C · S C · N M',
    phrase:'Diego E Giulia Studiano Sempre; Luca Prepara Caffè, Sara Compra Noci Mature.',
    explanation:'Le iniziali seguono De Nicola, Einaudi, Gronchi, Segni, Saragat, Leone, Pertini, Cossiga, Scalfaro, Ciampi, Napolitano, Mattarella.'
  },
  {
    id:'papi',
    title:'Papi dall’Unità d’Italia',
    initials:'P L P B P P · G P · G G · B F L',
    phrase:'Pietro Legge Pagine; Bruno Prepara Piani, Giulia Porta Grandi Guide, Benedetta Firma Libri.',
    explanation:'Le iniziali seguono i nomi pontificali. I due “G” consecutivi ricordano Giovanni Paolo I e Giovanni Paolo II.'
  }
];

export const noteSources = [
  {label:'BIPM · Sistema Internazionale e unità di base', url:'https://www.bipm.org/en/measurement-units/si-base-units'},
  {label:'IUPAC · Tavola periodica degli elementi', url:'https://iupac.org/what-we-do/periodic-table-of-elements/'},
  {label:'PubChem · Proprietà degli elementi', url:'https://pubchem.ncbi.nlm.nih.gov/periodic-table/'},
  {label:'Microsoft Support · Attività di base in Word ed Excel', url:'https://support.microsoft.com/en-us/office/excel-video-training-9bc05390-e94c-46af-a5b3-d7c22f6990bb'},
  {label:'MDN · Come funzionano Web, URL e HTTP', url:'https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works'},
  {label:'CISA · Sicurezza online essenziale', url:'https://www.cisa.gov/secure-our-world'},
  {label:'British Council · Grammatica inglese', url:'https://learnenglish.britishcouncil.org/free-resources/grammar'},
  {label:'Quirinale · Presidenti della Repubblica', url:'https://archivio.quirinale.it/aspr/presidente/'},
  {label:'Quirinale · I Re d’Italia', url:'https://palazzo.quirinale.it/luoghi/pdf/it/sala-regno-italia.pdf'},
  {label:'Camera dei deputati · Presidenti del Consiglio dal 1861 al 1943', url:'https://leg15.camera.it/organiparlamentarism/241/4405/5342/documentotesto.asp'},
  {label:'Senato · Governi della transizione e della Repubblica', url:'https://www.senato.it/legislature/repubblica/governi-della-repubblica'},
  {label:'Governo italiano · Governi dal 1943 a oggi', url:'https://presidenza.governo.it/Cerca/index.asp'},
  {label:'Treccani · Destra e Sinistra storica', url:'https://www.treccani.it/enciclopedia/sinistra-e-centro-destra_%28Enciclopedia-dei-ragazzi%29/'},
  {label:'Santa Sede · Elenco dei Pontefici', url:'https://www.vatican.va/content/vatican/it/holy-father.html'}
];

export const notesSearchIndex = [
  ...chemistryNotes.flatMap(section => section.items.map(item => ({section:'chimica', sectionTitle:'Chimica', anchor:section.id, title:item.term, text:`${item.definition} ${item.formula} ${item.tip}`}))),
  ...physicsNotes.flatMap(section => section.items.map(item => ({section:'fisica', sectionTitle:'Fisica', anchor:section.id, title:item.term, text:`${item.definition} ${item.formula} ${item.tip}`}))),
  ...computerScienceNotes.flatMap(section => section.items.map(item => ({section:'informatica', sectionTitle:'Informatica', anchor:section.id, title:item.term, text:`${item.definition} ${item.formula} ${item.tip}`}))),
  ...logicNotes.flatMap(section => section.items.map(item => ({section:'logica', sectionTitle:'Logica', anchor:section.id, title:item.term, text:`${item.definition} ${item.formula} ${item.tip}`}))),
  ...englishNotes.flatMap(section => section.items.map(item => ({section:'inglese', sectionTitle:'Inglese', anchor:section.id, title:item.term, text:`${item.definition} ${item.formula} ${item.tip}`}))),
  ...periodicElements.map(item => ({section:'tavola-periodica', sectionTitle:'Tavola periodica', anchor:`element-${item.atomicNumber}`, title:`${item.symbol} · ${item.name}`, text:`numero atomico ${item.atomicNumber} massa atomica ${item.atomicMass} gruppo ${item.group || ''} periodo ${item.period} ${item.standardState} ${item.artificial ? 'sintetico artificiale' : 'naturale'} ossidazione ${item.oxidationStates}`})),
  ...kingsOfItaly.map(item => ({section:'storia', sectionTitle:'Storia · Re d’Italia', anchor:'re-italia', title:item.name, text:`${item.years} ${item.party} ${item.area} ${item.note || ''}`})),
  ...kingdomPrimeMinisters.map(item => ({section:'storia', sectionTitle:'Storia · Presidenti del Consiglio del Regno', anchor:'presidenti-consiglio-regno', title:item.name, text:`${item.years} ${item.party} ${item.area} ${item.note || ''}`})),
  ...transitionPrimeMinisters.map(item => ({section:'storia', sectionTitle:'Storia · Transizione costituzionale', anchor:'presidenti-consiglio-transizione', title:item.name, text:`${item.years} ${item.party} ${item.area} ${item.note || ''}`})),
  ...presidents.map(item => ({section:'storia', sectionTitle:'Storia · Presidenti della Repubblica', anchor:'presidenti-repubblica', title:item.name, text:`${item.years} ${item.note || ''}`})),
  ...popes.map(item => ({section:'storia', sectionTitle:'Storia · Papi', anchor:'papi', title:item.name, text:`${item.birthName} ${item.years} ${item.note || ''}`})),
  ...primeMinisters.map(item => ({section:'storia', sectionTitle:'Storia · Presidenti del Consiglio', anchor:'presidenti-consiglio', title:item.name, text:`${item.years} ${item.party} ${item.area} ${item.note || ''}`}))
];
