# Installazione Linux Cloud — Quiz 400 VVF 2026

Questa modalità pubblica usa servizi isolati:

- **app**: portale e API FastAPI;
- **database**: PostgreSQL per account, progressi, sessioni e impostazioni;
- **caddy opzionale**: proxy e HTTPS automatico soltanto quando non esiste già un reverse proxy.

La versione portatile Windows/macOS continua a funzionare separatamente.

## Requisiti

- server Ubuntu 24.04 o Debian 12 a 64 bit;
- accesso `sudo`;
- un reverse proxy HTTPS esistente sulla porta pubblica 443, oppure porte 80/443 disponibili per il proxy incluso;
- per DuckDNS, un sottodominio e il token del proprio account.

## Installazione

Installa Git se necessario, clona il progetto e avvia l'installatore:

```bash
sudo apt update && sudo apt install -y git
git clone https://github.com/Den901/quiz-400-vvf-2026.git
cd quiz-400-vvf-2026
chmod +x cloud/install-linux.sh cloud/configure-ports.sh cloud/update-linux.sh cloud/backup-linux.sh
sudo ./cloud/install-linux.sh
```

Lo script:

1. installa Docker Engine e Compose dal repository ufficiale Docker se mancano;
2. chiede l'account del primo amministratore;
3. rileva le porte già utilizzate e chiede se è presente un reverse proxy HTTPS;
4. genera segreti casuali per database e cifratura;
5. crea `cloud/.env` con permessi riservati;
6. costruisce e avvia i container necessari.

Se usi il proxy incluso, apri inizialmente l'indirizzo mostrato dall'installatore. Se usi un reverse proxy esistente, configura prima il dominio come descritto sotto.

## Reverse proxy esistente: HTTPS pubblico sempre su 443

Quando l'installatore chiede se usi già un reverse proxy, rispondi **sì**. L'app non occuperà le porte pubbliche 80/443: verrà esposta su una porta interna libera, normalmente `8088`, mentre il tuo reverse proxy continuerà a ricevere tutto su `https://tuodominio` porta 443.

Se il reverse proxy gira direttamente sul server, il backend predefinito è `http://127.0.0.1:8088`. Esempio Nginx:

```nginx
location / {
    proxy_pass http://127.0.0.1:8088;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

Esempio per un Caddy già esistente:

```caddy
quiz.tuodominio.it {
    reverse_proxy 127.0.0.1:8088
}
```

Se il reverse proxy gira in un container o su un'altra macchina, scegli questa opzione nell'installatore: il backend verrà collegato a `0.0.0.0:PORTA`. Non aprire quella porta su Internet; consentila nel firewall soltanto dall'indirizzo del reverse proxy. In Nginx Proxy Manager usa l'IP del server come Forward Host e la porta interna scelta come Forward Port.

Il reverse proxy deve trasmettere `Host`, `X-Forwarded-For` e `X-Forwarded-Proto=https`. In questo modo login, cookie `Secure`, link di recupero e protezioni HTTPS funzionano correttamente.

### Controllare o cambiare porta

```bash
sudo ./cloud/configure-ports.sh
```

Lo script mostra la modalità attuale, controlla se la nuova porta è occupata, ricrea soltanto i servizi interessati e ripristina automaticamente la configurazione precedente se il cambio non riesce. Le porte effettive sono visibili anche in **Impostazioni Cloud > Porte e HTTPS**.

## Configurare DuckDNS e HTTPS

Nel portale apri **Impostazioni > Impostazioni Cloud** e compila:

- **Dominio**: per esempio `mioquiz` oppure `mioquiz.duckdns.org`;
- **Token DuckDNS**;
- **URL pubblico**: `https://mioquiz.duckdns.org`;
- intervallo di aggiornamento, minimo 5 minuti;
- spunta **Aggiornamento DuckDNS attivo**.

Salva e usa **Prova DuckDNS**. Il token viene cifrato nel database e non viene mai rimandato al browser. DuckDNS può rilevare automaticamente l'IPv4 pubblica quando il parametro IP è vuoto, come previsto dalla [specifica ufficiale DuckDNS](https://www.duckdns.org/spec.jsp).

Con un reverse proxy esistente, certificato e porta 443 restano gestiti da quel proxy. Con il proxy incluso, Caddy accetta certificati HTTPS soltanto per il dominio salvato dall'admin. Dopo la propagazione DNS, la prima visita a `https://...` ottiene automaticamente il certificato. Il meccanismo usa l'endpoint di autorizzazione richiesto dalla documentazione [On-Demand TLS di Caddy](https://caddyserver.com/docs/caddyfile/options#on-demand-tls).

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
- abilita nel firewall pubblico solo SSH e le porte del reverse proxy; la porta interna dell'app non va esposta a Internet;
- non esporre direttamente PostgreSQL o la porta 8000;
- usa una password admin unica e lunga;
- configura SMTP e un'email valida per ogni account;
- installa regolarmente gli aggiornamenti del sistema operativo;
- prima di aprire il portale al pubblico prepara informativa privacy, tempi di conservazione e contatto del titolare.

Le sessioni usano cookie `HttpOnly`, `SameSite=Lax` e `Secure` sotto HTTPS. Le password sono trattate con Argon2; token di sessione e recupero vengono conservati solo sotto forma di hash. Token DuckDNS e password SMTP sono cifrati usando `APP_SECRET`.
