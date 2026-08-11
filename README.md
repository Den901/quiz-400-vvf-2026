# Quiz 400 VVF 2026

Applicazione portatile e PWA installabile per esercitarsi sui quiz del concorso Vigili del Fuoco. Funziona su Windows e macOS, si adatta a telefono, tablet e desktop e conserva utenti, progressi, configurazione e statistiche nella cartella dell'app.

## Avvio rapido

1. Estrai completamente il file ZIP in una cartella normale.
2. Su Windows fai doppio clic su `Avvia-Quiz-400-VVF-2026-Windows.bat`.
3. Su macOS fai doppio clic su `Avvia-Quiz-400-VVF-2026-macOS.command`.
4. Lascia aperta la finestra di avvio mentre usi l'app.

Per terminare correttamente usa il pulsante **Chiudi app** nell'intestazione: spegne il server locale e conferma che i dati sono stati salvati. Se il browser impedisce la chiusura automatica della scheda, puoi chiuderla manualmente dopo il messaggio finale.

Quiz 400 VVF 2026 si apre automaticamente nel browser all'indirizzo locale `http://127.0.0.1:4190/`.

Se Python 3 non è presente, l'avviatore chiede il consenso prima di scaricare e installare la versione ufficiale. Windows usa Winget quando disponibile; macOS richiede la password di amministratore.

## Primo accesso

Al primo avvio viene chiesto di creare l'amministratore principale. L'amministratore può:

- creare utenti e altri amministratori;
- disattivare o riattivare gli account;
- importare dataset autorizzati;
- utilizzare tutte le modalità di studio e simulazione.

Conserva con cura nome utente e password: non esiste un servizio online per recuperarli.

## Modalità di studio

### Percorso per argomento

Le domande sono presentate nell'ordine originale. Puoi interrompere la sessione e riprendere dalla prima domanda non ancora svolta. Ogni quesito viene classificato come:

- **La so**;
- **Da ripetere**;
- **Non la so**;
- **Non risposta**.

### Prova guidata da 40 domande

Usa la stessa composizione della simulazione ufficiale. Dopo ogni risposta mostra subito esito, soluzione corretta e spiegazione. I pulsanti **Indietro** e **Continua** sono disponibili sia sopra sia sotto la spiegazione. Alla fine mostra punteggio, calcolo applicato e correzione completa.

Composizione: 8 Storia, 11 Logica, 1 Insiemi, 6 Fisica, 6 Chimica, 4 Informatica e 4 Inglese.

Per alcuni quesiti di Insiemi la fonte non fornisce una spiegazione testuale: vengono comunque mostrati diagramma e soluzione corretta.

### Configurazione delle prove da 40

Un amministratore può aprire **Amministrazione > Impostazioni prove da 40** oppure usare **Modifica composizione** nella pagina Simulazione. Per ogni materia può impostare da 0 a 40 domande: inserendo 0 la materia viene esclusa. Il totale deve restare esattamente 40. La configurazione viene applicata sia alla prova guidata sia alla simulazione a tempo e viene salvata nella cartella portatile.

Il pulsante **Ripristina predefinita** riporta la composizione a 8 Storia, 11 Logica, 1 Insiemi, 6 Fisica, 6 Chimica, 4 Informatica e 4 Inglese.

### Simulazione a tempo

- 40 domande in 40 minuti;
- cronometro grande e sempre visibile, da 40:00 a 00:00;
- consegna automatica allo scadere, con i quesiti rimanenti conteggiati come non risposti;
- ripresa della prova e del tempo effettivamente rimasto dopo un aggiornamento della pagina;
- estrazione basata su data e ora correnti, diversa a ogni nuova prova;
- rotazione persistente che evita di riproporre le domande già estratte finché la materia non completa il proprio ciclo;
- +1 punto per ogni risposta corretta;
- -0,33 punti per ogni risposta errata;
- 0 punti per ogni risposta non data;
- navigazione avanti e indietro;
- correzione completa alla fine, con risposte corrette, errate e non date.

Anche la prova guidata da 40 domande usa lo stesso cronometro di 40 minuti e termina automaticamente allo scadere. I quiz guidati per singola materia da 15, 30 o 50 domande restano invece senza limite di tempo.

Il risultato finale di entrambe le prove mostra il punteggio in evidenza e tre sezioni consultabili: **Risposte errate**, **Non risposte** e **Risposte corrette**. Ogni scheda riporta risposta scelta, soluzione esatta e spiegazione disponibile.

Le spiegazioni vengono presentate con paragrafi, elenchi, accenti e simboli ripuliti. Per i quesiti per i quali la fonte non fornisce una spiegazione testuale, l'app indica chiaramente che non è disponibile.

## Progressi e ripasso

La pagina Progressi mostra quante domande sono state svolte e la situazione per materia. I filtri permettono di esercitarsi solo sulle domande da ripetere, non conosciute o mai risposte. Lo storico conserva i risultati delle ultime simulazioni.

La rotazione dei quesiti viene salvata nel profilo. Una prova da 40 in corso viene salvata separatamente per ogni utente: ricaricando la pagina si ritrovano domanda, risposte e tempo effettivamente rimasto. Una volta conclusa, la successiva estrazione prosegue con domande nuove. Il percorso completo per argomento resta invece intenzionalmente nell'ordine originale.

## Dove vengono salvati i dati

La versione portatile salva automaticamente tutto, comprese le impostazioni delle prove, in:

`portable-data/fuocoquiz-state.json`

Il file contiene account, password sotto forma di hash, progressi, statistiche e dataset aggiuntivi importati. Non contiene password in chiaro.

Per trasferire o fare un backup, usa **Chiudi app** e copia l'intera cartella. Non rinominare o modificare manualmente il file JSON. Se elimini la cartella `portable-data`, perdi gli account e i progressi locali.

### Backup dall'app

Un amministratore può aprire **Impostazioni prove > Backup e ripristino**:

- **Scarica backup** crea un file JSON contenente utenti, progressi, statistiche, composizione delle prove e dataset importati;
- **Ripristina backup** controlla il file e chiede conferma prima di sostituire tutti i dati attuali;
- dopo il ripristino l'app viene ricaricata automaticamente.

Conserva i backup in un luogo protetto: pur non contenendo password in chiaro, includono account e dati di studio.

## Aggiornare senza perdere i dati

Chiudi la prova in corso, quindi usa il file adatto al computer:

- Windows: doppio clic su `Aggiorna-Quiz-400-VVF-2026-Windows.bat`;
- macOS: doppio clic su `Aggiorna-Quiz-400-VVF-2026-macOS.command`.

Il programma controlla l'ultima release pubblicata su GitHub, arresta in sicurezza l'eventuale app locale ancora aperta, crea un backup automatico e installa i nuovi file. La cartella `portable-data` viene esclusa dall'aggiornamento: account, password sotto forma di hash, progressi, statistiche, rotazione dei quiz e impostazioni restano conservati.

Prima dell'installazione viene creata una copia in `portable-data/backups`; sono mantenuti automaticamente gli ultimi dieci backup. Al termine riavvia l'app con il normale file di avvio.

A ogni accesso l'app controlla automaticamente se esiste una release più recente. Il pulsante **Aggiornamenti** nell'intestazione permette di ripetere il controllo manualmente. Se non c'è connessione, i quiz e i dati locali continuano a funzionare normalmente.

Quando trova una nuova versione, l'avviso contiene **Aggiorna ora**: l'app crea il backup, scarica e verifica il pacchetto, installa la release, riavvia il server locale e ricarica automaticamente la pagina. I file esterni con doppio clic restano disponibili come procedura alternativa.

## Utenti e percorsi personali

La gestione degli account si trova in **Impostazioni > Utenti e statistiche**. Da questa sezione l'amministratore crea, disattiva e riattiva gli utenti e vede un riepilogo delle attività.

Ogni account conserva in modo indipendente domande svolte, stato “La so / Da ripetere / Non la so”, quiz non risposti, rotazioni, punteggi e storico delle simulazioni. Quando un utente accede vede soltanto il proprio percorso e le proprie statistiche.

Non estrarre manualmente un nuovo ZIP sopra una vecchia installazione: usa il file **Aggiorna** oppure fai prima un backup dall'app.

## Installazione come app

Dal browser puoi scegliere **Installa app** per aggiungere Quiz 400 VVF 2026 alla schermata iniziale o al desktop. Perché il salvataggio portatile continui a funzionare, avvia sempre prima l'app con il file Windows o macOS e lascia aperta la finestra del server locale.

## Risoluzione dei problemi

- **La pagina non si apre:** verifica che la finestra di avvio sia ancora aperta e visita `http://127.0.0.1:4190/`.
- **La porta è occupata:** chiudi eventuali altre copie dell'app e riavvia.
- **macOS blocca il file:** fai clic destro su `Avvia-Quiz-400-VVF-2026-macOS.command`, scegli **Apri** e conferma. Se necessario esegui `chmod +x Avvia-Quiz-400-VVF-2026-macOS.command` nel Terminale.
- **Windows mostra un avviso:** verifica che il pacchetto provenga dalla fonte da cui lo hai ricevuto, quindi scegli l'opzione per eseguirlo.
- **I progressi non compaiono:** controlla di aver avviato la stessa cartella e di non aver eliminato `portable-data`.

## Dataset e uso autorizzato

Il pacchetto include 11.070 quesiti e 274 diagrammi. La sessione Chrome e le credenziali Mininterno non sono incluse né esportate. Prima di distribuire pubblicamente l'app o la banca dati, conserva la prova dell'autorizzazione e verifica che copra riproduzione e distribuzione dei contenuti.

## Nota di sicurezza

Questa versione è pensata per uso locale e portatile. Il server ascolta soltanto sul computer (`127.0.0.1`) e non espone l'app alla rete. Per un servizio pubblico multiutente servono un backend protetto, database, recupero password, backup centralizzati e informativa privacy.

Consulta anche `Guida-Quiz-400-VVF-2026.pdf` per la guida completa impaginata.
