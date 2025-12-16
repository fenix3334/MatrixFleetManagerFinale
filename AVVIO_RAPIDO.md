# ⚡ AVVIO RAPIDO - 3 Metodi

Scegli il metodo che preferisci:

---

## 🎯 METODO 1: Script Automatico (CONSIGLIATO)

### Linux/Mac:
```bash
cd /home/user/MatrixFleetManagerFinale
./start.sh
```

### Windows:
Doppio click su `start.bat`

**Aspetta 10 secondi** e poi apri il browser su **http://localhost:5173**

---

## 🎯 METODO 2: Manuale (2 Terminali)

### Terminale 1 - Backend:
```bash
cd /home/user/MatrixFleetManagerFinale/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Terminale 2 - Frontend:
```bash
cd /home/user/MatrixFleetManagerFinale/frontend
npm install
npm run dev
```

Apri browser: **http://localhost:5173**

---

## 🎯 METODO 3: Docker (Futuro)

_Coming soon..._

---

## ✅ Primo Accesso

1. Apri **http://localhost:5173**
2. Clicca **"Registrati"**
3. Compila:
   - Username: `admin`
   - Password: `admin123`
   - Nucleo: `Via Capitel`
4. Clicca **"Registrati"**
5. Vedi la **Dashboard**!

---

## 🔍 Verifica che Funzioni

### Test Backend:
```bash
curl http://localhost:5000/health
```

Risposta OK:
```json
{"status":"ok","message":"Matrix Fleet Manager API is running"}
```

### Test Frontend:
Apri browser: http://localhost:5173
Dovresti vedere la pagina di login

### Swagger API:
Apri browser: http://localhost:5000/api/docs
Puoi testare tutte le API

---

## 🛑 Come Fermare

### Se hai usato script automatico:
Premi **CTRL+C** nel terminale

### Se hai usato metodo manuale:
Premi **CTRL+C** in ENTRAMBI i terminali

---

## 🆘 Problemi?

### Backend non parte:
```bash
# Verifica Python
python3 --version

# Dovrebbe essere >= 3.8
```

### Frontend non parte:
```bash
# Verifica Node.js
node --version
npm --version

# Dovrebbero essere >= 18
```

### Porta occupata:
```bash
# Trova e chiudi processo su porta 5000
lsof -ti:5000 | xargs kill

# Trova e chiudi processo su porta 5173
lsof -ti:5173 | xargs kill
```

### Errore CORS nel browser:
1. Verifica che backend sia su porta 5000
2. Verifica che frontend sia su porta 5173
3. Riavvia entrambi

---

## 📞 Comandi Utili

```bash
# Pulisci tutto e ricomincia
cd backend && rm -rf venv instance
cd ../frontend && rm -rf node_modules

# Reinstalla backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Reinstalla frontend
cd ../frontend
npm install
```

---

## 🎉 Tutto OK?

Se vedi la dashboard, sei pronto! 🚀

Prossimi step:
1. Aggiungi un veicolo
2. Esplora le funzionalità
3. Testa le API su Swagger
