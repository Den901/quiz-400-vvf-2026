import {readFileSync,writeFileSync} from 'node:fs';

const datasetUrl=new URL('../quiz-dataset.json',import.meta.url);
const questions=JSON.parse(readFileSync(datasetUrl,'utf8'));
const scienceCategories=new Set(['fisica','chimica']);

const reviewedExplanations={
 '25290857':'Nell’ibridazione sp2 un orbitale s e due orbitali p formano tre orbitali ibridi equivalenti, disposti sullo stesso piano con angoli di circa 120 gradi. Resta un orbitale p non ibridato, perpendicolare al piano, che può formare un legame pi greco.',
 '25290860':'Nell’acqua pura, a 25 °C, le concentrazioni degli ioni H+ e OH- sono uguali. Poiché il prodotto ionico dell’acqua vale 10^-14, ciascuna concentrazione è pari a 10^-7 mol/L.',
 '25290942':'L’ammoniaca NH3 si comporta come una base perché l’atomo di azoto possiede una coppia elettronica libera e può accettare un protone H+, formando lo ione ammonio NH4+.',
 '25290980':'L’acido solforoso ha formula H2SO3. Sottraendo formalmente una molecola di acqua si ottiene SO2, cioè l’anidride solforosa, che è quindi l’anidride corrispondente.',
 '25291035':'FeSO3 è formato dallo ione ferro(II), Fe2+, e dallo ione solfito, SO3^2-. Il composto prende quindi il nome di solfito ferroso, o solfito di ferro(II).',
 '25291213':'Aggiungendo un acido all’acqua aumenta la concentrazione degli ioni H+ (più precisamente H3O+) e il pH diminuisce. Contemporaneamente la concentrazione degli ioni OH- si riduce.',
 '25291362':'In condizioni standard una mole di gas occupa circa 22,4 L. Quindi 11,2 L di CH4 corrispondono a 0,5 mol; la massa molare del metano è 16 g/mol e la massa cercata è 0,5 x 16 = 8 g.',
 '25291399':'Ogni mole di Ca(OH)2 può fornire due moli di ioni OH-. Nelle reazioni acido-base la normalità è quindi il doppio della molarità: 0,5 M x 2 = 1 N.',
 '25291465':'Nell’acqua pura, a 25 °C, gli ioni H+ e OH- hanno la stessa concentrazione. Dal prodotto ionico Kw = 10^-14 segue che la concentrazione degli ioni OH- è 10^-7 mol/L.',
 '25291558':'Secondo Brønsted-Lowry un acido è una specie chimica capace di cedere un protone H+. Una base, al contrario, è capace di accettarlo.',
 '25291799':'L’acido fosforico H3PO4 è triprotico: può cedere tre protoni H+. Perciò, nelle reazioni acido-base complete, una mole contiene tre equivalenti.',
 '25291846':'L’anidride carbonica CO2 disciolta in acqua reagisce formando acido carbonico H2CO3. Per questo una soluzione acquosa contenente CO2 assume carattere acido.',
 '25291854':'KHS è costituito dallo ione potassio K+ e dallo ione idrogenosolfuro HS-. Il suo nome è quindi idrogenosolfuro di potassio.',
 '25291932':'L’acido solforico H2SO4 è diprotico e può fornire due equivalenti di H+ per mole. Nelle reazioni acido-base la normalità di una soluzione 1 M è pertanto 2 N.',
 '25291951':'In una soluzione neutra a 25 °C, pH = 7 significa che le concentrazioni di H+ e OH- sono entrambe pari a 10^-7 mol/L.',
 '25291954':'Se la concentrazione di OH- è 10^-12 mol/L, il pOH è 12. A 25 °C vale pH + pOH = 14, quindi il pH è 2 e la soluzione è acida.',
 '25291976':'Un carbonio ibridato sp2 forma tre orbitali ibridi disposti con geometria trigonale planare e angoli di circa 120 gradi. La struttura attorno a quel carbonio è quindi planare.',
 '25291982':'È una neutralizzazione tra acido solforico e idrossido di sodio: H2SO4 + 2 NaOH -> Na2SO4 + 2 H2O. I prodotti sono solfato di sodio e acqua.',
 '25292032':'Il composto contiene lo ione calcio Ca2+ e due ioni diidrogenofosfato H2PO4-. Le cariche si bilanciano nella formula Ca(H2PO4)2, chiamata diidrogenofosfato di calcio.',
 '25292119':'A temperatura e pressione costanti una trasformazione è spontanea quando la variazione di energia libera di Gibbs è negativa, cioè quando delta G è minore di zero.'
};

function removeDamagedFragments(explanation){
 return explanation
  .split(/\n{2,}/)
  .map(paragraph=>paragraph.split(/(?<=[.!])\s+|\n+/).filter(fragment=>fragment.trim()&&!fragment.includes('?')&&!fragment.includes('\\')).join(' '))
  .filter(Boolean)
  .join('\n\n')
  .replace(/[ \t]+([,.;:])/g,'$1')
  .replace(/:([A-ZÀ-Ü])/g,': $1')
  .replace(/[ \t]{2,}/g,' ')
  .trim();
}

function removeDanglingCalculationPrompts(explanation){
 return explanation.split(/\n{2,}/).map(paragraph=>paragraph
  .replace(/:([A-ZÀ-Ü])/g,': $1')
  .replace(/,([^\s])/g,', $1')
  .split(/(?<=[.!])\s+/)
  .filter(fragment=>{
   const text=fragment.trim();
   return text!=='-'&&!(text.length<190&&text.endsWith(':')&&/(formula|calcol|sostitu|valori|seguente|risultato|energie)/i.test(text));
  }).join(' ')
 ).filter(Boolean).join('\n\n').trim();
}

let repaired=0;
for(const question of questions){
 if(!scienceCategories.has(question.category))continue;
 const visiblyDamaged=question.explanation?.includes('?')||question.explanation?.includes('\\');
 const reviewed=reviewedExplanations[String(question.id)];
 const cleaned=removeDanglingCalculationPrompts(reviewed||(visiblyDamaged?removeDamagedFragments(question.explanation):question.explanation));
 if(!visiblyDamaged&&!reviewed&&cleaned.length<100)continue;
 if(cleaned.length<100||cleaned.includes('?')||cleaned.includes('\\'))throw new Error(`Spiegazione ${question.id} non riparata in modo sicuro`);
 if(cleaned===question.explanation)continue;
 question.explanation=cleaned;
 repaired++;
}

writeFileSync(datasetUrl,`${JSON.stringify(questions,null,2)}\n`,'utf8');
console.log(`Riparate ${repaired} spiegazioni di Fisica e Chimica.`);
