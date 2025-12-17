# 🔄 Script di Sincronizzazione Automatica

## Come usare `sync_from_git.bat`

### 📋 Uso Rapido

**Doppio click su `sync_from_git.bat`**

Lo script farà automaticamente:
1. ✅ Verifica il branch corrente
2. ✅ Salva le tue modifiche locali (se presenti)
3. ✅ Scarica gli aggiornamenti da GitHub
4. ✅ Applica gli aggiornamenti ai tuoi file
5. ✅ Ripristina le tue modifiche locali

### 🎯 Quando usarlo

- Dopo che Claude ha fatto modifiche su GitHub
- Prima di iniziare a lavorare sul progetto
- Quando vuoi assicurarti di avere l'ultima versione del codice

### 🔒 Sicurezza

Lo script usa `git stash` per salvare temporaneamente le tue modifiche locali prima di scaricare gli aggiornamenti, quindi **non perderai mai il tuo lavoro**.

### ⚡ Shortcut (Opzionale)

Per rendere ancora più rapido:

1. **Crea un collegamento sul Desktop:**
   - Click destro su `sync_from_git.bat`
   - Invia a → Desktop (crea collegamento)
   - Ora hai l'icona sul desktop per sincronizzare con 1 click!

2. **Rinomina il collegamento:**
   - Click destro sul collegamento
   - Rinomina → "🔄 Sync Git"

### 📝 Note

- Lo script usa il percorso: `C:\Users\lucagiuseppe.forti\Desktop\progettoParcoauto`
- Branch: `claude/fix-fleet-manager-errors-dfwgN`
- Se cambi cartella o branch, modifica questi valori nello script

### ❓ Risoluzione Problemi

**"Non riconosce git come comando"**
- Assicurati che Git sia installato e nel PATH di sistema

**"Errore durante il pull"**
- Apri CMD nella cartella del progetto
- Esegui: `git status` per vedere eventuali conflitti
- Contatta per supporto se necessario

---

**Creato il:** 15 Dicembre 2025
**Versione:** 1.0
