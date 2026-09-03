# Changelog

## 3.15.0 - 2026-09-03

- Le fasce della Dashboard admin sono ora selezionabili.
- Il popup della fascia mostra foto profilo, nome, username, media da 40 e numero di prove di ogni candidato.
- Candidati ordinati per media decrescente; popup responsive e accessibile anche da tastiera.
- Dati nominativi disponibili soltanto agli amministratori.
- Nessun popup generale agli utenti.

## 3.14.3 - 2026-09-03

- Corretto il caricamento simultaneo che poteva mostrare due volte il riquadro «Sbarramento teorico».
- Nessuna duplicazione era presente nel database e nessun valore statistico è stato modificato.
- Nessun popup generale agli utenti.

## 3.14.2 - 2026-09-03

- Aggiunta alla Dashboard admin la soglia di sbarramento teorica di 14,71/40.
- Mostrati candidati sopra e sotto la soglia, con percentuale sul campione che ha svolto almeno una prova.
- Il riferimento è dichiarato come stima teorica e non come soglia ufficiale del concorso.
- Nessun popup generale agli utenti.

## 3.14.1 - 2026-09-03

- Nella Dashboard amministrativa ogni fascia mostra direttamente il proprio intervallo di punteggio.
- Restano visibili nello stesso riquadro numero dei candidati e proporzione grafica.
- Nessun popup generale agli utenti.

## 3.14.0 - 2026-09-03

- Nuova Dashboard amministrativa dedicata alla preparazione globale dei candidati.
- Medie distinte per singola prova, per candidato e per candidati con almeno tre prove, per evitare distorsioni dovute agli utenti più assidui.
- Fasce di preparazione indicative, numerosità e affidabilità del campione, giuste/sbagliate/non risposte medie.
- Confronto tra simulazioni, guidate e Sfida del giorno, andamento su 14 giorni e materie collettivamente più deboli.
- Endpoint aggregato accessibile soltanto agli amministratori; nessuna soglia viene presentata come previsione ufficiale.
- Nessun popup generale agli utenti.
- Ampliata su desktop la finestra «Apri prova» della Sfida del giorno ed eliminata la barra di scorrimento orizzontale superflua.

## 3.13.0 - 2026-09-03

- La Sfida del giorno registra il tempo cumulativo dedicato a ogni singola domanda, anche dopo ritorni e cambi di domanda.
- «Apri prova» mostra all’admin il tempo per quesito mantenendo numero e ordine originali della prova.
- Il selettore Sbagliate / Non risposte / Giuste non rimane più fissato a metà della finestra amministrativa, su desktop, tablet e mobile.
- Le prove già concluse prima di questa versione restano consultabili, ma non hanno tempi retroattivi.
- Nessuna modifica a punteggi o classifiche e nessun popup generale agli utenti.

## 3.12.0 - 2026-09-03

- Aggiunto nella classifica il pulsante amministrativo «Apri prova».
- L’admin può consultare tutte le 40 domande con risposta data, soluzione, esito e spiegazione.
- Endpoint protetto per ruolo amministratore; gli utenti ordinari non ricevono identificativi o dettagli delle prove altrui.
- Consultazione in sola lettura, senza modifiche a punteggi e classifiche; nessun popup generale.

## 3.11.1 - 2026-09-03

- Nei quiz ordinati e guidati per materia, una risposta corretta assegna automaticamente ★ Facile.
- Le risposte errate restano senza valutazione automatica e possono essere classificate dall’utente.
- Il voto automatico o manuale rimane sempre modificabile.
- Sfida del giorno, prove da 40 e Tutor restano esclusi; nessun popup generale agli utenti.

## 3.11.0 - 2026-09-03

- Aggiunta l’opzione amministrativa disattivabile «Sfida del giorno obbligatoria».
- Gli utenti che non hanno ancora consegnato la sfida vengono indirizzati alla prova prima di accedere alle risorse didattiche.
- Amministratori esclusi dal vincolo; account, privacy e logout rimangono disponibili.
- Sblocco immediato dopo la consegna e controllo automatico al login, al cambio di giornata e durante l’uso della PWA.
- Impostazione inizialmente disattivata e nessun popup generale agli utenti.

## 3.10.1 - 2026-09-02

- Corretta la rotazione della Sfida del giorno: i quesiti già comparsi nei giorni precedenti vengono esclusi finché il relativo gruppo non è esaurito.
- Quando occorre riciclare un gruppo, vengono preferiti i quesiti meno utilizzati e meno recenti.
- Le sfide già pubblicate e le relative classifiche non vengono rigenerate.
- Nessun popup generale di changelog agli utenti.

## 3.10.0 - 2026-09-02

- Introdotta nei quiz ordinati e guidati per materia la scala ★ Facile, ★★ Media, ★★★ Difficile.
- Un solo voto modificabile per utente e quesito, con media comunitaria e numero di voti.
- Valutazioni escluse da Sfida del giorno, simulazioni da 40 e Tutor.
- Voti compresi nell’esportazione personale e nei backup completi; cancellazione automatica con l’account.
- Informativa privacy aggiornata per chiarire che agli altri utenti sono visibili soltanto media e conteggio aggregati.
- Popup informativo attivo per tutti gli utenti. Cache PWA revisione 66.

## 3.9.0 - 2026-08-30

- Risposta personale dell’admin alle segnalazioni: quesito corretto con spiegazione oppure segnalazione accolta con disabilitazione.
- Popup riservato al destinatario con quesito, alternative ed esito; nessuna interruzione delle prove in corso.
- Pulsanti «Ho letto» e «Più tardi», con lettura condivisa tra dispositivi e rinvio di cinque minuti.
- Risposte e conferme di lettura incluse nei backup; migrazione additiva del database senza modifiche a statistiche o classifiche.
- Protezione del testo in scrittura nel pannello admin durante il ricaricamento automatico.
- Cache PWA revisione 65. Nessun popup generale di changelog agli utenti.

## 3.8.2 - 2026-08-29

- Risolto il blocco della **Sfida del giorno** sulla schermata “Preparazione…” causato dall'esaurimento delle connessioni PostgreSQL.
- Resa affidabile la chiusura delle sessioni database anche con numerose richieste contemporanee.
- Aumentata la capacità del pool per classifica, foto profilo e chiamate PWA parallele.
- Nessuna modifica alle domande, alle partecipazioni o alla classifica della sfida in corso; nessun popup automatico agli utenti.

## 3.8.1 - 2026-08-29

- Attivato per tutti gli utenti un popup informativo, mostrato una sola volta, sulla nuova foto profilo.
- Il popup spiega dove caricare la foto e offre il pulsante diretto **Apri Account**.
- La comunicazione viene rimandata se è in corso un quiz o una simulazione.
- Cache PWA aggiornata alla revisione 64.

## 3.8.0 - 2026-08-29

- Aggiunta la foto profilo personale nella schermata **Account**, con anteprima, ottimizzazione automatica e possibilità di rimozione.
- La foto compare accanto al nome nella classifica della **Sfida del giorno**, con layout adattato a desktop, tablet, smartphone e tema scuro.
- In assenza di una foto viene mostrata l'immagine neutra fornita come avatar predefinito.
- Le immagini personalizzate sono disponibili soltanto dopo l'accesso, validate come JPEG/PNG/WebP e limitate a 1 MB dopo l'ottimizzazione.
- Foto e metadati sono conservati in PostgreSQL, inclusi nei backup/ripristini e nell'esportazione personale; la cancellazione dell'account elimina anche la foto.
- Aggiornata l'informativa privacy sulla visibilità della foto nella classifica interna.
- Cache PWA aggiornata alla revisione 63; nessun popup di changelog viene inviato automaticamente agli utenti.

## 3.7.0 - 2026-08-28

- Aggiunti tre promemoria interni della **Sfida del giorno**: mattina, metà giornata e sera.
- Ogni fascia viene mostrata al massimo una volta al giorno per account e la memoria è sincronizzata tra i dispositivi.
- Il server verifica lo stato reale della sfida: chi ha già consegnato non riceve alcun promemoria.
- I popup non interrompono quiz o simulazioni in corso e non appaiono mentre l'utente sta già consultando la Sfida.
- Il messaggio distingue tra sfida da iniziare e sfida da riprendere e mostra quanti candidati sono già entrati in classifica.
- Nessun popup separato di changelog viene inviato agli utenti.

## 3.6.1 - 2026-08-28

- Aggiunto sulla voce **Utenti** del menu Admin il contatore degli account in attesa di approvazione.
- Il contatore viene verificato all'accesso, ogni 90 secondi e quando l'app torna in primo piano.
- Dopo l'approvazione la notifica viene aggiornata immediatamente, senza ricaricare il portale.
- Nessun popup di aggiornamento viene inviato agli utenti per questa modifica amministrativa.

## 3.6.0 - 2026-08-27

- Aggiunta nell’Admin una configurazione dedicata della Sfida del giorno con quantità modificabili per materia e per sottosezione di Logica.
- I quesiti di comprensione dei brani sono sempre esclusi dalla Sfida del giorno, anche se una richiesta amministrativa tenta di inserirli.
- Cambiare la configurazione non rigenera la sfida già creata oggi e non modifica tentativi, punteggi o classifica in corso; la nuova composizione vale dalla prossima generazione.
- Nella schermata conclusiva la classifica è mostrata prima del risultato personale.
- Le 40 domande corrette sono raccolte nel pannello richiudibile **Il tuo test**.
- Rimossa la voce **Dati** dalla barra di navigazione.
- Aggiunto **Segnala quesito errato** nelle prove e nei riepiloghi, con motivo e nota facoltativa.
- Nuova coda **Segnalazioni quesiti** nel pannello Admin, contatore di notifica, revisione e chiusura degli avvisi.
- L’admin può rendere un quesito non disponibile nelle nuove esercitazioni o riattivarlo; prove già iniziate, Sfida già generata e classifica restano intatte.
- Backup e ripristino includono segnalazioni e quesiti disattivati; la nuova migrazione PostgreSQL non modifica i dati esistenti.
- Cache PWA aggiornata alla revisione 60 e popup informativo una tantum agli utenti per presentare il nuovo pulsante di segnalazione.

## 3.5.0 - 2026-08-27

- Introdotta la **Sfida del giorno**: una prova ufficiale da 40 domande, identica e nello stesso ordine per tutti gli utenti.
- Cronometro da 40 minuti, correzione esclusivamente alla consegna e punteggio ufficiale `+1 / -0,33 / 0` calcolato dal server.
- Un solo tentativo valido per account al giorno; le risposte confermate vengono salvate sul server e la prova può essere ripresa mentre il timer continua.
- Aggiunta la classifica giornaliera con spareggio per risposte corrette, errori e tempo impiegato.
- Soluzioni, spiegazioni e revisione completa vengono rese disponibili soltanto al termine della sfida.
- Il risultato entra nelle statistiche personali, aggiorna la classificazione delle domande e alimenta il Tutor.
- Aggiunto il controllo amministratore per attivare/disattivare sfida e classifica; la composizione usa la configurazione predefinita dell’admin e non le preferenze personali.
- Backup e ripristino includono sfide, tentativi e classifiche.
- Aggiornata l’informativa privacy con la visibilità del nome visualizzato e del risultato ai soli utenti autenticati.
- Cache PWA aggiornata alla revisione 58. Nessun popup automatico agli utenti.

## 3.4.1 - 2026-08-26

- rimossi dal portale server i PDF originali: le dispense vengono distribuite soltanto come lezioni native;
- sostituite le schermate di pagine intere con ritagli dei soli schemi, formule, mappe e diagrammi utili;
- aggiunto il recupero OCR delle pagine-immagine, eliminando sezioni e capitoli apparentemente vuoti;
- ricostruite come tabelle native e responsive le pagine non estraibili su ossiacidi, sali ternari, reazioni di sintesi e prefissi del Sistema Internazionale;
- rese le verifiche specifiche per la lezione corrente, senza trascinare automaticamente gli argomenti precedenti;
- aggiunti filtri puntuali per periodi storici, tipi di logica, capitoli di fisica e chimica e programmi informatici;
- se la banca dati non contiene quesiti davvero compatibili, il portale lo segnala senza usare domande generiche;
- corretto l’indice laterale delle lezioni: ora scorre al capitolo scelto senza cambiare rotta o tornare alla Home;
- cache PWA aggiornata alla versione 57; nessun popup automatico inviato agli utenti.

## 3.4.0 - 2026-08-26

- digitalizzate 85 dispense in 166.770 parole organizzate come lezioni native del portale, eliminando il passaggio obbligatorio dal visualizzatore PDF;
- conservati 302 schemi, formule, tabelle ed esempi visuali selezionati dalle pagine originali;
- aggiunti indice interno, impaginazione responsive, lettura ottimizzata e supporto completo al tema scuro;
- aggiunta a ogni lezione la verifica di fine capitolo con 5 quesiti reali relativi soltanto agli argomenti già affrontati;
- la selezione delle verifiche privilegia domande non fatte, non note o da ripetere e applica gli esiti al percorso personale “Le so / Da ripetere”;
- spiegazioni mantenute a tendina e risultati registrati nello storico quiz dell’utente;
- cache PWA aggiornata alla versione 56; nessun popup automatico inviato agli utenti.

## 3.3.2 - 2026-08-26

- Corretto il messaggio “connessione negata” nel lettore PDF dei Percorsi di studio: i documenti possono essere incorporati esclusivamente dalle pagine dello stesso portale.
- Mantenute le protezioni contro l'incorporamento da siti esterni e incrementata la cache PWA.

## 3.3.1 - 2026-08-26

- Corretto il pacchetto cloud affinché includa nel contenitore i moduli, gli stili e tutti i documenti dei nuovi Percorsi di studio.
- Incrementata la cache PWA per rendere subito disponibili i file della nuova sezione dopo l'aggiornamento.

## 3.3.0 - 2026-08-25

- aggiunta la nuova sezione autonoma **Percorsi di studio**, separata dagli Appunti;
- organizzati tutti i 98 materiali consegnati in cinque percorsi e moduli progressivi: Storia, Logica e matematica, Fisica, Chimica e Informatica;
- integrate 85 dispense PDF, 9 bignami in formato Pages tramite anteprima visuale e 4 schemi grafici;
- ogni utente dispone di avanzamento personale per lezione, stato “Da iniziare”, “In corso” o “Completata” e funzione Riprendi;
- aggiunto il collegamento diretto tra ciascuna lezione e i quiz del relativo sottoargomento;
- il Tutor segnala nella sezione il contenuto più adatto all’area debole prioritaria;
- l’amministratore può mostrare o nascondere ogni percorso e vedere quante lezioni ha completato ciascun utente;
- i documenti si aprono dentro il percorso con comando per la visualizzazione a tutto schermo;
- interfaccia verificata per tema chiaro/scuro, telefono, tablet e desktop;
- cache PWA aggiornata alla versione 53; nessun popup automatico inviato agli utenti.

## 3.2.0 - 2026-08-25

- aggiunti 10 capitoli di Informatica allineati ai 2.119 quesiti e ai relativi sottoargomenti;
- aggiunti 10 capitoli di Logica allineati ai 5.853 quesiti, con procedure di risoluzione ed errori tipici;
- aggiunti 10 capitoli di Inglese allineati ai 1.551 quesiti, con regole, esempi e trappole ricorrenti;
- ogni capitolo mostra quanti quesiti del dataset sono collegati e rimanda direttamente all’allenamento della materia;
- ricerca Appunti estesa ai trenta nuovi capitoli;
- aggiunti i quattro Re d’Italia dal 1861 al 1946;
- aggiunti tutti i Presidenti del Consiglio del Regno d’Italia e della transizione costituzionale, con area politica e partito;
- mantenuta separata la cronologia completa dei Presidenti del Consiglio della Repubblica;
- interfaccia verificata su desktop, tablet, telefono e tema scuro;
- cache PWA aggiornata alla versione 52; nessun popup automatico inviato agli utenti.

## 3.1.0 - 2026-08-25

- ampliata la scheda di tutti i 118 elementi con famiglia, stato standard, origine naturale o sintetica, numero e massa atomica, valenze, temperature di fusione ed ebollizione, numeri di ossidazione e configurazione elettronica;
- dati chimici verificati tramite PubChem, con indicazione esplicita dei valori previsti o non determinati;
- aggiunti partito e area politica a tutti i Presidenti del Consiglio della Repubblica;
- inserita una nota didattica che distingue i governi repubblicani da Destra storica e Sinistra storica del Regno d’Italia;
- ricerca Appunti estesa alle nuove proprietà chimiche e classificazioni politiche;
- migliorata la disposizione delle schede su desktop, tablet, telefono e tema scuro;
- cache PWA aggiornata alla versione 51.

## 3.0.1 - 2026-08-25

- attivato per tutti gli utenti il popup informativo della nuova sezione Appunti;
- il messaggio presenta Chimica, Fisica, tavola periodica, cronologie e ricerca globale;
- il popup viene mostrato una sola volta per account;
- cache PWA aggiornata alla versione 50.

## 3.0.0 - 2026-08-25

- nuova sezione **Appunti** accessibile dal menu principale e dalla Home;
- appunti sintetici di Chimica e Fisica divisi in capitoli richiudibili, con ricerca per definizione o formula;
- tavola periodica interattiva completa di 118 elementi, filtri per famiglia e scheda dettaglio;
- cronologie aggiornate di Presidenti della Repubblica, Papi dall’Unità d’Italia e Presidenti del Consiglio dalla nascita della Repubblica;
- ricerca unica tra concetti, elementi e personaggi storici;
- trucchi mnemonici per l’ordine dei Papi e dei Presidenti della Repubblica, chiaramente indicati come aiuti amatoriali;
- interfaccia Appunti ottimizzata per tema chiaro/scuro, telefono, tablet e desktop;
- cache PWA aggiornata alla versione 49; il rilascio non apre popup automatici agli utenti.

## 2.9.1 - 2026-08-25

- Corretta la perdita della risposta selezionata nella prova guidata da 40 quando si passa a un’altra domanda tramite la panoramica.
- Aggiunta una memoria provvisoria separata per ciascuna delle 40 domande: le scelte restano modificabili fino alla conferma.
- Conservate le risposte selezionate anche dopo un ricaricamento o la ripresa della prova in corso.
- Conteggiate alla consegna le risposte selezionate ma non ancora confermate singolarmente; soltanto i quesiti realmente vuoti restano non risposti.
- Aggiunto nella panoramica lo stato “Selezionata” per distinguere le risposte provvisorie da quelle già corrette o errate.
- Attivato un popup informativo del bugfix mostrato una sola volta a ogni utente.
- Aggiornata la cache PWA alla versione 48.

## 2.9.0 - 2026-08-25

- Divise le 2.119 domande di Informatica in dieci settori: hardware, sistemi e file, Word, Excel, Office e dati, reti, Internet, sicurezza, software e informatica generale.
- Divise le 1.090 domande di Storia in dieci periodi e aree, dal Risorgimento all’Italia repubblicana e alla storia internazionale.
- Divise le 1.551 domande di Inglese in dieci settori grammaticali e lessicali, tra cui tempi verbali, modali, pronomi, preposizioni, costruzione della frase e vocabolario.
- Aggiunti per tutti i nuovi settori percorso ordinato, ripresa, quiz guidati, filtri, grafico, statistiche e analisi del Tutor.
- Mantenute senza modifiche banca dati, risposte, spiegazioni, preferenze, utenti e progressi esistenti.
- Attivato per questa release un popup informativo mostrato una sola volta a ogni utente.
- Aggiornata la cache PWA alla versione 47.

## 2.8.2 - 2026-08-20

- Mostrate cinque voci alla volta nel menu inferiore su telefono.
- Reso il menu scorrevole orizzontalmente per raggiungere Dati, Utenti e Admin senza comprimere le icone.
- Portata automaticamente in vista la voce attiva durante la navigazione.
- Disattivati i popup automatici di changelog; potranno essere riattivati esplicitamente per una release scelta dall’amministratore.
- Aggiornata la cache PWA alla versione 46.

## 2.8.1 - 2026-08-20

- Aggiunto **Tutor** come pulsante nel menu inferiore fisso.
- Mantenuto l’accesso al Tutor anche dalla Home.
- Compattata la barra superiore alle larghezze tablet per evitare pulsanti fuori dal bordo in orizzontale.
- Aggiornata la cache PWA alla versione 45 per rendere subito disponibili la nuova navigazione e la correzione tablet.

## 2.8.0 - 2026-08-20

- Aggiunta la nuova sezione **Tutor**, accessibile dalla Home.
- Analizzati errori, non risposte, punti persi e precisione delle ultime cinque prove da 40, insieme allo stato generale delle domande.
- Individuate automaticamente le priorità per materia e, quando disponibile, per sottosettore di Logica, Chimica e Fisica.
- Aggiunta per ogni priorità una strategia di studio motivata e un allenamento dedicato avviabile direttamente.
- Aggiunti piani personali da 15, 30 o 60 minuti, rispettivamente con 15, 30 o 50 domande.
- Distribuito il piano tra le tre aree più deboli con priorità a Non le so, Da ripetere e Da fare.
- Aggiunta una rotazione Tutor separata, così l’allenamento non altera la memoria anti-ripetizione delle simulazioni da 40.
- Salvati gli allenamenti Tutor nella cronologia e nelle statistiche personali e amministrative.
- Aggiornata la cache PWA alla versione 43.

## 2.7.0 - 2026-08-20

- Divise le 1.677 domande di Chimica in dieci settori selezionabili, tra cui reazioni, leggi e bilanciamenti, atomo, legami, mole e soluzioni, acidi e basi, stati della materia e chimica organica.
- Divise le 2.004 domande di Fisica in dieci settori selezionabili, tra cui misure, cinematica, dinamica, energia, fluidi, termodinamica, onde, elettromagnetismo e fisica atomica.
- Aggiunti per ogni settore percorso ordinato, ripresa dalle non fatte, quiz guidati, filtri personali, grafico e statistiche dedicate.
- Mostrato il settore accanto alla materia durante i quiz di Chimica e Fisica.
- Resi stabilmente fissi il menu superiore e la navigazione inferiore durante lo scorrimento su browser mobili e PWA.
- Conservate integralmente domande, risposte, spiegazioni, progressi, utenti, preferenze e statistiche esistenti.
- Aggiornata la cache PWA alla versione 42.

## 2.6.1 - 2026-08-17

- Riunite **Logica**, **Logica · Brani** e **Logica · Insiemi** in un’unica macro-materia Logica.
- Aggiunti Comprensione dei brani e Insiemi e diagrammi tra i tipi selezionabili nello studio e nelle prove da 40.
- Conservata automaticamente la precedente composizione ufficiale trasformando 11 Logica + 1 Insiemi in 12 Logica.
- Riunite le statistiche di Logica senza perdere progressi, sessioni o preferenze personali esistenti.
- Reso esplicito il totale di ogni tipo di quiz; Figure e simboli comprende 785 quesiti, 765 dei quali con immagine.
- Ridotte dimensioni e spazi verticali di domande, immagini e risposte su desktop, tablet e mobile.
- Aggiornata la cache PWA alla versione 41.

## 2.6.0 - 2026-08-17

- Aggiunte 3.224 domande di logica dopo esclusione dei brani lunghi e deduplica rispetto alla banca esistente.
- Importate tutte le figure necessarie ai quesiti visivi e aggiunta una nota di soluzione verificata quando non è disponibile un commento esplicativo completo.
- Divisa Logica in otto sottosezioni: deduzioni, serie, verbale, calcolo, figure, relazioni, ordinamenti e logica mista.
- Aggiunti studio ordinato, quiz guidati, filtri personali, grafico e statistiche per ogni sottosezione.
- Nelle configurazioni delle prove da 40 è ora possibile distribuire esattamente il totale Logica tra le sottosezioni scelte.
- La rotazione e il Deep learning tengono traccia separatamente delle sottosezioni, evitando ripetizioni premature.
- I nuovi account pubblici richiedono approvazione amministrativa; tutti gli account preesistenti restano approvati tramite migrazione.
- Aggiornata la cache PWA alla versione 40 senza eliminare dati o statistiche degli utenti.

## 2.5.1 - 2026-08-17

- Corretta la ripetizione delle prime domande nei filtri dei quiz per materia.
- Aggiunto un cursore personale separato per materia e stato: **Le so**, **Da ripetere**, **Non le so** e **Da fare**.
- La riapertura mantiene l'ordine ufficiale e riparte dalla domanda successiva all'ultima svolta.
- Per gli utenti esistenti il cursore iniziale viene ricostruito dall'attività più recente già salvata.
- Progressi, statistiche e classificazioni esistenti restano invariati.

## 2.5.0 - 2026-08-17

- Verificate sul database reale 8 e 12 ripetizioni tra prove guidate consecutive e corretta la causa.
- Aggiunta una memoria unica, condivisa da simulazione ufficiale e prova guidata, per tutte le domande già mostrate nelle prove da 40.
- La memoria resta valida anche quando una risposta corretta cambia lo stato della domanda in **Le so**.
- La selezione privilegia sempre **Non le so**, **Da ripetere** e **Da fare** prima delle domande note.
- La prova guidata usa l'intera banca dati; le spiegazioni non disponibili non vengono inventate.
- Nella prova guidata da 40 la risposta è modificabile fino alla conferma con **Continua**.
- Il comando **Termina prova** permette di concludere e salvare, annullare oppure terminare senza salvare.
- L'abbandono senza salvataggio ripristina anche la rotazione precedente, senza alterare il percorso futuro.

## 2.4.0 - 2026-08-17

- Corretta la rotazione delle prove da 40 per impedire ripetizioni prima dell'esaurimento delle domande disponibili nel ciclo.
- Il Deep learning usa ora le classificazioni personali maturate in tutte le modalità, compresi i quiz per materia.
- Aggiunta priorità esplicita: **Non le so**, **Da ripetere**, **Da fare** e, solo quando necessario, **Le so**.
- Aggiunta memoria delle domande deboli già proposte, separata per simulazione ufficiale e prova guidata.
- Una risposta corretta classifica subito la domanda come **Le so**; un errore la classifica **Da ripetere**.
- Aggiunti test automatici sulla rotazione ordinaria, sulla priorità adattiva e sul caso con 900 domande già note.

## 2.3.0 - 2026-08-14

- Aggiunta informativa privacy pubblica strutturata secondo gli articoli 12 e 13 GDPR.
- Aggiunta configurazione Admin di titolare, email, PEC, DPO opzionale, infrastruttura, provider email, trasferimenti e conservazione.
- Registrazione con presa visione versionata dell'informativa e relativa data nel profilo utente.
- Esportazione personale di profilo, statistiche, preferenze e log senza password o token.
- Pulizia automatica dei log di sicurezza oltre il periodo configurato e minimizzazione dei dati dei login falliti.
- Informativa accessibile dal login, dalla registrazione e dall'account, con stampa/PDF, tema scuro e layout mobile/tablet.

## 2.2.0 - 2026-08-14

- Nuovo centro aggiornamenti cloud riservato agli amministratori.
- Controllo automatico al login e controllo manuale delle release GitHub.
- Versione installata sempre visibile e confronto con la nuova versione disponibile.
- Changelog mostrato prima dell’installazione.
- Installazione da GitHub oppure da pacchetto ZIP server caricato manualmente.
- Validazione di versione, percorsi e hash dei file del pacchetto.
- Backup PostgreSQL e copia dei file automatici prima dell’aggiornamento, con ripristino dei file in caso di errore.
- Riavvio e spegnimento del solo portale dal pannello Admin, entrambi con conferma.
- Pacchetto server unico per Linux e Windows e nuovi script di gestione Windows.
- Nuove release EXE standalone dismesse; PostgreSQL resta il database ufficiale.

## 2.1.5 - 2026-08-14

- Resa più leggibile la cronologia con indicatori separati per **Giuste**, **Sbagliate** e **Non risposte**.
- Aggiunta la revisione completa degli ultimi 5 quiz: domanda, risposta data, soluzione corretta e spiegazione.
- Limitati ai 5 quiz più recenti i dettagli delle domande per contenere lo spazio occupato, mantenendo punteggi e statistiche di tutta la cronologia.
- Aggiunto per ogni utente un popup, mostrato una sola volta dopo l'aggiornamento, con il riepilogo delle novità.

## 2.1.4 - 2026-08-13

- Separata la gestione **Utenti e statistiche** dalle Impostazioni amministrative.
- Aggiunta una voce **Utenti** dedicata, visibile esclusivamente agli amministratori, su desktop, tablet e mobile.
- Mantenute nella nuova pagina tutte le funzioni di creazione e gestione account e le statistiche cloud per singolo utente.

## 2.1.3 - 2026-08-12

- Aggiunto il Deep learning opzionale per le prove da 40: le domande corrette vengono sospese fino al completamento della materia, mentre errori e non risposte restano nel ripasso.
- Separati i cicli adattivi della simulazione ufficiale e della prova guidata, con avanzamento per utente, riepilogo finale e salvataggio nei backup cloud e portatili.
- Aggiunto al primo accesso un popup informativo che permette di attivare subito il Deep learning o rimandare.
- Aggiunto il popup **Installa** con istruzioni dedicate a iPhone/iPad, Android e tablet, più il pulsante nativo quando supportato dal browser.
- Aggiunta una modalità tablet PWA automatica ottimizzata per orientamento verticale e orizzontale.
- Completato il tema scuro per spiegazioni, correzioni, dialoghi di consegna e abbandono prova, popup e pannelli che potevano mantenere sfondi chiari.

## 2.1.2 - 2026-08-12

- Aggiunto nelle schermate di accesso, registrazione e recupero password il disclaimer che identifica la piattaforma come gratuita, amatoriale, non ufficiale e non collegata al Ministero dell'Interno o al Corpo Nazionale dei Vigili del Fuoco.
- Sostituito in tutta l'app il logo precedente con il nuovo marchio nero e aggiunta all'area Admin la possibilità di caricare o ripristinare il logo globale.
- Aggiunti i temi chiaro, scuro e automatico, salvati separatamente per ogni utente.
- Aggiunte nel pannello Admin la media delle prove da 40 domande e le medie dei quiz per argomento, sia complessive sia per singolo utente.
- Reso esplicito lo stato dell'invio email e impediti falsi messaggi di invio quando il server SMTP non è configurato.
- L'email è ora obbligatoria nella registrazione pubblica per consentire il recupero della password.
- Migliorata la resa responsive del portale e corretta la visualizzazione del logo senza compressione.

## 2.1.1 - 2026-08-12

- Aggiunta la voce **Admin** nella navigazione, visibile esclusivamente agli amministratori.
- Riunite nel pannello Admin gestione utenti, statistiche, registrazioni, DuckDNS, email, backup e configurazione delle prove.
- Aggiunto il cambio della porta backend direttamente dal pannello sui server con Caddy host configurato.
- Il cambio porta usa un controllo host separato e limitato: l'app pubblica non riceve accesso al socket Docker.
- Il controllo verifica la disponibilità della porta, riavvia il solo backend, aggiorna Caddy e ripristina automaticamente la configurazione precedente in caso di errore.
- HTTPS pubblico continua a usare la porta 443 anche quando cambia la porta interna dell'app.

## 2.1.0 - 2026-08-12

- Ogni risposta errata viene inserita immediatamente in “Da ripetere”; “Non la so” resta disponibile come classificazione manuale.
- Ogni materia mostra un grafico a torta con domande note, da ripetere, non note e ancora da fare.
- Aggiunte precisione, copertura, tentativi e cronologia dei risultati per singola materia.
- Aggiunte statistiche separate per simulazioni ufficiali, prove guidate e quiz per materia.
- L’app individua automaticamente le materie più carenti e propone esercitazioni mirate sul gruppo più utile.
- Le sessioni salvano il dettaglio dei risultati per materia e restano separate per ogni utente, anche nel portale Cloud.
- Il pannello amministratore Cloud mostra precisione, domande da ripetere e copertura per materia.
- Le spiegazioni sono ora racchiuse in una tendina e si aprono solo su richiesta, durante il quiz e nel riepilogo finale.
- Abbandonando una prova guidata a tempo, le risposte della prova non alterano più i progressi personali.

## 2.0.1 - 2026-08-12

- Aggiunto controllo delle porte già utilizzate durante l'installazione Linux.
- Aggiunta modalità per reverse proxy esistente: HTTPS resta pubblico sulla porta 443 e l'app usa una porta backend libera.
- Aggiunto cambio porte sicuro con ripristino automatico in caso di errore tramite `cloud/configure-ports.sh`.
- Aggiunto supporto per reverse proxy sul sistema host, in container o su un'altra macchina.
- Le porte e la modalità proxy effettive sono ora visibili nel pannello Impostazioni Cloud.

## 2.0.0 - 2026-08-12

- Aggiunta installazione Linux cloud con Docker Compose, PostgreSQL e HTTPS automatico tramite Caddy.
- Aggiunte registrazione pubblica, login con sessione protetta e percorso sincronizzato fra dispositivi.
- Aggiunti recupero password via email SMTP configurabile e reset manuale con password temporanea da parte dell'admin.
- Aggiunti profilo personale e cambio password obbligatorio dopo un reset amministrativo.
- Aggiunta gestione centralizzata degli account: creazione, disattivazione, riattivazione, ruolo ed eliminazione.
- Aggiunta dashboard admin con progressi, livelli di conoscenza, simulazioni, punteggi, materie e ultime attività per ogni utente.
- Aggiunta configurazione admin di portale, registrazioni, sessioni, DuckDNS, SMTP, URL pubblico e informativa breve.
- Aggiunto aggiornamento automatico DuckDNS con token cifrato e test manuale dal pannello.
- Aggiunti backup/ripristino cloud, backup PostgreSQL e migrazioni del database per aggiornamenti futuri.
- Mantenuta la compatibilità con le versioni portatili Windows, EXE e macOS.

## 1.2.0 - 2026-08-11

- Aggiunto il pacchetto Windows con `Quiz-400-VVF-2026.exe`, utilizzabile senza installare Python.
- Aggiunto `Aggiorna-Quiz-400-VVF-2026.exe` per aggiornare con doppio clic e conservare tutti i dati.
- Incorporato negli eseguibili il logo VVF fornito per il progetto.
- L'aggiornamento avviato dalla versione EXE scarica automaticamente il pacchetto Windows corretto.
- Impedito l'avvio simultaneo di più copie dell'EXE sulla stessa porta locale.
- Adattato il server alla modalità grafica senza finestra del terminale.
- Account, progressi, statistiche, configurazioni e backup continuano a essere salvati in `portable-data` accanto all'app.
- Mantenuti gli avviatori portatili tradizionali per Windows e macOS.

## 1.1.6 - 2026-08-11

- Aggiunto `Termina prova` dalla domanda 1 alla 39, sempre con conferma e conteggio delle risposte mancanti.
- Se si cambia menu durante una prova compare un avviso esplicito: confermando, la prova viene eliminata e non può riprendere.
- Dopo l’installazione di un aggiornamento compare `Ricarica e aggiorna cache` per caricare immediatamente la nuova versione.
- La PWA usa ora la rete prima della cache locale, evitando file vecchi dopo gli aggiornamenti.
- Aggiunti identificatori di versione agli asset principali dell’interfaccia.

## 1.1.5 - 2026-08-11

- Il cronometro non resta più sovrapposto ai contenuti durante lo scorrimento.
- Il riquadro del tempo è ora compatto e allineato a destra.
- Aggiunta una barra percentuale che si accorcia con il tempo rimanente.
- Colori progressivi: verde da 40 a 31 minuti, giallo da 30 a 21, arancione da 20 a 11 e rosso lampeggiante negli ultimi 10 minuti.
- Controllo automatico degli aggiornamenti all’accesso, ogni 15 minuti e quando si riapre l’app.
- Se è disponibile una nuova versione, compare un popup con le scelte `Aggiorna ora` e `Più tardi`.

## 1.1.4 - 2026-08-11

- Aggiunte configurazioni personali nominate per la composizione delle prove da 40.
- Ogni utente può salvare, aggiornare, richiamare ed eliminare più configurazioni senza reinserire ogni volta le quantità.
- Le preferenze personali restano separate per account e sono comprese nel backup.
- Aggiunta durante le prove una panoramica orizzontale con 40 pallini numerati e cliccabili.
- I pallini mostrano subito domande risposte, non fatte e domanda attuale; nella prova guidata distinguono anche risposte corrette ed errate.
- Le domande tralasciate nella prova guidata possono essere riaperte e completate dalla panoramica.
- Alla domanda 40 il pulsante diventa `Consegna prova` e richiede conferma, indicando anche quante risposte mancano.

## 1.1.3 - 2026-08-11

- Aggiunto un cronometro grande e sempre visibile nelle simulazioni e nelle prove guidate da 40 domande.
- Il conto alla rovescia parte da 40:00 e conclude automaticamente la prova a 00:00.
- Le domande non completate allo scadere vengono registrate come non risposte e incluse nel riepilogo finale.
- Il tempo è calcolato sull'orario reale: continua correttamente anche se la pagina resta in secondo piano.
- La prova attiva viene salvata per il singolo utente e riprende con il tempo corretto dopo un aggiornamento della pagina.
- Negli ultimi cinque minuti e nell'ultimo minuto il cronometro cambia colore per rendere evidente la scadenza.

## 1.1.2 - 2026-08-09

- Aggiunto il pulsante `Aggiorna ora` direttamente nell'avviso dell'app.
- L'aggiornamento crea il backup, installa la release, riavvia il server locale e ricarica automaticamente la pagina.
- Il controllo aggiornamenti è ora visibile a ogni login, anche quando l'app è già aggiornata o la rete non è disponibile.
- Aggiunta la verifica SHA-256 del pacchetto scaricato da GitHub.
- Spostata la gestione degli utenti dentro Impostazioni.
- Ogni account mostra un riepilogo del proprio percorso separato: domande svolte, conosciute e simulazioni.
- Confermata la separazione per utente di progressi, statistiche, storico, rotazioni e classificazione dei quesiti.

## 1.1.1 - 2026-08-09

- Le nuove prove sono mescolate usando data e ora correnti, utente e contatore progressivo.
- Aggiunta una rotazione persistente per simulazioni, prove guidate da 40 e quiz guidati per materia.
- Le domande già estratte non vengono riproposte nella stessa modalità finché la materia non completa il proprio ciclo.
- La rotazione continua anche dopo la chiusura dell'app.
- Aggiunto l'aggiornamento con doppio clic per Windows e macOS.
- L'app controlla automaticamente le nuove versioni a ogni accesso e offre anche il controllo manuale.
- Prima di ogni aggiornamento viene creato un backup automatico dello stato.
- La cartella `portable-data` non viene mai sostituita dal programma di aggiornamento.

## 1.1.0 - 2026-08-09

- Aggiunto il punteggio finale alla prova guidata, ai quiz e alla simulazione.
- Aggiunto il calcolo visibile: +1 corretta, -0,33 errata, 0 non risposta.
- Nuovo riepilogo finale diviso in risposte errate, non risposte e corrette.
- Mostrate risposta scelta, soluzione esatta e spiegazione per ogni quesito.
- Corrette codifica, accenti, tag HTML, paragrafi ed elenchi delle spiegazioni.
- Migliorata la leggibilità delle spiegazioni su telefono, tablet e desktop.
- Corretto il pulsante per iniziare una nuova prova dalla schermata dei risultati.
- Confermati configuratore delle prove da 40, backup/ripristino e pulsante Chiudi app.

## 1.0.0 - 2026-08-07

- Prima versione portatile di Quiz 400 VVF 2026.
- Quiz ordinati per materia e simulazione 40/40.
- Account amministratore e utenti, progressi e statistiche locali.
- Avvio Windows/macOS e persistenza nella cartella portatile.
