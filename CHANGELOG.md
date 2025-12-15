
# GESTIONALE MATRIX - CHANGELOG

## Versione v1.25.5 - Novembre 2025

🎯 **Migliorie UI e migrazione database per sinistri**

- **Paginazione e stampa su Scadenze**: la pagina delle Scadenze ora mostra la barra di navigazione delle pagine anche nella parte superiore, accanto ai pulsanti di stampa, mantenendo i filtri correnti.  In precedenza questa funzionalità era presente solo negli altri moduli.
- **Pulsanti dei form corretti**: nei moduli di gestione (Manutenzioni, Preventive, Sinistri, ecc.) i pulsanti *Reset*, *Annulla* e *Salva* sono stati ridisegnati.  Grazie a una nuova regola CSS, le etichette restano all’interno dei riquadri e il testo non esce più dai pulsanti.
- **Colonne ridimensionabili ripristinate**: è stato reintrodotto lo script `resizable_table.js` (mancante nella versione precedente) e aggiunte le regole CSS per i manici di ridimensionamento.  Tutte le tabelle con classe `resizable-table` tornano a supportare l’allargamento e il restringimento delle colonne con il mouse.
- **Migrazione automatica per i sinistri**: all’avvio del modulo *Sinistri* viene eseguito un controllo della tabella `sinistri`.  Se il database non contiene le nuove colonne opzionali (numero sinistro, telefoni, numeri e dati delle patenti), vengono create automaticamente via `ALTER TABLE`.  Questo evita l’errore `no such column` quando si usano database esistenti senza aggiornamento.
- **Aggiornamento stile**: migliorato `matrix_style.css` con regole per i bottoni delle azioni nei form e per il manico di ridimensionamento, uniformando l’interfaccia in tutto il gestionale.

## Versione v1.25.3 - Ottobre 2025

🔧 **Correzione filtri veicoli nel modulo sinistri**

• **Scelta veicolo filtrata per nucleo**: il campo **Veicolo** nei moduli di creazione e modifica sinistro ora mostra solo i veicoli appartenenti al nucleo selezionato. In precedenza, gli utenti amministratori vedevano l’elenco completo dei veicoli di tutti i nuclei; ora la lista è filtrata correttamente tramite `get_veicoli_by_nucleo()`.

• **Rimozione popolamento automatico**: il costruttore di `SinistroForm` non popola più automaticamente le scelte del campo `veicolo_id`. Le scelte vengono impostate nelle route (`aggiungi_sinistro` e `modifica_sinistro`), assicurando coerenza con il filtro nucleo dell’utente.

• **Aggiornamento documentazione**: aggiornato il changelog per documentare questa modifica.


## Versione v1.25.0 - Ottobre 2025

🚧 **Nuovo modulo Sinistri**

- **Registrazione sinistri**: introdotta la gestione completa delle pratiche di sinistro.  È ora possibile registrare incidenti associati a un veicolo, indicando data, luogo, altri veicoli coinvolti, tipologia del sinistro (con controparte, vandalico o sconosciuto) e una descrizione dettagliata.  Ogni sinistro è legato al nucleo dell’utente e può essere filtrato per tipo e veicolo.
- **Allegati sinistro**: per ogni sinistro è possibile caricare uno o più documenti (ad es. CID, fotografie, documenti d’identità, denunce) tramite la nuova sezione “Allegati” presente nella pagina di dettaglio.  I file sono memorizzati in una cartella dedicata (`static/uploads/sinistri`) e possono essere scaricati o eliminati.
- **Navigazione dedicata**: il nuovo modulo è accessibile dalla barra di navigazione tramite la voce “Sinistri” (icona auto incidentata).  La pagina indice mostra i sinistri in ordine cronologico, con filtri avanzati e un pulsante per espandere le colonne della tabella.  Un contatore riepiloga il numero totale di sinistri e la suddivisione per tipologia.
- **CRUD modulare**: sono state implementate le rotte per creare, visualizzare, modificare ed eliminare un sinistro.  La creazione e la modifica sfruttano un form a schede in stile Matrix, con convalida dei campi.  La cancellazione rimuove anche gli allegati collegati.
- **Compatibilità nuclei**: tutte le query sui sinistri sono filtrate per nucleo come negli altri moduli.  Gli admin possono selezionare il nucleo desiderato dal menu e gestire i sinistri di ciascuna sede.
- **Aggiornamenti minori**: aggiornato `utils/nuclei.py` con la funzione `get_sinistri_by_nucleo`, importati i modelli e i blueprint necessari in `app/__init__.py` e aggiunto il link nella dashboard.

✔️ **Compatibilità**: il nuovo modulo è completamente modulare.  Le tabelle `sinistri` e `allegati_sinistri` vengono create automaticamente all’avvio dell’applicazione; nessun’altra funzionalità esistente è stata alterata.

## Versione v1.25.1 - Ottobre 2025

🐞 **Correzione bug CSRF**

- **Eliminazione sinistri e allegati**: corretta un’eccezione `UndefinedError: 'csrf_token' is undefined` che si verificava dopo l’inserimento o la visualizzazione dei sinistri.  Le azioni di eliminazione non utilizzano più il filtro `csrf_token()` nelle template `sinistri/index.html` e `sinistri/dettaglio.html`, poiché l’applicazione non utilizza la protezione CSRF di Flask‑WTF per le form anonime.  La modifica assicura che i pulsanti di cancellazione funzionino correttamente senza errori.

## Versione v1.25.2 - Ottobre 2025

🎨 **Miglioramento interfaccia sinistri**

- La pagina indice dei sinistri è stata aggiornata per presentare la tabella all’interno di una **cornice** con bordo e sfondo scuro, in linea con gli altri moduli (manutenzioni, scadenze).  Questo miglioramento rende l’elenco più coerente con il resto dell’interfaccia Matrix.
- Le intestazioni e le celle della tabella utilizzano colori e font coerenti con il tema Matrix, rendendo le informazioni dei sinistri facilmente leggibili.  Le righe cambiano colore al passaggio del mouse per evidenziare la riga selezionata.
- Le colonne della tabella mantengono la funzionalità di espansione, per adattarsi a contenuti lunghi, con la preferenza salvata nel browser.

## Versione v1.24.8 - Ottobre 2025

🔧 **Miglioramenti e correzioni**

- **Allegati per le scadenze**: ora è possibile caricare, scaricare ed eliminare documenti anche dalle scadenze.  È stato creato il modello `AllegatoScadenza` e un nuovo blueprint `allegati_scadenze` con le rotte per la gestione degli allegati.  Nella pagina di dettaglio della scadenza compare una sezione “Allegati” con l’elenco dei file e il modulo di upload, in analogia a quanto già presente per le manutenzioni.
- **Rimozione scadenze rinnovate dalle urgenze**: quando una scadenza viene segnata come “Rinnovata”, non compare più tra le scadenze urgenti.  Il filtro “urgenti” e il contatore in dashboard escludono ora le scadenze rinnovate.
- **Correzione ordinamento veicoli**: sistemato l’ordinamento dei veicoli che posiziona i mezzi con stato “Dismesso” in fondo all’elenco.  È stato aggiornato l’uso della funzione `case` di SQLAlchemy per evitare errori nella costruzione della query.
- **Compatibilità retroattiva**: le modifiche sono state implementate in modo modulare e sono pienamente compatibili con le versioni precedenti.  La creazione di nuove tabelle (`allegati_scadenze`) avviene automaticamente all’avvio dell’applicazione.


## Versione v1.24.9 - Ottobre 2025

🔧 **Miglioramenti scadenze**

- **Ordinamento scadenze**: nell’elenco scadenze le voci con stato “Rinnovata” vengono ora posizionate in fondo alla lista.  L’ordinamento mantiene le scadenze attive e scadute nella parte superiore e ordina le rinnovate per data di scadenza.
- **Avvisi solo per scadenze attive**: i messaggi “Programmare intervento” e “Intervento urgente” non vengono più visualizzati per le scadenze rinnovate.  Questo evita di mostrare alert inutili su scadenze già rinnovate.

## Versione v1.24.10 - Ottobre 2025

🔧 **Miglioramenti dashboard**

- **Statistica veicoli**: invertito il conteggio per evidenziare i veicoli attivi come numero principale (visualizzato in grande) e mostrare il totale dei veicoli presenti come sottotitolo.  In questo modo l’attenzione si concentra sui mezzi effettivamente in servizio.
- **Statistica fornitori**: la scheda fornitori ora mette in primo piano il numero di fornitori attivi, mentre il totale dei fornitori è riportato in piccolo come informazione di contesto.
- **Statistica manutenzioni**: la card relativa alle manutenzioni mostra come numero principale gli interventi “da fare” e, in sottotitolo, il totale delle manutenzioni registrate.
- Queste modifiche sono state applicate a tutte le card della dashboard dove erano presenti valori “attivi”, senza alterare il comportamento delle restanti funzionalità del gestionale.

## Versione v1.22 - Ottobre 2025

🚀 **Moduli aggiuntivi e miglioramenti**

- **Manutenzioni preventive (Modulo 1)**: introdotto il nuovo modulo per la programmazione degli interventi periodici.  È possibile impostare intervalli in chilometri e/o mesi per ciascun veicolo e registrare l’ultimo intervento effettuato.  La prossima scadenza viene calcolata automaticamente e gli interventi programmati sono accessibili da un’apposita voce di menu (“Preventive”).  Tutti i dati sono memorizzati in una tabella dedicata (`manutenzioni_preventive`) e non alterano le tabelle esistenti.
- **Analitica semplificata (Modulo 2)**: la dashboard ora include due grafici che mostrano a colpo d’occhio il numero di manutenzioni “Da fare” vs “Fatto” e le scadenze “Prossime” vs “Scadute”.  I grafici sono generati con Chart.js ed escludono qualsiasi informazione su costi, telematica o sensori, in linea con le richieste dell’utente.
- **Policy & Procedure (Modulo 4)**: aggiunta una pagina dedicata alle linee guida sull’utilizzo dei veicoli, accessibile dal menu “Policy”.  La pagina contiene indicazioni su ispezioni, responsabilità dei conducenti, pianificazione della manutenzione, uso appropriato dei mezzi e gestione della documentazione.
- **Allegati manutenzioni (Modulo 7)**: per ogni manutenzione è ora possibile caricare allegati (fatture, certificati, foto ecc.).  Gli allegati sono memorizzati nella cartella `static/uploads` e gestiti attraverso una nuova tabella (`allegati_manutenzioni`).  I file possono essere scaricati o eliminati dalla pagina di dettaglio della manutenzione.
- **Notifiche in‑app (Modulo 8)**: introdotto un sistema di notifiche che avvisa l’utente delle scadenze imminenti (entro 30 giorni) e delle manutenzioni preventive prossime.  Le notifiche sono visibili tramite un’icona a campana nella barra superiore e si aggiornano automaticamente per ciascun nucleo.

✔️ **Compatibilità**: tutti i nuovi moduli sono stati implementati in modo modulare e non interferiscono con le funzionalità esistenti.  Le nuove tabelle (`manutenzioni_preventive`, `allegati_manutenzioni` e `notifiche`) vengono create automaticamente all’avvio dell’applicazione.  La retro‑compatibilità con le versioni precedenti rimane garantita.

## Versione v1.22.1 - Ottobre 2025

🐞 **Correzioni bug**

- Risolto un problema per cui il gestionale non si avviava a causa di un `NameError` nella funzione `inject_notifications`.  Ora `current_user` viene importato correttamente da `flask_login` nel context processor.

## Versione v1.23 - Ottobre 2025

🎨 **Aggiornamento layout Preventive e Policy**

- **Uniformità grafica per le manutenzioni preventive**: la pagina indice delle manutenzioni preventive è stata allineata allo stile della gestione manutenzioni.  La tabella ora è incorniciata da bordi ben visibili, con intestazioni colorate e hover sulle righe, e utilizza le stesse classi di stile adottate per la tabella delle manutenzioni ordinarie. Anche la visualizzazione delle righe “nessun dato” è stata armonizzata.  La pagina di inserimento/modifica delle preventive mantiene la struttura a schede (“form-card”) già in uso per le altre sezioni.
- **Policy e Procedure dinamiche**: la pagina Policy ora non contiene più un testo statico, ma visualizza i documenti aziendali allegati dall’utente.  I file PDF caricati sono stati convertiti in immagini e ordinati cronologicamente (2019‑07‑25, 2022‑02‑09, 2023‑03‑28, 2023‑12‑20).  Ogni sezione mostra il titolo con la data e tutte le pagine del documento, rendendo immediata la consultazione delle procedure interne direttamente dall’interfaccia.
- **Route Policy migliorata**: la route `policy.view_policy` costruisce un elenco dei documenti presenti nella cartella `static/policy` e lo passa al template.  Se nuovi file vengono aggiunti alla cartella con il formato `gg-mm-aaaa.pdf`, appariranno automaticamente nella pagina senza ulteriori modifiche al codice.

✔️ **Compatibilità garantita**: nessuna funzionalità preesistente è stata modificata; l’aggiornamento riguarda unicamente il layout delle preventive e la visualizzazione dei documenti di policy.  Le variabili di stile e i colori rimangono coerenti sia con il tema Matrix sia con il tema Professional.

## Versione v1.23.1 - Ottobre 2025

## Versione v1.23.2 - Ottobre 2025

🛠️ **Correzioni bug e ulteriori miglioramenti**

- **Fix link immagini Policy su Windows**: in alcuni ambienti Windows i link alle immagini della sezione *Policy & Procedure* restituivano l’errore “Not Found” quando si tentava di aprire un documento.  Il problema era dovuto all’utilizzo di `os.path.join`, che genera percorsi con backslash (`\`) su Windows.  Ora i percorsi delle immagini sono costruiti con barre (`/`) indipendentemente dal sistema operativo, garantendo l’apertura corretta dei documenti【42532791316568†L347-L357】.
- **Migliorata coerenza visiva del form Preventive**: la pagina di aggiunta e modifica delle manutenzioni preventive è stata ulteriormente uniformata allo stile delle altre sezioni.  I campi sono organizzati in schede con bordi, icone e colori coerenti con quelli dei moduli esistenti, assicurando un’esperienza utente più consistente.

## Versione v1.24 - Ottobre 2025

🚀 **Nuove funzionalità e potenziamenti**

- **Filtri avanzati**: le pagine indice delle manutenzioni ordinarie e preventive sono state arricchite con un pannello di filtri per tipo di intervento e veicolo, oltre al filtro per stato già presente.  I filtri preservano il contesto durante la navigazione fra le pagine e consentono di combinare più criteri di ricerca contemporaneamente.
- **Esportazione Excel**: introdotte due nuove route (`/manutenzioni/export` e `/preventive/export`) che generano un file Excel contenente l’elenco corrente (con i filtri applicati) delle manutenzioni ordinarie e preventive.  I file includono le colonne principali (veicolo, tipo, data, km, stato, fornitore per le ordinarie; veicolo, tipo, intervallo, ultimo, prossimo e note per le preventive) e vengono scaricati direttamente dal browser.
- **Cronologia manutenzioni preventive**: per ogni manutenzione preventiva viene ora registrato un log delle operazioni (creazione, modifica, eliminazione).  La nuova pagina “Cronologia Preventiva” consente di consultare tutte le modifiche effettuate, con data, azione, autore e dettagli dei campi variati.  I log sono archiviati in una tabella dedicata (`log_preventive`).
- **Tasto “Colonne larghe”**: su entrambe le tabelle (manutenzioni ordinarie e preventive) è stato aggiunto un pulsante che permette di espandere le celle per visualizzare testi lunghi senza troncamento.  La preferenza viene salvata nel browser tramite `localStorage`, così che l’impostazione rimanga anche dopo il refresh della pagina.
- **Piccoli fix e pulizia**: rimossi i file duplicati nelle cartelle `static/policy` e aggiornati i percorsi per prevenire errori 404 sulle immagini.  Aggiornata la paginazione delle tabelle per mantenere i filtri quando si cambia pagina.  Creato il modello `AllegatoPreventiva` (per eventuali futuri allegati alle preventive) e predisposti i file per un modulo di allegati.

✔️ **Compatibilità**: l’aggiornamento non modifica strutture esistenti se non tramite nuove tabelle (`log_preventive`, `allegati_preventive`).  Le nuove funzionalità sono modulari e possono essere ignorate senza interferire con il resto dell’applicazione.

## Versione v1.24.1 - Ottobre 2025

🛠️ **Fix minori**

- **Colonne adattabili**: corretto il comportamento del pulsante “Larghezza Colonne” nelle tabelle delle manutenzioni ordinarie e preventive.  Ora, quando si attiva l’opzione, la tabella utilizza `table-layout: auto` e le celle `th` e `td` permettono l’andata a capo (`white-space: normal`, `word-break: break-word`), così che i testi lunghi siano visibili integralmente. La preferenza continua a essere memorizzata nel browser tramite `localStorage`.

🛠️ **Migliorie aggiuntive**

- **Form preventiva uniformato**: la pagina di aggiunta/modifica delle manutenzioni preventive (`/preventive/aggiungi` e `/preventive/modifica/<id>`) utilizza ora lo stesso layout a schede e la stessa grafica dei moduli esistenti. Questo garantisce coerenza visiva e usabilità omogenea con le altre pagine del gestionale.
    - **Immagini Policy cliccabili**: le immagini dei documenti presenti nella sezione Policy & Procedure sono ora racchiuse in un link. Cliccando su ogni miniatura si apre l’immagine a dimensione piena in una nuova scheda, facilitando la consultazione dei documenti.

## Versione v1.24.2 - Ottobre 2025

🔧 **Rimozione del modulo percorrenze e miglioramenti alla Scheda Km**

- **Eliminazione completa delle “Percorrenze”**: sono stati rimossi il blueprint, i form e tutte le pagine collegate alle “percorrenze” (inclusi i limiti).  La sequenza animata iniziale reindirizza ora alla dashboard e non più a una pagina non esistente.  Questo evita link obsoleti e pulisce la struttura del progetto.
- **Filtri avanzati per le Scadenze**: la pagina di gestione scadenze ora permette di filtrare per **stato**, **tipo** e **veicolo**.  È stato reintrodotto un filtro rapido che consente di visualizzare solo le scadenze urgenti (entro 30 giorni) o solo quelle attive.  I filtri si combinano fra loro e vengono preservati durante la navigazione.
- **Selezione Scheda Kilometrica più intuitiva**: la pagina per scegliere la scheda mensile non usa più menu a tendina per il mese.  L’utente seleziona l’anno da un elenco e poi clicca direttamente sul nome del mese (Gennaio, Febbraio, ecc.) per aprire la scheda corrispondente.  I link si aggiornano dinamicamente quando si cambia anno.
- **Veicoli dismessi esclusi**: la scheda mensile mostra ora solo i veicoli con stato **Attivo**.  Questo evita che i mezzi “Dismessi” o “Inattivi” compaiano nelle tabelle dei mesi successivi alla loro dismissione (non disponendo della data precisa di disattivazione).
- **Pulsante larghezza colonne esteso**: il tasto per espandere o restringere le colonne è stato aggiunto anche alle pagine della scheda kilometrica (mensile, trimestrale e riepilogo trimestrale).  La preferenza viene memorizzata nel browser via `localStorage`.
- **Pulizia finale**: rimossi i file e le directory obsolete legati alle percorrenze dal pacchetto distribuito.  Aggiornato lo script di redirect dello splash e uniformati i percorsi statici per evitare errori 404.

✔️ **Compatibilità garantita**: queste modifiche non richiedono migrazioni del database e non toccano le tabelle esistenti.  Gli utenti dei nuclei *Via Campania* e *Via Capitel* hanno accesso alle stesse funzionalità senza distinzione.  Tutti i nuovi filtri e i pulsanti lavorano correttamente indipendentemente dal nucleo selezionato.

## Versione v1.24.3 - Ottobre 2025

🐞 **Bug fix di avvio**

- **Modulo percorrenze rimosso correttamente**: il file `app/routes/__init__.py` importava ancora il blueprint `percorrenze_bp`, causando un errore `ModuleNotFoundError` all’avvio del gestionale.  L’import residuo è stato eliminato e l’elenco dei blueprint aggiornato.  Ora il gestionale si avvia correttamente senza tentare di caricare il modulo rimosso.



## Versione v1.24.4 - Ottobre 2025

🐞 **Bug fix per la selezione della scheda kilometrica**

- **Correzione dei link dinamici**: la pagina di selezione della scheda chilometrica causava un errore `ValueError: invalid literal for int()` a causa dell'utilizzo di `url_for` con parametri segnaposto (`"__YEAR__"` e `"__MONTH__"`) all'interno di un template Jinja.  Jinja tentava di convertire questi segnaposto in numeri durante il rendering, generando l'eccezione.  I link ai mesi sono ora costruiti dinamicamente via JavaScript concatenando anno e mese (es. `/scheda-km/2025/10`) senza passare per `url_for`, eliminando l'errore.

## Versione v1.7 - Settembre 2025
## Versione v1.24.6 - Ottobre 2025

## Versione v1.24.7 - Ottobre 2025

- **Elenco veicoli ordinato con dismessi in fondo**: nella pagina gestione veicoli, i mezzi "Dismessi" sono ora visualizzati dopo tutti i veicoli attivi.  L’ordinamento alfabetico per targa rimane invariato all’interno dei due gruppi, rendendo più rapido individuare i mezzi operativi.
- **Storico manutenzioni e scadenze per veicoli dismessi**: nei moduli di modifica delle manutenzioni e delle scadenze, le targhe dei veicoli dismessi restano disponibili nel menu a discesa.  Questo consente di consultare e modificare i record storici senza sostituire il veicolo con il primo attivo in elenco.
✨ **Selezione Scheda Kilometrica in stile calendario**

- **Griglia 3 x 4**: i 12 mesi sono disposti in una griglia di 3 colonne per 4 righe, raccolti all’interno di un riquadro con bordo e sfondo leggero.  L’aspetto richiama un piccolo calendario: ogni cella ha dimensioni uniformi, bordi arrotondati e un leggero effetto hover, in linea con il tema Matrix.
- **Riquadro compatto**: il calendario è racchiuso in un contenitore centrato con dimensioni massime prefissate, così da non occupare l’intera larghezza della pagina.  Questo migliora l’equilibrio visivo e rende la navigazione più intuitiva.
- **Link dinamici**: quando l’utente seleziona un anno diverso dal menu a tendina, i link all’interno delle celle vengono aggiornati via JavaScript senza ricaricare la pagina.  In questo modo il calendario resta sempre coerente con l’anno selezionato e senza errori.


🔄 **Anagrafica fornitori unica tra i nuclei**

- L'elenco dei fornitori è stato unificato: ora gli utenti di tutti i nuclei (es. *Via Capitel* e *Via Campania*) condividono la stessa anagrafica. Non è più necessario reinserire i fornitori per ciascun nucleo.
- Modificate le funzioni `get_fornitori_query()` e `validate_fornitore_access()` in `app/routes/fornitori.py`: ora non viene più applicato alcun filtro sul campo `nucleo` in nessun caso. Gli amministratori possono continuare a selezionare un nucleo per altre sezioni del gestionale (via `admin_nucleo_filter`), ma l’elenco fornitori rimane invariato per tutti i nuclei.
- Rimossa la validazione sull’appartenenza al nucleo quando si accede ai dettagli di un fornitore: tutti gli utenti possono visualizzare e modificare qualsiasi fornitore.

🔧 **Aggiornamenti ai menu a tendina dei fornitori**

- Tutti i campi selettivi che devono elencare i fornitori (ad esempio, la scelta della “Società di noleggio” nel modulo Veicoli) ora mostrano l’intera anagrafica, senza più filtri basati sul nucleo.  Sono state aggiornate le funzioni `get_societa_noleggio_choices()` e `get_fornitori_for_choices()` per restituire sempre tutti i fornitori attivi.

✔️ **Retro‐compatibilità garantita**: nessuna modifica è stata apportata ai moduli esistenti oltre a quelle necessarie per la condivisione dell’anagrafica fornitori. I fornitori esistenti nei diversi nuclei sono ora accessibili da tutti gli utenti.

## Versione v1.8 - Settembre 2025

🚧 **Filtraggio per nucleo nelle Schede Kilometriche**

- Le viste della *Scheda Kilometrica* (mensile e trimestrale) ora mostrano solo i veicoli appartenenti al nucleo corrente.  In precedenza, le schede includevano anche i veicoli di altri nuclei (es. *Via del Capitel*) quando si operava su *Via Campania*.
- Implementato l’utilizzo di `get_veicoli_by_nucleo()` in tutte le route della scheda chilometrica per recuperare i veicoli filtrati secondo il nucleo dell’utente o il filtro selezionato dall’amministratore.
- Per la vista trimestrale è stato aggiunto un filtro sugli ID dei veicoli per estrarre solo le schede chilometriche pertinenti.

✔️ **Compatibilità**: questa modifica non altera la struttura dei dati esistenti e si integra con la gestione precedente delle anagrafiche fornitori unificate.

## Versione v1.9 - Settembre 2025

🚗 **Creazione automatica della scadenza revisione**

- All'aggiunta di un nuovo veicolo viene ora generata automaticamente una scadenza di tipo **Revisione**.
  La data della prima revisione viene calcolata a quattro anni dalla data di immatricolazione, come previsto
  dalla normativa vigente, con gestione automatica dei casi di anni bisestili. La scadenza viene associata al
  nucleo dell'utente che inserisce il veicolo e viene impostata come "Attiva" con notifica 30 giorni prima.
- Questa funzionalità elimina il passaggio manuale di creazione della scadenza, riducendo il rischio di
  dimenticanze e migliorando l'efficienza della gestione.

✔️ **Compatibilità con le release precedenti**: l'introduzione della revisione automatica non modifica la
struttura del database esistente. Se l'inserimento della scadenza dovesse fallire per un qualsiasi motivo,
il veicolo viene comunque creato correttamente e l'operazione può essere completata manualmente.

## Versione v1.10 - Settembre 2025

📊 **Riepilogo trimestrale accessibile e stampabile**

- Nella vista mensile della *Scheda Kilometrica* è stato aggiunto un collegamento diretto al trimestre
  corrispondente. Il trimestre viene calcolato automaticamente in base al mese selezionato e consente di
  visualizzare rapidamente i dati mensili del trimestre.
- Nel riepilogo trimestrale è disponibile un nuovo tasto **Esporta Excel** che genera un file Excel con i
  chilometri iniziali, finali e percorsi per ogni veicolo nel trimestre. Questo consente di effettuare
  analisi o archiviazione dei dati anche per periodi più lunghi rispetto al singolo mese.
- Aggiunto anche un pulsante **Stampa** nella vista riepilogo trimestrale che richiama la finestra di
  stampa del browser, facilitando la creazione di report cartacei o PDF del riepilogo.

✔️ **Mantenimento compatibilità**: queste funzionalità sono integrate senza alterare la logica esistente. I
moduli esistenti restano invariati e la nuova rotta per l’esportazione trimestrale utilizza la stessa
logica di calcolo già presente nel riepilogo.

## Versione v1.11 - Settembre 2025

🔧 **Correzione conteggi fornitori nella dashboard**

- Le statistiche dei fornitori (totale, attivi, società di noleggio) ora fanno riferimento all’anagrafica unica
  condivisa tra tutti i nuclei, senza più filtri per nucleo. Questo risolve i conteggi errati visualizzati
  nelle dashboard dei nuclei *Via Campania* e *Via Capitel*.

📊 **Filtri corretti per l’esportazione mensile**

- L’esportazione Excel mensile ora include solo i veicoli del nucleo corrente (o selezionato dall’amministratore),
  evitando che nella stampa di *Via Campania* compaiano i veicoli di *Via Capitel*.

🗓️ **Rimozione del dettaglio trimestrale e accesso diretto al riepilogo**

- Il collegamento “Vai al trimestre” dalla vista mensile apre direttamente il riepilogo trimestrale con i
  chilometri iniziali, finali e percorsi; la pagina che visualizzava i tre mesi del trimestre non è più
  accessibile dal menu, in linea con le richieste dell’utente.
- Eliminato il pulsante “Dettaglio mensile” nella vista trimestrale per evitare confusione.

📁 **Formato Excel migliorato per la scheda mensile**

- Ogni file Excel generato per il mese contiene ora una prima riga con il nome del mese in italiano, tutto maiuscolo,
  con carattere grande (48), celle unite e centratura verticale e orizzontale.
- Tutte le celle della tabella (intestazioni e dati) sono bordate per migliorare la leggibilità. Anche
  l’esportazione trimestrale contiene bordi.

💅 **Migliorie nella visualizzazione delle tabelle HTML**

- Sono stati applicati bordi sottili a tutte le celle delle tabelle nella scheda kilometrica (viste mensile e
  riepilogo trimestrale). I campi di input sono stati adattati per non sovrapporsi ed essere più leggibili.

🗓️ **Nomi dei mesi localizzati**

- La scheda kilometrica mostra ora i nomi dei mesi in italiano (es. “Gennaio” invece di “January”).

## Versione v1.12 - Settembre 2025

💡 **Tabella migliorata per la scheda kilometrica**

- Introdotta una nuova classe CSS `km-table` che sostituisce l’uso della tabella Bootstrap standard.
  La nuova tabella ha bordi chiari (bianchi con leggera trasparenza) che risaltano sullo sfondo scuro,
  padding aumentato tra le celle e righe alternate per facilitare la lettura.
- Aggiornate le viste mensile e trimestrale della scheda kilometrica a utilizzare la classe `km-table`.
- Gli input dei chilometri sono stati ridimensionati e adattati allo stile della nuova tabella.
- Le modifiche rendono le tabelle più professionali e leggibili, in linea con le richieste dell’utente.

## Versione v1.13 - Settembre 2025

🖨️ **Funzionalità di stampa avanzata e report veicoli**

- Ogni pagina del gestionale presenta ora due pulsanti di stampa: **Stampa pagina** per inviare
  direttamente alla stampante l’intero contenuto della vista corrente e **Stampa selezione** che
  permette di selezionare con il mouse una porzione della pagina e stamparne solo il contenuto
  evidenziato. Quest’ultima funzione apre una finestra temporanea con gli stili del tema corrente
  applicati alla selezione e nasconde elementi superflui come header, footer e menu.
- È stato aggiunto un nuovo script `print_utils.js` che gestisce la stampa della selezione
  clonando il contenuto selezionato e applicandovi i fogli di stile correnti.
- Durante la stampa (via browser), header, footer e pulsanti di controllo vengono nascosti per
  ottimizzare lo spazio sulla carta grazie a un nuovo foglio di stile `@media print` incluso in
  `base.html`.

📄 **Report dinamico per veicoli**

- È stato introdotto un nuovo modulo *Report* con un blueprint dedicato (`report_bp`).
  Dalla pagina dettaglio di ogni veicolo è ora disponibile il pulsante **Report** (icona
  `fa-file-alt`) che porta a una pagina riepilogativa del veicolo.
- Il report mostra targa, marca, modello, chilometri attuali, la società di noleggio e altre
  informazioni anagrafiche. Inoltre elenca le manutenzioni da fare, quelle eseguite, le scadenze
  attive, le scadenze scadute e i fornitori coinvolti (con settore, telefoni ed email).
- L’utente può scegliere dinamicamente quali sezioni visualizzare e stampare tramite caselle di
  spunta; le sezioni disattivate vengono nascoste senza ricaricare la pagina.
- Tutte le tabelle del report utilizzano la classe `km-table` introdotta nella versione precedente
  per garantire leggibilità e bordi chiari.

🎨 **Nuovo tema professional e miglioramenti UI**

- È stato aggiunto un secondo tema grafico “Professional” caratterizzato da colori
  rilassanti (verde acqua/azzurro su sfondo scuro), font moderni e contrasti più soft.
- Nel menu utente è possibile selezionare il tema preferito (Matrix o Professional) e la scelta
  viene salvata nella sessione dell’utente senza influenzare gli altri utilizzatori del sistema.
- Le icone della barra di navigazione sono state uniformate e rese più moderne: Dashboard usa
  `fa-gauge-high`, Veicoli `fa-car-side`, Fornitori `fa-id-card`, Manutenzioni `fa-wrench`,
  Scadenze `fa-calendar-check` e Scheda Kilometrica `fa-road`.  È stato inoltre aggiunto
  un pulsante **Report** nella pagina dettaglio veicolo con icona `fa-file-alt`.
- L’intestazione e il contenitore principale erano inizialmente spostati verso sinistra (circa 5 cm)
  sui monitor di grandi dimensioni per compensare lo spazio a destra e impedire che la barra di
  navigazione uscisse dallo schermo.  Questa scelta è stata rivista nella versione v1.14, dove
  l’interfaccia torna centrata attraverso margini automatici.

✔️ **Compatibilità e modularità**

- Tutte le modifiche sono state sviluppate in maniera modulare: i nuovi file (route, template e
  script) non interferiscono con i moduli esistenti e possono essere facilmente disattivati o
  sostituiti in versioni future.  La stampa avanzata funziona sia con il tema Matrix originale
  sia con il nuovo tema Professional.

## Versione V1_1_CLEAN - Luglio 2025

✅ **Pulizia sistema limiti**:
- Eliminati file `limiti.html` e `limite_form.html`
- Rimosse tutte le route Flask relative ai limiti
- Rimossi i controlli/validazioni legati ai limiti nei form

✅ **Semplificazione interfaccia percorrenze**:
- Rimossa colonna "Limite" dalla tabella principale
- Rimossa colonna "Stato"
- Etichetta "Km finali" rinominata in "Km"

✅ **Contenuti aggiornati**
- File `form.html` aggiornato con layout Matrix e lista veicoli dinamica

✅ **Pulizia progetto**
- Rimozione file obsoleti e duplicati
- Nuovo pacchetto zip con struttura semplificata e sicura

---

Prossime versioni potrebbero includere:
- Cruscotto riepilogativo per veicolo
- Filtri avanzati mese/trimestre/anno
- Report PDF ed esportazione CSV

## Versione v1.15 - Settembre 2025

🎨 **Tema professionale completamente rivisto**

- Il vecchio tema “Professional” è stato sostituito da un nuovo stile più sobrio e moderno.  La
  paletta utilizza toni di blu e grigio con accenti azzurri, pensati per essere riposanti e
  professionali. Lo sfondo animato “Matrix” è stato disabilitato e sostituito da uno sfondo
  fisso, eliminando distrazioni visive.
- L’animazione del codice che scorre è caricata solo quando si utilizza il tema Matrix: in
  modalità professionale non viene caricato il file `matrix_effects.js` e gli elementi
  `#matrix-bg` e `#matrix-canvas` sono nascosti.
- È stato importato il font “Inter” per migliorare la leggibilità generale e aggiornati gli
  accenti cromatici.
- Le checkbox e i pulsanti del report veicolo sono state stilizzate con un colore di accento
  coerente con il nuovo tema e dimensioni maggiori per essere più visibili.

🖨️ **Stampa ottimizzata**

- Le regole `@media print` sono state aggiornate per ridurre la dimensione dei caratteri durante
  la stampa, evitando che i contenuti risultino enormi su carta.  I checkbox e i controlli del
  report vengono nascosti correttamente solo nella versione da stampare.
- Continuano a essere disponibili i pulsanti “Stampa pagina” e “Stampa selezione”, con la
  funzione di selezione migliorata dalla maggiore leggibilità delle checkbox.

✔️ **Altre correzioni**

- Il tema professionale disabilita completamente lo sfondo e l’animazione Matrix per favorire la
  selezione del testo e la stampa dell’area evidenziata.
- Le modifiche non influiscono sul database o sui moduli esistenti e possono essere attivate via
  menu utente dal cambio tema.

## Versione v1.14 - Settembre 2025

🎛️ **Ulteriori miglioramenti all’interfaccia e alla stampa**

- La barra di navigazione è stata ulteriormente raffinata: tutte le icone sono state aggiornate a versioni più moderne e coerenti (`fa-gauge-high` per Dashboard, `fa-car-side` per Veicoli, `fa-id-card` per Fornitori, `fa-wrench` per Manutenzioni, `fa-calendar-check` per Scadenze).
- Aggiunti stili di stampa globali: durante la stampa tramite il browser vengono automaticamente nascosti header, footer, menu utente e pulsanti di stampa, permettendo di ottenere documenti puliti.  Il contenuto principale si espande a tutta larghezza della pagina per sfruttare al meglio lo spazio.
- Nei report dei veicoli le caselle di selezione (checkbox) vengono nascoste nella stampa completa, così da non comparire sul documento cartaceo.
- Piccoli ritocchi all’icona dei Fornitori e alle altre etichette per uniformare la grafica con il tema Professional.

  - È stato corretto l’allineamento generale dell’interfaccia: l’intestazione e l’area dei contenuti tornano ad essere centrate su schermi di grandi dimensioni.  Il margine negativo introdotto nella versione precedente, che spostava tutto verso sinistra, è stato rimosso e sostituito con margini automatici.

🚀 **Preparazione ai test di nuove funzionalità**

- Queste modifiche introducono le basi per ulteriori miglioramenti, tra cui la stampa selettiva di parti del report e la prova di nuovi layout professionali.  Il sistema rimane compatibile con le versioni precedenti e non richiede alcuna migrazione del database.

## Versione v1.15 - Settembre 2025

🎨 **Nuovo tema professionale “Business”**

- Il tema professionale è stato completamente ridisegnato: ora utilizza una palette blu/grigio con accenti azzurri su uno sfondo scuro fisso.  Lo sfondo e l’animazione Matrix non vengono più mostrati quando si seleziona questo tema.
- I caratteri sono stati aggiornati (Inter/Roboto) per migliorare la leggibilità e rendere l’interfaccia più moderna e riposante per gli occhi.
- Le variabili CSS sono state riorganizzate per offrire un look coerente e professionale, evitando effetti “giocosi”.

🖨️ **Correzioni stampa e interfaccia report**

- Sono state ridotte le dimensioni dei caratteri durante la stampa (12 pt per il testo, 10 pt per le tabelle) per evitare testi sovradimensionati sui documenti cartacei.
- I controlli di selezione presenti nel report veicolo sono stati stilizzati: i checkbox sono ora ben visibili, colorati secondo il tema e racchiusi in etichette cliccabili, così da poter scegliere facilmente quali sezioni includere nella stampa.
- Il foglio di stile di stampa nasconde automaticamente header, footer, menu utente e pulsanti di controllo, lasciando in evidenza solo i dati selezionati.

🔧 **Gestione dinamica degli effetti grafici**

- Lo script `matrix_effects.js` viene caricato solo quando il tema in uso è Matrix.  Per il tema professionale, sia il canvas sia lo sfondo animato vengono completamente disattivati, rendendo l’interfaccia statica.

## Versione v1.17 - Settembre 2025

📄 **Stampe ottimizzate**

- Le tabelle della scheda chilometrica e dei report ora presentano bordi neri ben definiti e una dimensione del carattere ridotta (9 pt) durante la stampa, per garantire un layout leggibile su carta.
- È stata migliorata la sezione `@media print` in `base.html`: tutte le tabelle collassano i bordi, le celle sono bordate e il contenuto si adatta alla larghezza del foglio A4.
- Correzioni alle bordature bianche delle tabelle in modalità scura: i bordi sono ora più visibili (trasparenza aumentata), rendendo le griglie facilmente leggibili sullo schermo.

🎨 **Tema professionale aggiornato**

- Introdotte variabili RGB per il colore principale (`--matrix-green-r`, `--matrix-green-g`, `--matrix-green-b`) che consentono di generare sfondi trasparenti coerenti con la palette azzurra.
- Le componenti dell’interfaccia che in precedenza utilizzavano valori “verde Matrix” fissi (come i pulsanti utente e il menu a tendina) sono state sovrascritte nel tema professionale: ora adottano sfondi e bordi azzurri con trasparenze basate sulle nuove variabili.
- Le etichette con i checkbox per i report sono state perfezionate nel tema professionale: il contrasto è stato aumentato e l’accent color segue la nuova palette.

🔧 **Altri miglioramenti**

- Aggiunta una classe al tag `<body>` (`theme-matrix` o `theme-professional`) per applicare stili mirati in base al tema selezionato.
- Sistemato l’allineamento del menù utente e l’uso di spaziature coerenti, completando la centratura dell’interfaccia iniziata nella versione precedente.
- Rimosse tutte le animazioni e transizioni dal tema Matrix e disabilitato il caricamento del file `matrix_effects.js`. Lo sfondo animato e altri effetti in movimento non vengono più caricati, eliminando la linea orizzontale che attraversava lo schermo.

### v1.25.9 – Aggiornamento dipendenze (pandas)

- **Inclusione `pandas`**: aggiunta la libreria `pandas` al file `requirements.txt` (versione minima 2.1.4) per risolvere l’errore `ModuleNotFoundError: No module named 'pandas'` riscontrato durante l’inizializzazione del database (`init_db.py`) e l’avvio dell’applicazione. Alcuni moduli (es. manutenzioni) utilizzano `pandas` per generare report Excel, quindi la libreria è ora installata automaticamente insieme alle altre dipendenze.
- **Nessuna altra modifica**: questo aggiornamento non tocca blueprint, database o interfaccia. Si tratta esclusivamente di un hotfix per assicurare che tutte le funzionalità funzionino al primo avvio senza errori.

## Versione v1.18 - Settembre 2025

🔧 **Correzione report veicolo**

- Le manutenzioni da fare e quelle eseguite vengono ora separate con un confronto case-insensitive sul campo `stato`. Questo evita che interventi con valori come “eseguita”, “ESEGUITA” o spazi aggiuntivi vengano visualizzati in entrambe le sezioni.  In presenza di manutenzioni con stato diverso da “Eseguita” (es. “Da fare”, “Programmato”, “In corso”), queste verranno correttamente considerate “da fare”.

💡 **Miglioramento dell’usabilità**

- È stata verificata la logica di visualizzazione delle sezioni nel report veicolo: ora la selezione tramite check-box nasconde o mostra soltanto le sezioni scelte senza confondere i dati.

## Versione v1.18 - Settembre 2025

🔧 **Rimozione definitiva della riga animata**

- Nel tema Matrix è stato disattivato anche l’effetto di evidenziazione delle voci di menu (`.nav-link::before`), che causava la visualizzazione di una riga orizzontale in movimento su alcune schermate.  Ora questa pseudo‑elemento non viene più renderizzato, eliminando l’ultima animazione visibile.

Questa versione non introduce altre modifiche funzionali, ma perfeziona l’interfaccia affinché risulti completamente statica e professionale.

## Versione v1.21 - Ottobre 2025

🔧 **Correzione eliminazione manutenzioni e scadenze**

- Sono stati risolti i problemi di eliminazione nelle tabelle **Manutenzioni** e **Scadenze** che generavano errori `405 Method Not Allowed`.
- Le route di eliminazione (`/elimina/<id>`) sono ora configurate per accettare solo richieste **POST**, impedendo cancellazioni via GET.
- I pulsanti di eliminazione nei template sono stati convertiti in **form** con metodo POST e conferma tramite `onsubmit`, in linea con le migliori pratiche di sicurezza HTTP.
- Grazie a queste modifiche, l'eliminazione di una manutenzione o una scadenza avviene correttamente senza errori, mantenendo l’interfaccia utente e il popup di conferma invariati.

### v1.25.6 – UI compact pass (reversibile)
- Top‑bar/`matrix-header` resa compatta (~56px) con allineamento automatico dell’area utente a destra.
- Navigazione (`.main-nav`) su una sola riga con overflow orizzontale **solo** sulla riga dei link.
- Tipografia omogenea: base 14px, titoli 22/18, badge 12px su tutti i moduli.
- Card e tabelle uniformate (padding coerenti, ombre leggere, colonna Azioni a larghezza minima).
- Nessuna modifica a logica/blueprint/DB. Solo CSS in `matrix_style.css` e `professional_style.css`.

### v1.25.8 – Header Style B + Toggle offset
- Header Style B: minimal dark con underline neon + LED bar separata (no overlap).
- Nav rifinita; hover/active eleganti (neon medio).
- Toggle utente (Barra distanziata/compatta) con persistenza in localStorage (default: distanziata 22px).
- (Se assente) persistenza larghezze colonne.
- Solo HTML/CSS/JS. Nessun cambio a blueprint/DB.

### v1.25.9 FIX4 – Header senza linee verdi
- Rimosse definitivamente le linee verdi (pseudo-elementi ::before/::after e separatori).
- Header pulito con sola ombra, nessuna possibilità di sovrapposizione.

### v1.26.0 – Topbar Geotab-like con Toggle
- Aggiunto stile topbar **Geotab-like** (compatta, senza separatori, hover soft).
- Nuovo toggle nel menu utente: *Stile topbar: Geotab/Matrix* con persistenza `localStorage`.
- Nessun cambio a blueprint/DB.
