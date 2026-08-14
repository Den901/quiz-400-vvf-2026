# Verifica tecnica e legale preliminare

## Privacy e protezione dei dati

La versione cloud presenta un'informativa estesa prima della registrazione, registra la sola presa visione del testo vigente e permette all'utente di esportare i dati che lo riguardano. Il portale non usa cookie pubblicitari o strumenti di profilazione commerciale. Gli amministratori devono mantenere aggiornati dal pannello i dati del titolare, i fornitori effettivi, l'ubicazione del server, gli eventuali trasferimenti internazionali e i tempi di conservazione.

Il testo è una base tecnica aderente alla struttura dell'articolo 13 GDPR, ma la conformità dipende anche dall'organizzazione concreta del titolare, dai contratti con i fornitori, dalle misure di sicurezza, dalla gestione delle richieste e dall'aggiornamento del registro dei trattamenti quando applicabile.

Data della verifica: 7 agosto 2026. Questa è una valutazione progettuale, non un parere legale.

## Cosa è stato osservato

La pagina del concorso `idc=1459`, visualizzata con la sessione Chrome già autenticata senza accedere a cookie o credenziali, espone 11.070 quesiti suddivisi in: Chimica (1.677), Fisica (2.004), Informatica (2.119), Lingua inglese (1.551), Logica (1.707), Logica/Brani (648), Logica/Insiemi (274), Storia (1.090). Sono presenti modalità Trainer e Questionario, ordine casuale/originale e PDF per materia.

La modalità Trainer presenta una domanda alla volta, tre risposte, correzione immediata e possibilità di saltare. Questa osservazione serve a progettare il flusso, non a riprodurre il codice o il dataset del sito.

## Valutazione

- **Login:** una PWA indipendente non può e non deve riusare la sessione Mininterno. Cookie `HttpOnly`, same-origin e CORS impediscono un'integrazione client legittima; aggirarli o esportare credenziali sarebbe insicuro.
- **Scraping:** la consultazione manuale consentita dall'account non autorizza automaticamente estrazione e reimpiego sistematici. Una banca dati può essere protetta nella selezione/struttura e dal diritto *sui generis*; estrazioni ripetute possono essere problematiche anche se i singoli quesiti derivano da una fonte pubblica.
- **PDF/download:** la presenza di una funzione di download per uso sul sito non prova una licenza di redistribuzione in una nuova app. Le condizioni trovate riguardano espressamente il software e ne limitano l'uso alla persona; non è stata individuata una licenza aperta per l'intera banca dati web.
- **Dati pubblici:** se la banca dati ufficiale è pubblicata direttamente dall'amministrazione con licenza/condizioni di riutilizzo, si può importare da quella fonte rispettandone attribuzione, integrità e aggiornamenti. Il d.lgs. 36/2006 disciplina il riutilizzo dei documenti pubblici, ma non trasforma automaticamente una raccolta privata di Mininterno in open data.

## Percorso consigliato

1. Cercare sul portale ufficiale del Corpo/Ministero il file della banca dati e la relativa licenza o condizioni di riutilizzo.
2. In assenza di licenza chiara, chiedere autorizzazione scritta al titolare del dataset o un feed/API/licenza a Mininterno/Edena.
3. Conservare prova della provenienza, versione, hash e licenza di ogni pacchetto importato.
4. Distribuire nel frattempo solo app, schema import e contenuti originali/liberamente licenziati.

## Decisione realizzativa

In seguito alla dichiarazione dell'utente di essere autorizzato a creare l'app e usare i contenuti per lo studio, è stato acquisito il dataset completo (11.070 quesiti) tramite i canali di generazione/download esposti dal sito. La sessione Chrome è stata usata soltanto per accedere alle pagine e generare i documenti: cookie e credenziali non sono stati letti né esportati. Prima di una pubblicazione a terzi è prudente conservare prova che l'autorizzazione copra anche riproduzione e distribuzione, non soltanto uso personale.
