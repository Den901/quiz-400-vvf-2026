# Quiz 400 VVF 2026 — server Windows

## Requisiti

- Windows 10/11 oppure Windows Server;
- PowerShell avviato come amministratore;
- Docker Desktop o Docker Engine con `docker compose` funzionante;
- reverse proxy HTTPS, se il portale deve essere pubblico.

## Installazione

Estrarre il pacchetto server in una cartella stabile, per esempio `C:\Quiz400VVF`, quindi aprire PowerShell come amministratore:

```powershell
cd C:\Quiz400VVF
Set-ExecutionPolicy -Scope Process Bypass
.\cloud\install-windows.ps1
```

Lo script chiede l’account amministratore iniziale, sceglie la prima porta libera a partire da 8088, crea password casuali per PostgreSQL e la chiave applicativa, poi avvia i container.

Il file `cloud\.env` contiene segreti e non deve essere pubblicato, inviato o inserito in un backup non protetto.

## Reverse proxy e HTTPS

Per impostazione predefinita il backend Windows ascolta su `0.0.0.0:PORTA`. Configurare il reverse proxy affinché:

- riceva il traffico pubblico HTTPS sulla porta 443;
- inoltri al server Windows sulla porta indicata dall’installatore;
- invii gli header `Host`, `X-Forwarded-Host` e `X-Forwarded-Proto`.

Se il reverse proxy gira sulla stessa macchina, è consigliabile cambiare `APP_BIND_ADDRESS` in `127.0.0.1` dentro `cloud\.env` e ricreare il container app.

## Controllo aggiornamenti

L’installatore registra l’attività pianificata `Quiz400VVF-ServerControl`, eseguita come servizio di sistema. Il pannello Admin può quindi:

- cercare la release su GitHub;
- ricevere automaticamente la notifica;
- leggere il changelog;
- installare da GitHub o da ZIP caricato;
- riavviare o spegnere il solo portale.

Per verificare l’attività:

```powershell
Get-ScheduledTask -TaskName Quiz400VVF-ServerControl
```

## Backup

```powershell
.\cloud\backup-windows.ps1
```

I dump PostgreSQL vengono salvati in `cloud\backups` e conservati per 30 giorni. Il centro aggiornamenti esegue questo backup automaticamente prima di installare.

## Avvio manuale

Dopo **Spegni portale** dal pannello:

```powershell
.\cloud\start-windows.ps1
```

La macchina, PostgreSQL e gli altri servizi non vengono spenti dal pannello.

## Aggiornamento manuale di emergenza

Se il pannello non è raggiungibile, conservare `cloud\.env` e i volumi Docker, estrarre la nuova release sopra i soli file applicativi e avviare:

```powershell
docker compose --env-file .\cloud\.env -f .\cloud\compose.yml up -d --build
```

Non usare `docker compose down -v`: l’opzione `-v` elimina anche il volume PostgreSQL.
