# Installazione Linux Cloud — Quiz 400 VVF 2026

Questa modalità pubblica usa tre servizi isolati:

- **app**: portale e API FastAPI;
- **database**: PostgreSQL per account, progressi, sessioni e impostazioni;
- **caddy**: accesso web, compressione e HTTPS automatico.

La versione portatile Windows/macOS continua a funzionare separatamente.

## Requisiti

- server Ubuntu 24.04 o Debian 12 a 64 bit;
- accesso `sudo`;
- porte TCP 80 e 443 raggiungibili da Internet;
- inoltro delle porte 80/443 sul router se il server è in una rete domestica;
- per DuckDNS, un sottodominio e il token del proprio account.

## Installazione

Dalla cartella del progetto:

```bash
chmod +x cloud/install-linux.sh cloud/update-linux.sh cloud/backup-linux.sh
sudo ./cloud/install-linux.sh
```

Lo script:

1. installa Docker su Debian/Ubuntu se manca;
2. chiede l'account del primo amministratore;
3. genera segreti casuali per database e cifratura;
4. crea `cloud/.env` con permessi riservati;
5. costruisce e avvia i container.

Apri inizialmente `http://IP-DEL-SERVER` e accedi come amministratore.

## Configurare DuckDNS e HTTPS

Nel portale apri **Impostazioni > Impostazioni Cloud** e compila:

- **Dominio**: per esempio `mioquiz` oppure `mioquiz.duckdns.org`;
- **Token DuckDNS**;
- **URL pubblico**: `https://mioquiz.duckdns.org`;
- intervallo di aggiornamento, minimo 5 minuti;
- spunta **Aggiornamento DuckDNS attivo**.

Salva e usa **Prova DuckDNS**. Il token viene cifrato nel database e non viene mai rimandato al browser. DuckDNS può rilevare automaticamente l'IPv4 pubblica quando il parametro IP è vuoto, come previsto dalla [specifica ufficiale DuckDNS](https://www.duckdns.org/spec.jsp).

Caddy accetta certificati HTTPS soltanto per il dominio salvato dall'admin. Dopo la propagazione DNS, la prima visita a `https://...` ottiene automaticamente il certificato. Il meccanismo usa l'endpoint di autorizzazione richiesto dalla documentazione [On-Demand TLS di Caddy](https://caddyserver.com/docs/caddyfile/options#on-demand-tls).

## Registrazioni e recupero password

L'admin può:

- aprire o chiudere la registrazione pubblica;
- impostare durata delle sessioni e scadenza dei link di recupero;
- configurare SMTP, mittente e STARTTLS;
- inviare un'email di prova al proprio indirizzo;
- generare una password temporanea se la posta non è configurata.

Il link di recupero è monouso. Un reset invalida le sessioni precedenti e obbliga l'utente che riceve una password temporanea a cambiarla al primo accesso.

## Gestione utenti e statistiche

In **Impostazioni > Utenti e statistiche** l'admin può:

- creare utenti o altri amministratori;
- disattivare e riattivare account;
- eliminare definitivamente un account e il suo percorso;
- generare una password temporanea;
- vedere domande svolte, conosciute, da ripetere e non conosciute;
- vedere simulazioni, punteggio medio/migliore, dettaglio per materia e ultime sessioni.

Il sistema impedisce di disattivare o eliminare il proprio account e garantisce che resti almeno un amministratore attivo.

## Backup

### Dal portale

**Scarica backup** esporta account, hash password, progressi e impostazioni. Il file è sensibile: conservalo cifrato e non inviarlo tramite canali pubblici.

### Dal server

```bash
sudo ./cloud/backup-linux.sh
```

Il dump PostgreSQL viene salvato in `cloud/backups`. I file più vecchi di 30 giorni vengono eliminati. È consigliato copiare i dump anche su uno spazio esterno cifrato.

## Aggiornamento

```bash
sudo ./cloud/update-linux.sh
```

Lo script crea prima un dump, scarica gli aggiornamenti, applica le migrazioni del database e ricostruisce i container senza eliminare i volumi.

## Comandi utili

```bash
docker compose --env-file cloud/.env -f cloud/compose.yml ps
docker compose --env-file cloud/.env -f cloud/compose.yml logs -f app
docker compose --env-file cloud/.env -f cloud/compose.yml restart
```

## Sicurezza operativa

- non pubblicare `cloud/.env` né i backup;
- abilita nel firewall solo SSH, 80/TCP, 443/TCP e 443/UDP;
- non esporre direttamente PostgreSQL o la porta 8000;
- usa una password admin unica e lunga;
- configura SMTP e un'email valida per ogni account;
- installa regolarmente gli aggiornamenti del sistema operativo;
- prima di aprire il portale al pubblico prepara informativa privacy, tempi di conservazione e contatto del titolare.

Le sessioni usano cookie `HttpOnly`, `SameSite=Lax` e `Secure` sotto HTTPS. Le password sono trattate con Argon2; token di sessione e recupero vengono conservati solo sotto forma di hash. Token DuckDNS e password SMTP sono cifrati usando `APP_SECRET`.
