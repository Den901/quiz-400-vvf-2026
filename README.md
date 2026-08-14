# Quiz 400 VVF 2026

La versione cloud include un'informativa privacy pubblica configurabile dall'amministratore, la registrazione della presa visione e l'esportazione dei dati personali dell'utente.

Portale web amatoriale e gratuito per esercitarsi sui quiz del concorso Vigili del Fuoco. È una PWA installabile da browser su telefono, tablet e computer, ma viene gestita centralmente da un server Linux o Windows.

Il progetto non rappresenta, non è affiliato e non è approvato dal Ministero dell’Interno, dal Corpo Nazionale dei Vigili del Fuoco o da altri enti del concorso.

## Distribuzione supportata

Dalla versione 2.2.0 viene mantenuta una sola linea software:

- portale server Docker per Linux e Windows;
- database PostgreSQL centralizzato;
- accesso pubblico HTTPS, anche dietro reverse proxy esistente;
- PWA per iPhone, iPad, Android, tablet e desktop;
- pacchetto di aggiornamento unico `Quiz-400-VVF-2026-Server.zip`.

Non vengono più create nuove versioni EXE o nuove release standalone. Gli eventuali file EXE presenti nelle vecchie release restano soltanto come archivio storico e non ricevono aggiornamenti.

## Funzioni principali

- quiz per materia in ordine, con ripresa dalle domande non ancora fatte;
- classificazione personale: **Le so**, **Da ripetere**, **Non le so**, **Da fare**;
- errore inserito automaticamente tra le domande da ripetere;
- prova guidata con risposta corretta e spiegazione a tendina;
- simulazione ufficiale di 40 domande in 40 minuti;
- punteggio `+1` corretta, `-0,33` errata, `0` non risposta;
- composizione predefinita: 8 storia, 12 logica (di cui 1 insiemi), 6 fisica, 6 chimica, 4 informatica, 4 inglese;
- composizioni personalizzate salvate separatamente per ogni utente;
- panoramica delle 40 domande e navigazione avanti/indietro;
- consegna manuale con conferma e consegna automatica a tempo scaduto;
- riepilogo finale con giuste, sbagliate, non risposte, punteggio e spiegazioni;
- revisione dettagliata degli ultimi cinque quiz;
- statistiche globali, per materia e per tipo di prova;
- suggerimenti di esercitazione sulle materie più deboli;
- ripasso adattivo “Deep learning” senza servizi di intelligenza artificiale esterni;
- tema chiaro, scuro o automatico;
- logo configurabile dall’amministratore;
- registrazione, recupero password via email e gestione utenti;
- preferenze, progressi e statistiche isolati per account.

## Pannello amministratore

La voce **Admin** contiene:

- impostazioni generali, DuckDNS, SMTP, porte e reverse proxy;
- utenti e statistiche centralizzate;
- backup e ripristino applicativo;
- logo e composizione predefinita delle prove;
- centro aggiornamenti del portale;
- riavvio e spegnimento del solo portale.

La versione installata è visibile nell’intestazione e nel centro aggiornamenti.

## Aggiornamenti cloud

Il portale controlla automaticamente GitHub quando accede un amministratore e ogni 15 minuti durante l’uso. Nel centro aggiornamenti è possibile:

1. premere **Cerca aggiornamenti**;
2. vedere versione installata e versione disponibile;
3. leggere il changelog completo prima dell’installazione;
4. installare la release server pubblicata su GitHub;
5. caricare manualmente lo stesso file ZIP e installarlo.

Un pacchetto manuale viene accettato solo se contiene il manifest server, una versione valida e l’elenco verificabile dei file. Prima dell’installazione il controllo esterno al portale crea:

- un dump PostgreSQL;
- una copia dei file applicativi correnti.

Se il nuovo portale non torna disponibile, i file precedenti vengono ripristinati. Il volume PostgreSQL, `cloud/.env`, backup e file di controllo non sono inclusi né sostituiti dal pacchetto.

## Installazione Linux

Requisiti per l’installazione automatica: Ubuntu o Debian con accesso amministratore. Docker viene installato dallo script se manca.

```bash
sudo ./cloud/install-linux.sh
```

Con reverse proxy già esistente, lascia pubblica la porta 443 sul proxy e inoltra internamente verso la porta backend scelta. Il backend dovrebbe ascoltare su `127.0.0.1` quando il proxy gira sulla stessa macchina.

Per un’installazione già esistente:

```bash
sudo ./cloud/install-server-control.sh
```

Guida completa: [cloud/README-LINUX.md](cloud/README-LINUX.md).

## Installazione Windows Server

Requisiti: Windows 10/11 o Windows Server con Docker Desktop/Engine e Docker Compose disponibili. Aprire PowerShell come amministratore:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\cloud\install-windows.ps1
```

Lo script crea PostgreSQL, avvia il portale e registra il controllo aggiornamenti all’avvio di Windows. Il backend ascolta sulla prima porta libera da 8088 in poi; il reverse proxy HTTPS può pubblicarlo sulla 443.

Guida completa: [cloud/README-WINDOWS.md](cloud/README-WINDOWS.md).

## Avvio dopo uno spegnimento dal pannello

Lo spegnimento agisce soltanto sul container del portale. PostgreSQL, sistema operativo e altri servizi restano accesi.

Linux:

```bash
sudo ./cloud/start-linux.sh
```

Windows PowerShell:

```powershell
.\cloud\start-windows.ps1
```

## Backup

Dal pannello Admin è possibile esportare e ripristinare account, impostazioni, progressi e statistiche. Per un backup PostgreSQL completo:

Linux:

```bash
sudo ./cloud/backup-linux.sh
```

Windows PowerShell:

```powershell
.\cloud\backup-windows.ps1
```

I dump vengono conservati in `cloud/backups`, esclusa dal repository e dai pacchetti di aggiornamento.

## Creazione di una release server

```powershell
python .\cloud\build-server-release.py
```

Il file risultante è `outputs/Quiz-400-VVF-2026-Server.zip`. Il costruttore esclude automaticamente credenziali, database, backup, directory di controllo, dati portatili ed eseguibili.

## Sicurezza e dati

- password utente: hash Argon2;
- cookie di sessione: `HttpOnly`, `Secure` su HTTPS e `SameSite=Lax`;
- token SMTP e DuckDNS: cifrati con la chiave del server;
- operazioni di aggiornamento, riavvio e spegnimento: disponibili soltanto agli amministratori e inoltrate a un controllo host separato;
- richieste di spegnimento e riavvio: conferma obbligatoria anche sul backend;
- dati persistenti: volume PostgreSQL separato dal codice e dai pacchetti.

Prima di aprire il portale al pubblico occorre predisporre una propria informativa privacy e verificare di avere titolo per usare e distribuire banca dati, spiegazioni, immagini e marchi.
