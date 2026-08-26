import {
  chemistryNotes,
  computerScienceNotes,
  elementCategories,
  englishNotes,
  kingdomPrimeMinisters,
  kingsOfItaly,
  logicNotes,
  memoryTricks,
  noteSources,
  notesSearchIndex,
  periodicElements,
  physicsNotes,
  popes,
  presidents,
  primeMinisters,
  transitionPrimeMinisters
} from './study-notes.js?v=53';

const normalizeSearch = value => String(value || '')
  .normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '')
  .toLocaleLowerCase('it')
  .trim();

export function renderNotes(app, section = '', helpers = {}) {
  app.classList.toggle('notes-wide-page', section === 'tavola-periodica');
  const esc = helpers.esc || (value => String(value ?? ''));
  const sectionLinks = () => `<nav class="notes-section-nav" aria-label="Sezioni degli appunti">
    <a href="#notes/chimica">Chimica</a>
    <a href="#notes/tavola-periodica">Tavola periodica</a>
    <a href="#notes/fisica">Fisica</a>
    <a href="#notes/informatica">Informatica</a>
    <a href="#notes/logica">Logica</a>
    <a href="#notes/inglese">Inglese</a>
    <a href="#notes/storia">Storia</a>
  </nav>`;

  const sourcesMarkup = () => `<footer class="card notes-sources">
    <h2>Fonti di riferimento</h2>
    <p>Contenuti sintetizzati per lo studio e verificati il 25 agosto 2026. Per date, nomenclatura e unità fanno fede le fonti istituzionali.</p>
    <ul>${noteSources.map(source => `<li><a href="${esc(source.url)}" target="_blank" rel="noopener">${esc(source.label)}</a></li>`).join('')}</ul>
  </footer>`;

  const formatNumber = value => Number(value).toLocaleString('it-IT', {maximumFractionDigits: 3});
  const formatTemperature = kelvin => Number.isFinite(kelvin)
    ? `${formatNumber(kelvin)} K · ${formatNumber(kelvin - 273.15)} °C`
    : 'Non determinata';

  const focusAnchor = anchor => {
    const target = document.getElementById(anchor);
    if (!target) return;
    const details = target.closest('details');
    if (details) details.open = true;
    target.scrollIntoView({behavior: 'smooth', block: 'center'});
    target.classList.add('notes-focus');
    setTimeout(() => target.classList.remove('notes-focus'), 1700);
  };

  const homeView = () => {
    app.innerHTML = `<section class="notes-hero">
      <div><div class="eyebrow">Ripasso rapido</div><h1>Appunti</h1><p>Concetti essenziali collegati ai quiz, formule, grammatica, strategie logiche e cronologie storiche in schede facili da consultare.</p></div>
      <span class="notes-hero-mark" aria-hidden="true">✎</span>
    </section>
    <section class="card notes-search-card">
      <label for="notesSearch">Cerca negli appunti</label>
      <div class="notes-search-input"><span aria-hidden="true">⌕</span><input id="notesSearch" data-global-notes-search type="search" placeholder="Es. phishing, present perfect, sillogismo, Giolitti…" autocomplete="off"></div>
      <div class="notes-search-results" data-global-notes-results aria-live="polite"></div>
    </section>
    <div class="notes-hub-grid">
      <a class="card notes-hub-card chemistry" href="#notes/chimica"><span class="notes-hub-icon">⚗</span><div><h2>Chimica</h2><p>Atomo, legami, mole, reazioni, acidi, basi e gas.</p><small>${chemistryNotes.length} capitoli</small></div></a>
      <a class="card notes-hub-card periodic" href="#notes/tavola-periodica"><span class="notes-hub-icon">118</span><div><h2>Tavola periodica</h2><p>Tutti gli elementi, gruppi, periodi e famiglie.</p><small>118 elementi</small></div></a>
      <a class="card notes-hub-card physics" href="#notes/fisica"><span class="notes-hub-icon">F</span><div><h2>Fisica</h2><p>Unità di misura, leggi, formule e definizioni.</p><small>${physicsNotes.length} capitoli</small></div></a>
      <a class="card notes-hub-card computer" href="#notes/informatica"><span class="notes-hub-icon">⌨</span><div><h2>Informatica</h2><p>Hardware, Office, reti, Web, sicurezza e dati.</p><small>10 capitoli · 2.119 quiz</small></div></a>
      <a class="card notes-hub-card logic" href="#notes/logica"><span class="notes-hub-icon">∴</span><div><h2>Logica</h2><p>Deduzioni, serie, calcolo, figure, insiemi e brani.</p><small>10 capitoli · 5.853 quiz</small></div></a>
      <a class="card notes-hub-card english" href="#notes/inglese"><span class="notes-hub-icon">EN</span><div><h2>Inglese</h2><p>Tempi, pronomi, preposizioni, lessico e frase.</p><small>10 capitoli · 1.551 quiz</small></div></a>
      <a class="card notes-hub-card history" href="#notes/storia"><span class="notes-hub-icon">⌛</span><div><h2>Storia</h2><p>Re, Presidenti, Papi e governi dal 1861.</p><small>Cronologie e aree politiche</small></div></a>
    </div>
    <aside class="notes-study-tip"><b>Metodo consigliato</b><span>Leggi una scheda, copri la definizione e prova a ripeterla. Subito dopo allenati nei quiz della materia corrispondente.</span></aside>`;

    const input = app.querySelector('[data-global-notes-search]');
    const results = app.querySelector('[data-global-notes-results]');
    const updateResults = () => {
      const query = normalizeSearch(input.value);
      if (query.length < 2) {
        results.innerHTML = '<p class="meta">Scrivi almeno due lettere: puoi cercare una formula, un elemento o un personaggio.</p>';
        return;
      }
      const matches = notesSearchIndex
        .filter(item => normalizeSearch(`${item.title} ${item.text} ${item.sectionTitle}`).includes(query))
        .slice(0, 30);
      results.innerHTML = matches.length
        ? matches.map(item => `<button class="notes-search-result" type="button" data-note-section="${esc(item.section)}" data-note-anchor="${esc(item.anchor)}"><span>${esc(item.sectionTitle)}</span><b>${esc(item.title)}</b><small>${esc(item.text)}</small></button>`).join('')
        : '<p class="notes-empty">Nessun appunto corrisponde alla ricerca.</p>';
      results.querySelectorAll('[data-note-section]').forEach(button => {
        button.onclick = () => {
          const targetHash = `#notes/${button.dataset.noteSection}`;
          const anchor = button.dataset.noteAnchor;
          if (location.hash === targetHash) renderNotes(app, button.dataset.noteSection, helpers);
          else location.hash = targetHash;
          setTimeout(() => focusAnchor(anchor), 120);
        };
      });
    };
    input.addEventListener('input', updateResults);
    updateResults();
  };

  const noteItemsMarkup = items => `<div class="note-fact-grid">${items.map(item => `<article class="note-fact">
    <div><h3>${esc(item.term)}</h3><p>${esc(item.definition)}</p></div>
    ${item.formula ? `<code>${esc(item.formula)}</code>` : ''}
    ${item.tip ? `<span class="note-tip">${esc(item.tip)}</span>` : ''}
  </article>`).join('')}</div>`;

  const subjectView = kind => {
    const subjectDefinitions = {
      chimica:{title:'Chimica', sections:chemistryNotes, subtitle:'Concetti base, relazioni e formule da riconoscere nei quiz.'},
      fisica:{title:'Fisica', sections:physicsNotes, subtitle:'Unità di misura, leggi fondamentali, formule e definizioni.'},
      informatica:{title:'Informatica', sections:computerScienceNotes, subtitle:'Schede costruite sui dieci sottoargomenti e sui 2.119 quesiti di Informatica presenti nel portale.'},
      logica:{title:'Logica', sections:logicNotes, subtitle:'Metodi e strategie ricavati dalle dieci tipologie e dai 5.853 quesiti di Logica presenti nel portale.'},
      inglese:{title:'Inglese', sections:englishNotes, subtitle:'Regole, esempi e trappole ricorrenti nei 1.551 quesiti di Inglese presenti nel portale.'}
    };
    const definition = subjectDefinitions[kind] || subjectDefinitions.chimica;
    const {sections, title, subtitle} = definition;
    const coveredQuestions = sections.reduce((sum, item) => sum + (item.quizCount || 0), 0);
    app.innerHTML = `<a class="back-link" href="#notes">← Tutti gli appunti</a>${sectionLinks()}
      <div class="section-head notes-page-head"><div><div class="eyebrow">Appunti · ${sections.length} capitoli${coveredQuestions ? ` · ${coveredQuestions.toLocaleString('it-IT')} quesiti` : ''}</div><h1>${title}</h1></div><a class="button primary compact" href="#category/${kind}">Vai ai quiz</a></div>
      <p class="notes-lead">${subtitle}</p>
      <div class="card notes-inline-search"><label>Cerca in ${title}<input data-notes-filter type="search" placeholder="Cerca definizione o formula…" autocomplete="off"></label></div>
      <div class="note-accordion">${sections.map((item, index) => `<details class="card note-chapter" id="${esc(item.id)}" data-search="${esc(`${item.title} ${item.summary} ${item.items.map(fact => `${fact.term} ${fact.definition} ${fact.formula} ${fact.tip}`).join(' ')}`)}" ${index === 0 ? 'open' : ''}>
        <summary><span><small>Capitolo ${index + 1}${item.quizCount ? ` · ${item.quizCount.toLocaleString('it-IT')} quesiti collegati` : ''}</small><b>${esc(item.title)}</b><em>${esc(item.summary)}</em></span><i aria-hidden="true">⌄</i></summary>
        ${noteItemsMarkup(item.items)}
      </details>`).join('')}</div>
      <p class="notes-empty hidden" data-notes-empty>Nessun capitolo corrisponde alla ricerca.</p>${sourcesMarkup()}`;

    const input = app.querySelector('[data-notes-filter]');
    const empty = app.querySelector('[data-notes-empty]');
    input.addEventListener('input', () => {
      const query = normalizeSearch(input.value);
      let visible = 0;
      app.querySelectorAll('.note-chapter').forEach(item => {
        const match = !query || normalizeSearch(item.dataset.search).includes(query);
        item.classList.toggle('hidden', !match);
        if (match) {
          visible += 1;
          if (query) item.open = true;
        }
      });
      empty.classList.toggle('hidden', visible > 0);
    });
  };

  const categoryLabel = id => elementCategories.find(category => category.id === id)?.label || id;
  const cellMarkup = (element, row, column) => `<button id="element-${element.atomicNumber}" class="periodic-element ${esc(element.category)}" style="grid-row:${row};grid-column:${column}" type="button" data-element="${element.atomicNumber}" data-category="${esc(element.category)}" data-search="${esc(`${element.atomicNumber} ${element.symbol} ${element.name} ${categoryLabel(element.category)} ${element.atomicMass} ${element.standardState} ${element.oxidationStates} ${element.artificial ? 'sintetico artificiale' : 'naturale'}`)}" aria-label="${esc(`${element.name}, simbolo ${element.symbol}, numero atomico ${element.atomicNumber}`)}">
    <small>${element.atomicNumber}</small><em>${esc(element.atomicMass)}</em><b>${esc(element.symbol)}</b><span>${esc(element.name)}</span>
  </button>`;

  const tableMarkup = () => {
    const main = periodicElements.filter(item => item.group !== null).map(item => cellMarkup(item, item.period + 1, item.group)).join('');
    const lanthanides = periodicElements.filter(item => item.category === 'lanthanide').map((item, index) => cellMarkup(item, 1, index + 1)).join('');
    const actinides = periodicElements.filter(item => item.category === 'actinide').map((item, index) => cellMarkup(item, 2, index + 1)).join('');
    return `<div class="periodic-scroll" tabindex="0" aria-label="Tavola periodica scorrevole"><div class="periodic-grid">
      ${Array.from({length: 18}, (_, index) => `<span class="periodic-group" style="grid-row:1;grid-column:${index + 1}">${index + 1}</span>`).join('')}
      ${main}<span class="periodic-placeholder lanthanide" style="grid-row:7;grid-column:3">57–71<br>Lantanidi</span><span class="periodic-placeholder actinide" style="grid-row:8;grid-column:3">89–103<br>Attinidi</span>
    </div></div>
    <div class="periodic-scroll f-block-scroll" tabindex="0" aria-label="Lantanidi e attinidi scorrevoli"><div class="periodic-f-block">${lanthanides}${actinides}</div></div>`;
  };

  const periodicView = () => {
    app.innerHTML = `<a class="back-link" href="#notes">← Tutti gli appunti</a>${sectionLinks()}
      <div class="section-head notes-page-head"><div><div class="eyebrow">Chimica · 118 elementi</div><h1>Tavola periodica</h1></div><a class="button primary compact" href="#category/chimica">Vai ai quiz</a></div>
      <p class="notes-lead">Cerca per nome, simbolo o numero atomico. Su telefono e tablet scorri la tavola orizzontalmente e tocca un elemento per i dettagli.</p>
      <section class="card periodic-controls"><label>Cerca elemento<input data-element-search type="search" placeholder="Es. Fe, ferro o 26" autocomplete="off"></label><label>Famiglia<select data-element-category><option value="">Tutte le famiglie</option>${elementCategories.map(item => `<option value="${esc(item.id)}">${esc(item.label)}</option>`).join('')}</select></label></section>
      <div class="periodic-legend">${elementCategories.map(item => `<span class="${esc(item.id)}"><i></i>${esc(item.label)}</span>`).join('')}</div>
      <section class="card element-detail" data-element-detail aria-live="polite"></section>
      ${tableMarkup()}<p class="notes-empty hidden" data-periodic-empty>Nessun elemento corrisponde ai filtri.</p>
      <aside class="notes-study-tip"><b>Trucco per gli andamenti</b><span>Raggio atomico: cresce verso il basso e a sinistra. Elettronegatività ed energia di ionizzazione: crescono verso l’alto e a destra.</span></aside>${sourcesMarkup()}`;

    const search = app.querySelector('[data-element-search]');
    const select = app.querySelector('[data-element-category]');
    const elements = [...app.querySelectorAll('.periodic-element')];
    const empty = app.querySelector('[data-periodic-empty]');
    const showDetail = atomicNumber => {
      const item = periodicElements.find(element => element.atomicNumber === Number(atomicNumber));
      const panel = app.querySelector('[data-element-detail]');
      const valence = item.valences?.length ? item.valences.join(', ') : 'Non determinate';
      panel.innerHTML = `<div class="element-detail-head">
        <div class="element-detail-symbol ${esc(item.category)}"><small>${item.atomicNumber}</small><b>${esc(item.symbol)}</b></div>
        <div><div class="eyebrow">${esc(categoryLabel(item.category))}</div><h2>${esc(item.name)}</h2><p>Periodo ${item.period}${item.group ? ` · Gruppo ${item.group}` : ' · Serie del blocco f'}</p></div>
      </div>
      <div class="element-property-grid">
        <div><small>Famiglia</small><b>${esc(categoryLabel(item.category))}</b></div>
        <div><small>Stato standard</small><b>${esc(item.standardState)}</b></div>
        <div><small>Origine</small><b>${item.artificial ? 'Sintetico / artificiale*' : 'Rilevato in natura'}</b></div>
        <div><small>Numero atomico</small><b>${item.atomicNumber}</b></div>
        <div><small>Massa atomica</small><b>${esc(item.atomicMass)} u</b></div>
        <div><small>Valenze (da N.O.)</small><b>${esc(valence)}</b></div>
        <div><small>Temperatura di fusione</small><b>${esc(formatTemperature(item.meltingKelvin))}</b></div>
        <div><small>Temperatura di ebollizione</small><b>${esc(formatTemperature(item.boilingKelvin))}</b></div>
        <div class="wide"><small>Numeri di ossidazione</small><b>${esc(item.oxidationStates || 'Non determinati')}</b></div>
        <div class="wide"><small>Configurazione elettronica</small><b>${esc(item.electronConfiguration || 'Non determinata')}</b></div>
      </div>
      <p class="element-source-note">Dati PubChem. Le valenze sono ricavate dai valori assoluti dei numeri di ossidazione e possono dipendere dal composto. “Previsto” indica un dato teorico; *tecnezio, promezio ed elementi oltre l’uranio sono contrassegnati come sintetici, pur potendo esistere tracce naturali. Le proprietà non note sono indicate come non determinate.</p>`;
    };
    const filter = () => {
      const query = normalizeSearch(search.value);
      const category = select.value;
      let matches = 0;
      let firstMatch = null;
      elements.forEach(element => {
        const match = (!query || normalizeSearch(element.dataset.search).includes(query)) && (!category || element.dataset.category === category);
        element.classList.toggle('dimmed', !match);
        if (match) {
          matches += 1;
          firstMatch ||= element;
        }
      });
      empty.classList.toggle('hidden', matches > 0);
      if ((query || category) && firstMatch) showDetail(firstMatch.dataset.element);
    };
    search.addEventListener('input', filter);
    select.addEventListener('change', filter);
    elements.forEach(element => element.onclick = () => showDetail(element.dataset.element));
    showDetail(1);
  };

  const timelineMarkup = items => `<div class="history-timeline">${items.map(item => `<article class="history-person" data-search="${esc(`${item.name} ${item.birthName || ''} ${item.years} ${item.party || ''} ${item.area || ''} ${item.note || ''}`)}">
    <span class="history-years">${esc(item.years)}</span><div><h3>${esc(item.name)}${item.current ? '<mark>In carica</mark>' : ''}</h3>${item.birthName ? `<p>${esc(item.birthName)}</p>` : ''}${item.party || item.area ? `<div class="political-tags">${item.party ? `<span>${esc(item.party)}</span>` : ''}${item.area ? `<span class="area">${esc(item.area)}</span>` : ''}</div>` : ''}${item.note ? `<small>${esc(item.note)}</small>` : ''}</div>
  </article>`).join('')}</div>`;

  const historyView = () => {
    app.innerHTML = `<a class="back-link" href="#notes">← Tutti gli appunti</a>${sectionLinks()}
      <div class="section-head notes-page-head"><div><div class="eyebrow">Storia istituzionale</div><h1>Cronologie d’Italia e della Chiesa</h1></div><a class="button primary compact" href="#category/storia">Vai ai quiz</a></div>
      <p class="notes-lead">Re, Presidenti della Repubblica, Papi e tutti i Presidenti del Consiglio dall’Unità d’Italia a oggi.</p>
      <div class="card notes-inline-search"><label>Cerca un nome o un anno<input data-notes-filter type="search" placeholder="Es. Pertini, 1978, Leone XIV…" autocomplete="off"></label></div>
      <aside class="history-classification-note"><b>Come leggere le aree politiche</b><span>Nel Regno d’Italia sono indicate Destra storica, Sinistra storica e le successive aree liberali; dal 1922 è distinto il fascismo. Per transizione e Repubblica sono riportati partito e area del governo. Le etichette sono sintesi didattiche: coalizioni e orientamenti possono cambiare tra un mandato e l’altro.</span></aside>
      <div class="history-sections">
        <details class="card history-section" id="re-italia" open><summary><span><small>${kingsOfItaly.length} sovrani</small><b>Re d’Italia</b><em>Da Vittorio Emanuele II a Umberto II · 1861–1946</em></span><i>⌄</i></summary>${timelineMarkup(kingsOfItaly)}</details>
        <details class="card history-section" id="presidenti-repubblica"><summary><span><small>12 nomi</small><b>Presidenti della Repubblica</b><em>Dal Capo provvisorio dello Stato a oggi</em></span><i>⌄</i></summary>${timelineMarkup(presidents)}</details>
        <details class="card history-section" id="papi"><summary><span><small>13 Pontefici</small><b>Papi dall’Unità d’Italia</b><em>Da Pio IX a Leone XIV</em></span><i>⌄</i></summary>${timelineMarkup(popes)}</details>
        <details class="card history-section" id="presidenti-consiglio-regno"><summary><span><small>${kingdomPrimeMinisters.length} nomi</small><b>Presidenti del Consiglio del Regno</b><em>Dall’Unità d’Italia alla caduta del fascismo · 1861–1943</em></span><i>⌄</i></summary>${timelineMarkup(kingdomPrimeMinisters)}</details>
        <details class="card history-section" id="presidenti-consiglio-transizione"><summary><span><small>${transitionPrimeMinisters.length} nomi</small><b>Transizione costituzionale</b><em>Dalla caduta del fascismo alla Repubblica · 1943–1946</em></span><i>⌄</i></summary>${timelineMarkup(transitionPrimeMinisters)}</details>
        <details class="card history-section" id="presidenti-consiglio"><summary><span><small>${primeMinisters.length} nomi</small><b>Presidenti del Consiglio della Repubblica</b><em>Dal 1946 a oggi</em></span><i>⌄</i></summary>${timelineMarkup(primeMinisters)}</details>
      </div><p class="notes-empty hidden" data-notes-empty>Nessun nome o periodo corrisponde alla ricerca.</p>
      <div class="section-head"><div><div class="eyebrow">Aiuti allo studio</div><h2>Trucchi mnemonici</h2></div></div>
      <div class="memory-grid">${memoryTricks.map(trick => `<article class="card memory-card"><span>${esc(trick.title)}</span><h3>${esc(trick.initials)}</h3><blockquote>${esc(trick.phrase)}</blockquote><p>${esc(trick.explanation)}</p></article>`).join('')}</div>
      <p class="memory-disclaimer">I trucchi mnemonici sono aiuti amatoriali creati per ricordare l’ordine: non sono contenuti ufficiali e non sostituiscono lo studio delle date.</p>${sourcesMarkup()}`;

    const input = app.querySelector('[data-notes-filter]');
    const empty = app.querySelector('[data-notes-empty]');
    input.addEventListener('input', () => {
      const query = normalizeSearch(input.value);
      let count = 0;
      app.querySelectorAll('.history-person').forEach(item => {
        const match = !query || normalizeSearch(item.dataset.search).includes(query);
        item.classList.toggle('hidden', !match);
        if (match) {
          count += 1;
          if (query) item.closest('details').open = true;
        }
      });
      empty.classList.toggle('hidden', count > 0);
    });
  };

  if (section === 'chimica') subjectView('chimica');
  else if (section === 'fisica') subjectView('fisica');
  else if (section === 'informatica') subjectView('informatica');
  else if (section === 'logica') subjectView('logica');
  else if (section === 'inglese') subjectView('inglese');
  else if (section === 'tavola-periodica') periodicView();
  else if (section === 'storia') historyView();
  else homeView();
}
