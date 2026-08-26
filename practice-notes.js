// Schede costruite sui 30 sottoargomenti effettivamente usati dal dataset del portale.
const note = (term, definition, formula = '', tip = '') => ({term, definition, formula, tip});

export const computerScienceNotes = [
  {
    id:'informatica-hardware', title:'Hardware, componenti e periferiche', quizCount:274,
    summary:'CPU, memorie, archiviazione, porte e dispositivi di ingresso o uscita.',
    items:[
      note('Hardware e software','Hardware è la parte fisica del computer; software è l’insieme di programmi e istruzioni che la fanno funzionare.'),
      note('CPU','Esegue istruzioni e operazioni logico-aritmetiche e coordina gli altri componenti. Comprende unità di controllo, unità aritmetico-logica e registri.'),
      note('RAM, ROM e cache','La RAM è veloce, riscrivibile e volatile; la ROM conserva istruzioni non volatili; la cache è memoria molto rapida vicina alla CPU.','RAM = lavoro temporaneo · ROM = stabile · cache = accesso rapido'),
      note('Memorie di massa','HDD usa dischi magnetici; SSD usa memoria elettronica ed è normalmente più veloce; chiavette USB e schede di memoria sono rimovibili.'),
      note('Bit, byte e capacità','Un bit vale 0 oppure 1; un byte contiene 8 bit. Nei quiz tradizionali si usa spesso 1 KB = 1024 B, 1 MB = 1024 KB e 1 GB = 1024 MB.','1 byte = 8 bit','Nel Sistema Internazionale kB, MB e GB sono potenze di 1000; le potenze di 1024 sono KiB, MiB e GiB. Nei quesiti controlla la convenzione usata.'),
      note('Periferiche di input','Tastiera, mouse, scanner, microfono e webcam inviano dati al computer. Lo scanner digitalizza un documento cartaceo.'),
      note('Periferiche di output','Monitor, stampante, plotter e altoparlanti restituiscono informazioni. Un touchscreen è sia input sia output.'),
      note('Scheda madre e schede dedicate','La scheda madre collega CPU, RAM, memorie e periferiche. La scheda video elabora la grafica; la scheda di rete collega il dispositivo alla rete.'),
      note('Pixel e risoluzione','Il pixel è il più piccolo elemento indirizzabile di un’immagine digitale o di uno schermo. La risoluzione indica normalmente il numero di pixel orizzontali × verticali.'),
      note('BIOS e UEFI','Inizializzano l’hardware all’avvio e passano il controllo al sistema operativo. UEFI è il successore moderno del BIOS tradizionale.')
    ]
  },
  {
    id:'informatica-sistemi-file', title:'Sistemi operativi, file e cartelle', quizCount:318,
    summary:'Interfaccia, processi, estensioni, archivi compressi e gestione delle risorse.',
    items:[
      note('Sistema operativo','Gestisce hardware, memoria, processi, file, periferiche e interfaccia utente. Windows, Linux, macOS, Android e iOS sono sistemi operativi.'),
      note('File, cartella e percorso','Un file contiene dati; una cartella organizza file e altre cartelle; il percorso indica la posizione della risorsa nel file system.'),
      note('Estensione','La parte finale dopo il punto suggerisce il formato e il programma associato: .txt testo, .jpg immagine, .pdf documento, .zip archivio compresso.','nomefile.estensione'),
      note('Compressione','Riduce lo spazio occupato raccogliendo uno o più file in un archivio. La decompressione ricrea file e cartelle utilizzabili; ZIP è un formato comune.'),
      note('Processo e multitasking','Un processo è un programma in esecuzione. Il multitasking permette al sistema operativo di gestire più processi alternando le risorse.'),
      note('Memoria virtuale','Usa una parte dell’archiviazione come supporto alla RAM. È utile quando la RAM non basta, ma è più lenta della memoria fisica.'),
      note('Appunti di sistema','Copia conserva l’originale; taglia prepara lo spostamento; incolla inserisce il contenuto memorizzato negli appunti.'),
      note('Cestino ed eliminazione','Normalmente un file eliminato passa nel Cestino e può essere ripristinato finché non viene rimosso definitivamente.'),
      note('Formattazione e partizione','La partizione divide logicamente un disco; la formattazione prepara un file system e può rendere inaccessibili i dati precedenti.'),
      note('Scorciatoie ricorrenti','Ctrl+C copia, Ctrl+X taglia, Ctrl+V incolla, Ctrl+Z annulla, Ctrl+A seleziona tutto, Alt+Tab cambia finestra.','Ctrl+C · Ctrl+X · Ctrl+V · Ctrl+Z')
    ]
  },
  {
    id:'informatica-word', title:'Word ed elaborazione testi', quizCount:258,
    summary:'Formattazione, stili, impaginazione, stampa unione e formati dei documenti.',
    items:[
      note('Carattere e paragrafo','Tipo, dimensione, grassetto, corsivo, apice e pedice riguardano il carattere; allineamento, rientri e interlinea riguardano il paragrafo.'),
      note('Allineamenti','Sinistra allinea il margine sinistro; centrato dispone il testo al centro; destra allinea il margine destro; giustificato allinea entrambi i margini.'),
      note('Stili e sommario','Gli stili Titolo organizzano la struttura del documento e permettono di generare automaticamente il sommario.'),
      note('Intestazione e piè di pagina','Sono aree ripetute nella parte superiore o inferiore delle pagine; possono contenere titolo, data e numero di pagina.'),
      note('Stampa unione','Combina un documento principale con una lista di destinatari per creare lettere, etichette o messaggi personalizzati.'),
      note('Trova e sostituisci','Trova individua testo o formattazione; Sostituisci modifica tutte o alcune occorrenze in modo controllato.'),
      note('Formati frequenti','.doc e .docx sono documenti Word; .rtf conserva una formattazione compatibile; .txt contiene testo semplice; PDF privilegia la distribuzione e l’aspetto stabile.'),
      note('Selezioni e tasti','Ctrl+A seleziona tutto; Ctrl+Maiusc+Fine seleziona dal cursore alla fine; Ctrl+S salva; Ctrl+P apre la stampa.','Ctrl+A · Ctrl+Maiusc+Fine · Ctrl+S · Ctrl+P'),
      note('Protezione del documento','Una password di apertura limita la lettura; una protezione o password di modifica può consentire la lettura impedendo modifiche non autorizzate.'),
      note('Orientamento e margini','Orientamento verticale o orizzontale, dimensione pagina e margini appartengono all’impostazione della pagina, non alla formattazione del carattere.')
    ]
  },
  {
    id:'informatica-excel', title:'Excel e fogli di calcolo', quizCount:214,
    summary:'Celle, formule, riferimenti, funzioni, grafici, filtri e tabelle pivot.',
    items:[
      note('Cartella, foglio e cella','Il file Excel è una cartella di lavoro composta da fogli. Una cella è identificata da lettera della colonna e numero della riga, per esempio A3.'),
      note('Formula','Una formula inizia con = e può usare numeri, operatori, funzioni e riferimenti ad altre celle.','=A1+B1'),
      note('Riferimento relativo','Cambia quando la formula viene copiata in un’altra posizione.','A1'),
      note('Riferimento assoluto','Resta fisso quando la formula viene copiata; il simbolo $ blocca colonna e riga.','$A$1','A$1 blocca solo la riga; $A1 blocca solo la colonna.'),
      note('Operatori','+ somma, - sottrazione, * moltiplicazione, / divisione, ^ potenza; nei confronti si usano =, >, <, >=, <= e <>.'),
      note('Funzioni comuni','SOMMA totalizza, MEDIA calcola la media aritmetica, MIN e MAX cercano gli estremi, CONTA.NUMERI conta le celle numeriche, SE valuta una condizione.','=SOMMA(A1:A10)'),
      note('Testo, numero e data','Un valore che non è riconosciuto come numero o data e non inizia con = viene normalmente trattato come testo.'),
      note('Ordinamento e filtro','Ordinare cambia l’ordine delle righe; filtrare mostra soltanto quelle che rispettano i criteri senza cancellare le altre.'),
      note('Grafico','Rappresenta visivamente dati selezionati. Prima si seleziona l’intervallo coerente, poi si sceglie il tipo di grafico adatto.'),
      note('Tabella pivot','Raggruppa e riepiloga grandi insiemi di dati per categorie, somme, conteggi o altre aggregazioni senza cambiare i dati originali.')
    ]
  },
  {
    id:'informatica-office-dati', title:'Presentazioni, posta e basi di dati', quizCount:201,
    summary:'PowerPoint, email, campi dei destinatari e concetti fondamentali dei database.',
    items:[
      note('PowerPoint','Serve a creare presentazioni composte da diapositive. Layout organizza i segnaposto; transizione agisce tra diapositive; animazione agisce sugli oggetti.'),
      note('Indirizzo email','Nell’indirizzo nome@dominio, la parte prima di @ identifica la casella; quella dopo @ identifica il dominio del servizio.','utente@dominio'),
      note('A, Cc e Ccn','A contiene i destinatari principali; Cc invia una copia visibile; Ccn invia una copia nascondendo quell’indirizzo agli altri destinatari.'),
      note('Allegato e mailing list','Un allegato è un file inviato con il messaggio. Una mailing list distribuisce messaggi a un gruppo di iscritti.'),
      note('Protocolli di posta','SMTP invia la posta; IMAP sincronizza la casella mantenendo i messaggi sul server; POP3 scarica normalmente i messaggi sul client.','SMTP = invio · IMAP/POP3 = ricezione'),
      note('Database','È una raccolta strutturata di dati gestita da un DBMS. Nei database relazionali i dati sono organizzati in tabelle collegate.'),
      note('Campo, record e tabella','Un campo è una proprietà o colonna; un record è una riga completa; la tabella raccoglie record dello stesso tipo.'),
      note('Chiave primaria','Identifica in modo univoco ogni record di una tabella; una chiave esterna collega un record a un’altra tabella.'),
      note('Query','Interroga, filtra, ordina o combina dati secondo criteri. Non è necessariamente una copia dei dati.'),
      note('Access','Microsoft Access è un sistema per creare e gestire database, maschere, query e report; non è un foglio di calcolo.')
    ]
  },
  {
    id:'informatica-reti', title:'Reti, protocolli e connettività', quizCount:211,
    summary:'LAN, WAN, indirizzi, apparati, protocolli e trasmissione dei dati.',
    items:[
      note('PAN, LAN, MAN e WAN','PAN copre lo spazio personale; LAN un edificio o sede; MAN un’area urbana; WAN aree geografiche molto estese.'),
      note('Client e server','Il client richiede un servizio; il server lo fornisce. In una rete peer-to-peer i dispositivi possono condividere risorse senza un server centrale dedicato.'),
      note('Switch, router e gateway','Lo switch collega dispositivi nella stessa rete locale; il router instrada pacchetti tra reti; il gateway è il punto di accesso verso un’altra rete.'),
      note('Modem e access point','Il modem adatta il segnale al collegamento del provider; l’access point offre connettività Wi-Fi ai dispositivi in un’area.'),
      note('Indirizzo IP e MAC','L’IP identifica logicamente un’interfaccia in rete e può cambiare; il MAC identifica l’interfaccia a livello locale ed è normalmente assegnato al dispositivo.'),
      note('TCP e UDP','TCP è orientato alla connessione e controlla consegna e ordine; UDP riduce i controlli e privilegia rapidità e bassa latenza.'),
      note('DNS e DHCP','DNS traduce nomi di dominio in indirizzi IP; DHCP assegna automaticamente configurazioni di rete ai dispositivi.'),
      note('HTTP, HTTPS e FTP','HTTP trasferisce risorse Web; HTTPS aggiunge cifratura e autenticazione tramite TLS; FTP è un protocollo tradizionale per trasferire file.'),
      note('Fibra ottica','Trasporta segnali luminosi in filamenti di vetro o materiale plastico, offrendo grande capacità e resistenza ai disturbi elettromagnetici.'),
      note('VPN','Crea un collegamento logico protetto attraverso una rete non fidata; può cifrare il traffico tra dispositivo e punto VPN.')
    ]
  },
  {
    id:'informatica-internet', title:'Internet, Web e servizi digitali', quizCount:183,
    summary:'Browser, URL, domini, HTML, collegamenti, cookie, cloud e servizi online.',
    items:[
      note('Internet e Web','Internet è l’infrastruttura mondiale di reti; il Web è uno dei servizi che usa Internet per distribuire pagine e risorse collegate.'),
      note('Browser e motore di ricerca','Il browser visualizza e usa pagine Web; il motore di ricerca indicizza risorse e aiuta a trovarle. Chrome è un browser, Google Search è un motore.'),
      note('URL','È l’indirizzo di una risorsa. Può includere schema, dominio, porta, percorso, parametri e frammento.','https://dominio/percorso?chiave=valore#sezione'),
      note('Dominio e provider','Il dominio è un nome leggibile associato a risorse di rete; il provider o ISP fornisce servizi di accesso a Internet.'),
      note('WWW, HTML e collegamento','WWW significa World Wide Web; HTML struttura una pagina; un link o collegamento ipertestuale porta a un’altra risorsa.'),
      note('Download e upload','Download trasferisce dati dalla rete al dispositivo; upload trasferisce dati dal dispositivo verso un servizio remoto.'),
      note('Cookie e cache','Un cookie è un piccolo dato salvato dal browser per stato o preferenze; la cache conserva copie di risorse per caricarle più rapidamente.'),
      note('Cloud computing','Risorse, applicazioni o spazio di archiviazione sono forniti tramite rete da sistemi remoti. Sincronizzazione e backup non sono automaticamente la stessa cosa.'),
      note('Commercio e servizi online','E-commerce, home banking, SPID, videoconferenza e social network sono servizi digitali: richiedono attenzione a dominio, HTTPS e autenticazione.'),
      note('Domini di primo livello','Il suffisso finale è il TLD: .it è nazionale, .com nasce per attività commerciali, .org per organizzazioni e .edu è usato soprattutto da istituzioni educative statunitensi.')
    ]
  },
  {
    id:'informatica-sicurezza', title:'Sicurezza informatica', quizCount:122,
    summary:'Malware, phishing, password, aggiornamenti, firewall, backup e firma digitale.',
    items:[
      note('Malware','Software dannoso. Virus si lega a file, worm si propaga autonomamente, trojan si presenta come programma legittimo, ransomware cifra o blocca dati chiedendo un riscatto.'),
      note('Phishing','Messaggio o sito ingannevole che cerca credenziali, denaro o l’apertura di allegati. Verifica mittente, dominio, urgenze anomale e richieste sensibili.'),
      note('Password e MFA','Usa password lunghe, uniche e gestite con un password manager. L’autenticazione a più fattori aggiunge una verifica oltre alla password.'),
      note('Antivirus e firewall','L’antivirus rileva o blocca codice dannoso; il firewall controlla il traffico di rete secondo regole. Sono complementari, non sostituiscono gli aggiornamenti.'),
      note('Patch e aggiornamenti','Correggono vulnerabilità e difetti noti. Sistema operativo, browser e applicazioni devono essere mantenuti aggiornati.'),
      note('Backup','È una copia separata usata per recuperare i dati. Regola 3-2-1: tre copie, due supporti diversi, una copia fuori sede o isolata.','3 copie · 2 supporti · 1 esterna'),
      note('Crittografia simmetrica e asimmetrica','La simmetrica usa la stessa chiave per cifrare e decifrare; l’asimmetrica usa una coppia di chiavi pubblica e privata.'),
      note('Firma digitale','Il firmatario usa la chiave privata; la verifica usa la chiave pubblica. Garantisce autenticità e integrità, non nasconde necessariamente il contenuto.'),
      note('HTTPS e certificato','HTTPS protegge il traffico con TLS. Il certificato aiuta a verificare l’identità del sito, ma non rende automaticamente affidabile ogni contenuto pubblicato.'),
      note('Ingegneria sociale','Sfrutta fiducia, paura, fretta o autorità per indurre una persona a compiere azioni rischiose. La difesa principale è verificare tramite un canale indipendente.')
    ]
  },
  {
    id:'informatica-software-dati', title:'Software, dati e rappresentazione', quizCount:156,
    summary:'Algoritmi, programmi, licenze, codifica binaria, testo digitale e compressione.',
    items:[
      note('Algoritmo','Procedimento finito composto da passi elementari, ordinati, chiari e non ambigui per risolvere un problema.'),
      note('Programma e codice sorgente','Il programma è una sequenza di istruzioni eseguibili; il codice sorgente è la forma scritta in un linguaggio di programmazione.'),
      note('Compilatore e interprete','Il compilatore traduce il programma prima dell’esecuzione; l’interprete analizza ed esegue le istruzioni durante l’uso.'),
      note('Bug e debug','Un bug è un errore o comportamento indesiderato del software; il debugging è l’attività di individuarlo e correggerlo.'),
      note('Licenze','Open source rende disponibile il codice secondo una licenza; freeware è gratuito ma non necessariamente aperto; shareware è distribuito in prova o con limitazioni.'),
      note('Sistema binario','Usa soltanto 0 e 1. Ogni posizione vale una potenza di 2.','1001₂ = 8 + 1 = 9₁₀'),
      note('ASCII e Unicode','Sono sistemi di codifica dei caratteri. Unicode rappresenta scritture e simboli di molte lingue; UTF-8 è una codifica Unicode molto diffusa.'),
      note('Compressione senza e con perdita','Lossless ricostruisce esattamente i dati; lossy elimina informazioni considerate meno importanti per ridurre maggiormente la dimensione.'),
      note('Testo digitale e ipertesto','Il testo digitale può essere cercato e modificato; l’ipertesto collega informazioni tramite rimandi navigabili.'),
      note('Input, elaborazione e output','Input inserisce dati, elaborazione li trasforma, output restituisce risultati; l’archiviazione conserva dati e programmi.','Input → elaborazione → output')
    ]
  },
  {
    id:'informatica-generale', title:'Informatica generale e trappole ricorrenti', quizCount:182,
    summary:'Concetti trasversali da distinguere rapidamente durante la prova.',
    items:[
      note('Account','Insieme dei dati che identifica un utente e gli consente di accedere a un servizio; non coincide con la sola password.'),
      note('Accessibilità','Capacità di servizi e contenuti digitali di essere utilizzabili anche da persone con disabilità, tramite struttura, comandi e alternative adeguate.'),
      note('Salva e Salva con nome','Salva aggiorna il file corrente; Salva con nome crea una nuova copia o permette di cambiare posizione, nome o formato.'),
      note('Backup e sincronizzazione','Il backup conserva versioni recuperabili; la sincronizzazione replica le modifiche e può propagare anche cancellazioni o errori.'),
      note('RAM e prestazioni','Aumentare la RAM può ridurre l’uso della memoria virtuale, ma la velocità dipende anche da CPU, archiviazione, software e carico.'),
      note('Dato e informazione','Il dato è un valore grezzo; l’informazione nasce da dati organizzati e interpretati in un contesto.'),
      note('Una cella, un contenuto','In un foglio di calcolo ogni cella contiene un singolo valore o una singola formula, anche se il testo può includere più parole.'),
      note('Procedura di risposta','Individua l’ambito della domanda, elimina le alternative che confondono strumenti diversi e controlla parole assolute come “sempre”, “solo” e “mai”.')
    ]
  }
];

export const logicNotes = [
  {
    id:'logica-deduzioni', title:'Deduzioni e condizioni', quizCount:918,
    summary:'Implicazioni, condizioni necessarie o sufficienti, negazioni e conclusioni certe.',
    items:[
      note('Implicazione','“Se A, allora B” significa che A è sufficiente per B e B è necessaria per A.','A → B'),
      note('Contrapposta','Da “se A allora B” segue validamente “se non B allora non A”.','A → B ≡ ¬B → ¬A'),
      note('Inversa non valida','Da “se A allora B” non puoi concludere automaticamente “se B allora A” né “se non A allora non B”.','A → B non implica B → A'),
      note('Se e solo se','Indica una doppia implicazione: A è sia necessaria sia sufficiente per B.','A ↔ B'),
      note('Negare “tutti”','La negazione di “tutti gli A sono B” è “almeno un A non è B”, non “nessun A è B”.','¬∀ = ∃ non'),
      note('Negare “esiste”','La negazione di “esiste almeno un A che è B” è “nessun A è B”.','¬∃ = nessuno'),
      note('Sillogismo','Se tutti gli A sono B e tutti i B sono C, allora tutti gli A sono C. L’esistenza di B non dimostra da sola l’esistenza di A.'),
      note('Conclusione necessaria','Deve essere vera in ogni situazione compatibile con le premesse. Un esempio possibile non basta a renderla necessaria.'),
      note('Metodo rapido','Trasforma ogni frase in una freccia o in un insieme, ignora informazioni decorative e prova a costruire un controesempio alle alternative.')
    ]
  },
  {
    id:'logica-serie', title:'Serie e sequenze', quizCount:292,
    summary:'Successioni numeriche, alfabetiche, simboliche e confronti di stringhe.',
    items:[
      note('Differenze','Calcola prima le differenze tra termini; se non sono costanti, controlla differenze di secondo livello o un andamento crescente.','+2, +4, +6…'),
      note('Rapporti','Verifica moltiplicazioni o divisioni costanti e combinazioni del tipo ×n ± k.','×2, ×2, ×2…'),
      note('Sottoserie alternate','Se la regola non emerge, separa termini in posizione dispari e pari: spesso formano due serie indipendenti.'),
      note('Potenze e figure note','Riconosci quadrati, cubi, numeri primi, Fibonacci e fattoriali.','1, 4, 9, 16… · 1, 1, 2, 3, 5…'),
      note('Serie a coppie','Un termine può essere la trasformazione del precedente: numero e quadrato, lettera e posizione, base e risultato.','7, 49, 8, 64, 9, 81'),
      note('Serie alfabetiche','Converti le lettere nelle posizioni dell’alfabeto e controlla salti, ritorni e alternanze.','A=1 · B=2 · … · Z=26'),
      note('Sequenze identiche','Confronta a blocchi di 3–4 caratteri e segna subito posizione e quantità delle ripetizioni; non affidarti alla forma complessiva.'),
      note('Controllo finale','La regola scelta deve spiegare tutti i passaggi, non soltanto gli ultimi due. Se due regole funzionano, preferisci quella più semplice e uniforme.')
    ]
  },
  {
    id:'logica-verbale', title:'Logica verbale', quizCount:260,
    summary:'Sinonimi, contrari, analogie, parole estranee e significato delle frasi.',
    items:[
      note('Sinonimo','Deve mantenere il significato nel contesto, non soltanto appartenere allo stesso argomento.'),
      note('Contrario','Individua prima il significato preciso e il registro della parola; evita termini soltanto diversi o non correlati.'),
      note('Analogia','Nomina la relazione della prima coppia e applicala nello stesso verso alla seconda: parte-tutto, strumento-funzione, causa-effetto, categoria-esempio.'),
      note('Parola da scartare','Cerca la categoria condivisa dalla maggioranza e verifica che un solo termine non vi appartenga.'),
      note('Parola ponte','Il termine corretto deve avere un legame preciso con entrambe le parole proposte, anche con significati diversi.'),
      note('Doppia negazione','Semplifica una negazione alla volta. “Non è dimostrata l’impossibilità di A” significa che non è stato dimostrato che A sia impossibile; non prova che A sia vero.'),
      note('Significato equivalente','Conserva quantità, tempo, soggetto e grado di certezza. “Può” non equivale a “deve”; “alcuni” non equivale a “tutti”.'),
      note('Lessico raro','Usa radice, prefissi, suffissi e contesto della frase; poi elimina le alternative incompatibili con tono e grammatica.')
    ]
  },
  {
    id:'logica-calcolo', title:'Problemi e calcolo logico', quizCount:1025,
    summary:'Percentuali, proporzioni, medie, velocità, probabilità e problemi numerici.',
    items:[
      note('Percentuale','Calcola la parte moltiplicando il totale per p/100; per risalire al totale dividi la parte per p/100.','parte = totale · p/100'),
      note('Variazioni successive','Un aumento del 20% e una diminuzione del 20% non si annullano: si moltiplicano i fattori.','1,20 · 0,80 = 0,96'),
      note('Proporzione','Il prodotto dei medi è uguale al prodotto degli estremi.','a : b = c : d ⇒ ad = bc'),
      note('Media aritmetica','Somma dei valori divisa per il loro numero. Se conosci media e quantità, ricava prima la somma totale.','media = somma / quantità'),
      note('Velocità, spazio e tempo','Mantieni unità coerenti e usa il triangolo delle formule.','s = vt · v = s/t · t = s/v'),
      note('Lavoro e portata','Se più macchine identiche lavorano insieme, le portate si sommano e il tempo diminuisce in proporzione.','tempo = quantità / portata totale'),
      note('Probabilità semplice','Casi favorevoli diviso casi possibili, se gli esiti sono equiprobabili.','P = favorevoli / possibili'),
      note('Scale','In scala 1:n, una lunghezza sulla carta moltiplicata per n dà la distanza reale nella stessa unità.','reale = disegno · n'),
      note('Strategia','Scrivi dati e incognita, converti le unità prima del calcolo e fai una stima per scartare risultati impossibili.')
    ]
  },
  {
    id:'logica-figure', title:'Figure e simboli', quizCount:785,
    summary:'Rotazioni, simmetrie, matrici, dadi e trasformazioni visive.',
    items:[
      note('Rotazione','La figura cambia orientamento ma conserva ordine relativo delle parti e verso interno. Controlla rotazioni di 90°, 180° e 270°.'),
      note('Riflessione','Lo specchio inverte destra e sinistra rispetto all’asse; non equivale a una semplice rotazione.'),
      note('Traslazione','La figura cambia posizione senza ruotare né ribaltarsi.'),
      note('Matrici','Confronta righe e colonne cercando una sola trasformazione alla volta: somma, sottrazione, sovrapposizione, rotazione o alternanza.'),
      note('Conteggio','Conta separatamente forme, lati, colori, riempimenti e orientamenti. Una caratteristica può crescere mentre un’altra diminuisce.'),
      note('Dadi','Su un dado standard le facce opposte sommano 7; in un dado generico ricava le opposizioni dalle viste, ricordando che tre facce visibili condividono un vertice.'),
      note('Sviluppi di solidi','Segna una faccia base e simula mentalmente le pieghe; facce che nel reticolo sono molto separate possono diventare adiacenti.'),
      note('Metodo anti-errore','Descrivi a parole la trasformazione prima di guardare le risposte e verifica dettagli asimmetrici come tacche, frecce e zone nere.')
    ]
  },
  {
    id:'logica-insiemi', title:'Insiemi e diagrammi', quizCount:274,
    summary:'Inclusione, sovrapposizione, separazione e catene tra categorie.',
    items:[
      note('Sottoinsieme','Se ogni elemento di A appartiene a B, A è contenuto in B. Nel diagramma il cerchio A sta completamente dentro B.','A ⊆ B'),
      note('Insiemi disgiunti','Non hanno elementi in comune e i cerchi non si sovrappongono.','A ∩ B = ∅'),
      note('Intersezione possibile','Se alcune entità possono appartenere a entrambi gli insiemi, i cerchi si sovrappongono senza che uno contenga necessariamente l’altro.'),
      note('Catena di inclusioni','Se “Capi Squadra Esperti” è parte dei “Capi Squadra”, che sono parte dei “Vigili del Fuoco”, servono tre insiemi annidati.','C ⊆ B ⊆ A'),
      note('Categoria e oggetto','Un singolo esempio appartiene alla sua categoria, ma una categoria più ampia non è contenuta nel singolo esempio.'),
      note('Compatibilità reale','Chiediti se esiste almeno un elemento che può appartenere a entrambe le categorie; non basarti soltanto sulle parole simili.'),
      note('Tre insiemi','Valuta le tre relazioni a coppie e poi controlla se può esistere una zona comune a tutti.'),
      note('Procedura','Scrivi per ogni coppia: contenuto, disgiunto o sovrapposto. Solo dopo scegli il diagramma che soddisfa contemporaneamente tutte le relazioni.')
    ]
  },
  {
    id:'logica-relazioni', title:'Relazioni e classificazioni', quizCount:50,
    summary:'Unione, intersezione, differenza, complemento e relazioni tra elementi.',
    items:[
      note('Appartenenza','x ∈ A significa che x è un elemento di A; A ⊆ B significa invece che ogni elemento di A appartiene a B.','x ∈ A · A ⊆ B'),
      note('Unione','Contiene tutti gli elementi che appartengono ad A oppure a B, senza duplicati.','A ∪ B'),
      note('Intersezione','Contiene soltanto gli elementi comuni ad A e B.','A ∩ B'),
      note('Differenza','A meno B contiene gli elementi di A che non appartengono a B. L’ordine è importante.','A ∖ B'),
      note('Complemento','Rispetto a un insieme universo U, il complemento di A contiene gli elementi di U che non sono in A.','Aᶜ = U ∖ A'),
      note('Cardinalità','Per due insiemi finiti, somma le quantità e sottrai gli elementi contati due volte.','|A ∪ B| = |A| + |B| − |A ∩ B|'),
      note('Insieme vuoto','Non contiene elementi e si indica con ∅. È sottoinsieme di ogni insieme.'),
      note('Classificazione','Individua proprietà necessarie e sufficienti per appartenere a una classe; un nome simile non garantisce la stessa relazione logica.')
    ]
  },
  {
    id:'logica-ordinamenti', title:'Ordinamenti e posizioni', quizCount:140,
    summary:'Classifiche, posti, giorni, relazioni spaziali e vincoli multipli.',
    items:[
      note('Vincolo diretto','Trasforma “A prima di B” in una freccia o in due caselle ordinate.','A < B'),
      note('Vincolo immediato','“Subito prima” o “immediatamente dopo” crea un blocco inseparabile; “prima” da solo può lasciare posti intermedi.'),
      note('Catena','Unisci progressivamente i confronti: se A precede B e B precede C, allora A precede C.','A < B < C'),
      note('Due graduatorie','Velocità e ordine di arrivo sono proprietà diverse: costruisci due colonne e non trasferire automaticamente un confronto dall’una all’altra.'),
      note('Posti e fermate','Assegna un numero alla prima posizione nota, traduci “due prima” con −2 e “cinque dopo” con +5, poi verifica tutti i vincoli.'),
      note('Giorni della settimana','Fissa un giorno di riferimento e muoviti modulo 7; “il giorno che precede venerdì” è giovedì, poi applica ieri o dopodomani.'),
      note('Negazioni di adiacenza','“9 non segue immediatamente 4” vieta il blocco 49; “9 non precede immediatamente 2” vieta 92. Cerca i blocchi proibiti.'),
      note('Tabella dei casi','Quando mancano posizioni assolute, elenca pochi casi compatibili e cancella quelli che violano anche un solo vincolo.')
    ]
  },
  {
    id:'logica-brani', title:'Comprensione dei brani', quizCount:648,
    summary:'Informazioni esplicite, inferenze consentite e alternative non dimostrabili.',
    items:[
      note('Solo il testo','Rispondi usando esclusivamente il brano, anche se conosci informazioni esterne vere.'),
      note('Esplicito, deducibile, non deducibile','Separa ciò che è scritto, ciò che segue necessariamente e ciò che è soltanto plausibile.'),
      note('Parole assolute','“Sempre”, “mai”, “tutti” e “solo” rendono un’alternativa più forte: deve essere sostenuta esattamente dal testo.'),
      note('Causa ed effetto','Non scambiare successione temporale o correlazione con causalità. Cerca connettivi come perché, quindi, provoca e dipende da.'),
      note('Soggetto e riferimento','Controlla a chi si riferiscono pronomi e dimostrativi e non attribuire a un gruppo ciò che il testo dice di un altro.'),
      note('Idea principale','Riassumi ogni paragrafo in poche parole e individua la tesi che li collega; i dettagli veri possono non rispondere alla domanda.'),
      note('Negazioni','Riscrivi l’alternativa in forma semplice: due negazioni possono conservare un significato molto diverso da una frase affermativa.'),
      note('Prova testuale','Per ogni risposta indica mentalmente la frase che la giustifica. Se non trovi una prova o un passaggio necessario, scartala.')
    ]
  },
  {
    id:'logica-mista', title:'Logica mista e strategie', quizCount:1461,
    summary:'Codici, scale, leve, problemi ibridi e metodo generale di risoluzione.',
    items:[
      note('Codici parola-numero','Allinea lettere e cifre, cerca ripetizioni e ricava una corrispondenza posizione per posizione prima di decodificare.'),
      note('Leve e bilance','In equilibrio i momenti rispetto al fulcro sono uguali.','forza₁ · braccio₁ = forza₂ · braccio₂'),
      note('Scale cartografiche','Moltiplica la misura sulla carta per il denominatore e converti alla fine nell’unità richiesta.','1:2500 · 15 cm = 375 m'),
      note('Figure con valori','Scrivi un’equazione per ogni forma invece di calcolare a mente; attenzione a forme ruotate o quantità diverse nell’ultima riga.'),
      note('Problema ibrido','Separa la parte linguistica da quella numerica: prima traduci i vincoli, poi esegui i calcoli.'),
      note('Eliminazione','Scarta risultati con unità errata, segno impossibile, ordine incompatibile o grandezza fuori scala.'),
      note('Gestione del tempo','Dopo circa un minuto senza progresso, marca la domanda e prosegui. Tornando dopo, riparti dai dati scritti e non dal ragionamento confuso.'),
      note('Verifica','Sostituisci il risultato nelle condizioni iniziali. Una risposta corretta deve soddisfare tutte le informazioni, non soltanto quella usata per calcolarla.')
    ]
  }
];

export const englishNotes = [
  {
    id:'inglese-tempi-verbali', title:'Tempi verbali', quizCount:388,
    summary:'Present, past, perfect, continuous e principali forme del futuro.',
    items:[
      note('Present simple','Abitudini, fatti e situazioni stabili. Alla terza persona singolare aggiunge normalmente -s.','I work · he works'),
      note('Present continuous','Azione in corso o situazione temporanea; si forma con be + verbo in -ing.','I am working now'),
      note('Past simple','Azione conclusa in un tempo passato definito; usa il paradigma irregolare quando necessario.','I watched · I went'),
      note('Past continuous','Azione in svolgimento in un momento passato, spesso interrotta da un past simple.','I was studying when he called'),
      note('Present perfect','Passato collegato al presente, esperienza o durata non conclusa; usa have/has + participio.','I have lived here for six years'),
      note('Past perfect','Azione avvenuta prima di un’altra azione passata.','I had left before she arrived'),
      note('Futuro','Will per decisioni istantanee o previsioni; be going to per intenzioni o evidenze; present continuous per programmi organizzati.','I will help · I am going to study · I am leaving tomorrow'),
      note('Segnali temporali','Every/usually → present simple; now/at the moment → continuous; yesterday/ago/last → past simple; since/for/already/yet → spesso present perfect.'),
      note('Domande e negazioni','Present simple usa do/does; past simple usa did. Dopo l’ausiliare il verbo torna alla forma base.','Does he like…? · He did not go')
    ]
  },
  {
    id:'inglese-modali-condizionali', title:'Modali, condizionali e forma passiva', quizCount:63,
    summary:'Can, must, should, periodi ipotetici, passivo e costruzioni correlate.',
    items:[
      note('Verbi modali','Can, could, may, might, must, should e would sono seguiti dalla forma base senza to e non prendono -s.','She can drive'),
      note('Must e have to','Must esprime forte obbligo del parlante; have to necessità esterna. Mustn’t significa divieto; don’t have to significa assenza di necessità.'),
      note('Should','Esprime consiglio o aspettativa, non obbligo assoluto.','You should study'),
      note('Zero e first conditional','Zero: verità generale, if + present, present. First: possibilità futura, if + present, will + base.','If water reaches 100°C, it boils · If it rains, I will stay home'),
      note('Second conditional','Situazione ipotetica presente o futura: if + past, would + base.','If I knew, I would tell you'),
      note('Third conditional','Ipotesi irreale nel passato: if + past perfect, would have + participio.','If I had known, I would have told you'),
      note('Forma passiva','Il complemento oggetto dell’attiva diventa soggetto; si usa be nel tempo richiesto + participio passato.','They built it → It was built'),
      note('Modal perfect','Modal + have + participio: must have deduzione, should have rimpianto/critica, could have possibilità non realizzata.','He must have worked hard'),
      note('Would you mind','È seguito dalla forma in -ing; una risposta positiva alla richiesta è normalmente “No, not at all”.','Would you mind helping me?')
    ]
  },
  {
    id:'inglese-pronomi', title:'Pronomi, possessivi e relativi', quizCount:83,
    summary:'Soggetto, complemento, possesso, riflessivi e relative clauses.',
    items:[
      note('Pronomi soggetto','I, you, he, she, it, we, they precedono normalmente il verbo.','They are ready'),
      note('Pronomi complemento','Me, you, him, her, it, us, them seguono verbo o preposizione.','I know him · Come with us'),
      note('Aggettivi possessivi','My, your, his, her, its, our, their accompagnano un nome e non prendono articolo.','Their names'),
      note('Pronomi possessivi','Mine, yours, his, hers, ours, theirs sostituiscono il nome.','This pen is mine'),
      note('Riflessivi','Myself, yourself, himself, herself, itself, ourselves, yourselves, themselves rimandano al soggetto.','She taught herself'),
      note('Who, which e that','Who per persone; which per cose; that può sostituirli in molte relative restrittive.'),
      note('Whose e whom','Whose esprime possesso; whom è forma complemento, soprattutto formale.','The man whose car…'),
      note('Indefiniti','Someone/something in frasi affermative; anyone/anything spesso in domande e negative; nobody/nothing hanno già valore negativo.')
    ]
  },
  {
    id:'inglese-nomi-articoli', title:'Articoli, nomi e quantità', quizCount:105,
    summary:'A, an, the, plurali, countable e quantificatori.',
    items:[
      note('A e an','Articolo indefinito singolare: a prima di suono consonantico, an prima di suono vocalico. Conta il suono, non la lettera.','a university · an hour'),
      note('The','Indica qualcosa di specifico, già noto o unico nel contesto. Non si usa automaticamente con ogni nome.'),
      note('Articolo zero','Niente articolo con plurali o nomi non numerabili in senso generale.','Books are useful · Water is essential'),
      note('Plurali','Regola generale -s/-es; irregolari frequenti: child/children, man/men, woman/women, person/people, mouse/mice.'),
      note('Countable e uncountable','I countable hanno singolare e plurale; gli uncountable, come information e advice, non usano normalmente a/an né il plurale.'),
      note('Much e many','Much con non numerabili; many con plurali numerabili. A lot of funziona con entrambi.','much sugar · many books'),
      note('Few e little','Few con numerabili e little con non numerabili indicano quantità insufficiente; a few/a little indicano una piccola quantità ma positiva.'),
      note('Some e any','Some è comune nelle affermative e nelle offerte; any nelle domande e negative.','some milk · any tomatoes'),
      note('How much e how many','How much chiede quantità o prezzo con non numerabili; how many chiede il numero di elementi contabili.')
    ]
  },
  {
    id:'inglese-aggettivi-avverbi', title:'Aggettivi, avverbi e comparativi', quizCount:64,
    summary:'Posizione, forma, confronti e superlativi regolari o irregolari.',
    items:[
      note('Aggettivo','Descrive un nome, normalmente lo precede o segue be e verbi simili. In inglese non cambia per genere o numero.','a tall boy · two tall girls'),
      note('Avverbio','Descrive verbo, aggettivo o altro avverbio; molti avverbi di modo terminano in -ly.','She speaks slowly'),
      note('Good e well','Good è normalmente aggettivo; well è normalmente avverbio.','a good result · she works well'),
      note('Comparativo breve','Aggettivi brevi usano -er + than; raddoppia la consonante quando richiesto.','tall → taller than · big → bigger than'),
      note('Comparativo lungo','Aggettivi lunghi usano more/less + aggettivo + than.','more expensive than'),
      note('Superlativo','The + -est per aggettivi brevi; the most/least per quelli lunghi.','the tallest · the most useful'),
      note('Irregolari','Good → better → best; bad → worse → worst; far → farther/further → farthest/furthest.'),
      note('Uguaglianza','As + aggettivo + as; nella negativa not as/so … as.','She is as nice as her brother'),
      note('Comparativi correlativi','The + comparative…, the + comparative… esprime due variazioni collegate.','The fewer mistakes you make, the better your mark')
    ]
  },
  {
    id:'inglese-preposizioni', title:'Preposizioni di tempo, luogo e movimento', quizCount:159,
    summary:'In, on, at, to, from, for, since, by e combinazioni frequenti.',
    items:[
      note('Tempo: at, on, in','At per ore e momenti precisi; on per giorni e date; in per mesi, anni, stagioni e periodi lunghi.','at 8 · on Monday · in July'),
      note('Luogo: at, on, in','At indica un punto; on una superficie; in uno spazio o area.','at the station · on the table · in London'),
      note('To e from','To indica destinazione o destinatario; from origine o provenienza.','go to London · come from Canada'),
      note('Into e onto','Into indica movimento verso l’interno; onto movimento verso una superficie. In e on indicano normalmente posizione.'),
      note('For e since','For introduce una durata; since il momento iniziale.','for two weeks · since Monday'),
      note('By e until','By significa entro e non oltre; until indica continuità fino a un momento.','finish by Friday · wait until Friday'),
      note('Between e among','Between tra due o tra elementi distinti; among all’interno di un gruppo.'),
      note('Collocazioni','Listen to, depend on, look at, wait for, arrive in una città/paese, arrive at un luogo puntuale.'),
      note('Mezzi e movimento','By car/train/plane, on foot; get in/out of a car, get on/off a bus or train.')
    ]
  },
  {
    id:'inglese-costruzione-frase', title:'Costruzione della frase e domande', quizCount:73,
    summary:'Ordine delle parole, ausiliari, negazioni, risposte brevi e discorso indiretto.',
    items:[
      note('Ordine base','Soggetto + verbo + complemento; gli avverbi di frequenza precedono il verbo principale ma seguono be.','I often study · She is always ready'),
      note('Domande','Ausiliare + soggetto + verbo base; con be l’ausiliare è lo stesso verbo.','Does he work? · Is she ready?'),
      note('Wh- questions','Parola interrogativa + ausiliare + soggetto + verbo. Se who/what è soggetto, non serve do.','Where do you live? · Who called?'),
      note('Negazioni','Do/does/did + not + forma base; con be e modali aggiungi not direttamente.','He doesn’t work · She isn’t ready · I can’t drive'),
      note('Risposte brevi','Ripetono soggetto e ausiliare, non il verbo principale.','Do you like it? Yes, I do'),
      note('Question tags','Affermazione positiva → coda negativa; affermazione negativa → coda positiva, con lo stesso ausiliare.','You are ready, aren’t you?'),
      note('So e neither','So + ausiliare + soggetto concorda con un’affermazione positiva; neither con una negativa.','I like it. So do I. · I don’t. Neither do I.'),
      note('Discorso indiretto','Con un verbo introduttivo al passato, tempi e riferimenti possono arretrare: am → was, will → would, today → that day.'),
      note('Too ed enough','Too precede aggettivo/avverbio; enough lo segue ma precede un nome.','too difficult · good enough · enough time')
    ]
  },
  {
    id:'inglese-phrasal-idioms', title:'Phrasal verbs ed espressioni', quizCount:23,
    summary:'Verbi frasali, collocazioni e modi di dire presenti nei quesiti.',
    items:[
      note('Look for / look after','Look for = cercare; look after = prendersi cura di.','I am looking for my keys · She looks after the child'),
      note('Look forward to','Significa attendere con piacere ed è seguito da nome o forma in -ing.','I look forward to going'),
      note('Give up / carry on','Give up = smettere o rinunciare; carry on = continuare.','give up smoking · carry on working'),
      note('Turn on / turn off','Accendere o spegnere un dispositivo. Con un pronome: turn it on, non turn on it.'),
      note('Put on / take off','Put on = indossare; take off = togliere un indumento o decollare, secondo il contesto.'),
      note('Find out / set up','Find out = scoprire; set up = organizzare, installare o fondare.'),
      note('Get along / get in touch','Get along = andare d’accordo; get in touch = mettersi in contatto.'),
      note('Run out of / break down','Run out of = esaurire una scorta; break down = guastarsi o crollare emotivamente.'),
      note('Espressioni','On the same page = essere d’accordo; as far as I know = per quanto ne so; in spite of = nonostante; straight on = sempre dritto.')
    ]
  },
  {
    id:'inglese-vocabolario', title:'Vocabolario e situazioni quotidiane', quizCount:79,
    summary:'Sinonimi, contrari, famiglia, luoghi, professioni, viaggi e indicazioni.',
    items:[
      note('Sinonimi frequenti','Nearly = almost; begin = start; difficult = hard; purchase = buy; reply = answer.'),
      note('Contrari frequenti','Love/hate, cheap/expensive, early/late, borrow/lend, arrive/leave, accept/refuse.'),
      note('Famiglia','Parents = genitori, relatives = parenti, niece = nipote femmina, nephew = nipote maschio, toddler = bambino piccolo.'),
      note('Falsi amici','Actually = in realtà, eventually = alla fine, library = biblioteca, parents = genitori, sensible = ragionevole, factory = fabbrica.'),
      note('Professioni e luoghi','Doctor/nurse → hospital; teacher → school; waiter → restaurant; clerk → office; firefighter → fire station.'),
      note('Viaggio','Ticket, platform, luggage, boarding pass, departure, arrival, lift/ride, traffic lights e crossroads ricorrono nelle situazioni pratiche.'),
      note('Tempo e calendario','Monday–Sunday; January–December. Before indica prima, after dopo, next successivo, previous precedente.'),
      note('Odd one out','Trova la categoria comune: cello e harp sono strumenti, jug è un recipiente; niece e toddler sono persone, veal è carne.'),
      note('Contesto','Prima di tradurre una parola isolata, controlla il verbo, le preposizioni e la situazione: lo stesso termine può avere più significati.')
    ]
  },
  {
    id:'inglese-generale', title:'Grammatica generale e strategia', quizCount:514,
    summary:'Costruzioni trasversali, gerundio, infinito, imperativo e metodo di scelta.',
    items:[
      note('Infinito con to','Dopo want, need, decide, hope, plan e aggettivi come important si usa spesso to + verbo.','It is important to study'),
      note('Forma in -ing','Dopo enjoy, avoid, finish, mind e preposizioni si usa -ing.','instead of watching TV'),
      note('Imperativo','Usa la forma base senza soggetto per ordini o istruzioni; la negativa usa don’t.','Give her my message · Don’t touch it'),
      note('Make e do','Make per creare o produrre; do per attività e compiti. Collocazioni: make a mistake, make a decision, do homework, do a job.'),
      note('Say e tell','Say qualcosa; tell qualcuno qualcosa.','say hello · tell me the truth'),
      note('There is / there are','There is con singolare o non numerabile; there are con plurale.','There is some milk · There are two books'),
      note('Connettivi','Because introduce causa; so conseguenza; although contrasto; unless significa “se non”; while può indicare contemporaneità o contrasto.'),
      note('Scelta grammaticale','Guarda prima i segnali temporali, poi soggetto e ausiliare, infine la forma richiesta dopo preposizioni, modali o verbi particolari.'),
      note('Controllo finale','Rileggi l’intera frase con la risposta: deve essere corretta sia grammaticalmente sia per significato e registro.')
    ]
  }
];
