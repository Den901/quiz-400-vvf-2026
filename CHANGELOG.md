# Changelog

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
