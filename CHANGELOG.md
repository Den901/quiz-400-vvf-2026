# Changelog

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
- La PWA usa ora la rete locale prima della cache e mantiene la cache come riserva offline, evitando file vecchi dopo gli aggiornamenti.
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
