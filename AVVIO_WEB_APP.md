# 🚀 Guida Rapida - Avvio Web App

## ⚡ Quick Start (2 comandi)

### Terminale 1 - Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Terminale 2 - Frontend
```bash
cd frontend
npm install
npm run dev
```

Apri browser: **http://localhost:5173**

---

## 📋 Checklist Pre-Avvio

### Backend
- [ ] Python 3.8+ installato
- [ ] Virtual environment creato
- [ ] Dipendenze installate (`pip install -r requirements.txt`)
- [ ] File `.env` presente in `backend/`

### Frontend
- [ ] Node.js 18+ installato
- [ ] NPM/Yarn disponibile
- [ ] Dipendenze installate (`npm install`)
- [ ] File `.env` presente in `frontend/`

---

## 🔧 Setup Dettagliato

### 1. Backend API

```bash
# Naviga nella directory backend
cd /path/to/MatrixFleetManagerFinale/backend

# Crea virtual environment
python -m venv venv

# Attiva virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt

# Verifica .env
cat .env  # Dovrebbe esistere

# Avvia server
python run.py
```

**Output atteso:**
```
 * Running on http://127.0.0.1:5000
 * Debugger is active!
```

**Testa API:**
```bash
curl http://localhost:5000/health
# Output: {"status":"ok","message":"Matrix Fleet Manager API is running"}
```

### 2. Frontend Vue.js

```bash
# Naviga nella directory frontend
cd /path/to/MatrixFleetManagerFinale/frontend

# Installa dipendenze (prima volta)
npm install

# Verifica .env
cat .env  # Dovrebbe contenere: VITE_API_URL=http://localhost:5000/api

# Avvia dev server
npm run dev
```

**Output atteso:**
```
  VITE v7.2.4  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3. Primo Accesso

1. Apri browser: **http://localhost:5173**
2. Dovresti vedere la pagina di login
3. Clicca su "Registrati"
4. Crea primo utente:
   - Username: `admin`
   - Password: `admin123` (min 6 caratteri)
   - Nucleo: `Via Capitel`
5. Accedi alla dashboard

---

## 🐛 Troubleshooting

### Backend non si avvia

**Problema: `ModuleNotFoundError: No module named 'flask'`**
```bash
# Verifica che virtual environment sia attivo
which python  # Dovrebbe puntare a venv/bin/python

# Reinstalla dipendenze
pip install -r requirements.txt
```

**Problema: `FileNotFoundError: .env`**
```bash
# Copia .env.example
cp .env.example .env

# Oppure crea manualmente
cat > .env << EOF
DATABASE_URL=sqlite:///instance/fleet_manager.db
JWT_SECRET_KEY=dev-jwt-secret-key-2024
JWT_ACCESS_TOKEN_EXPIRES=3600
FLASK_ENV=development
SECRET_KEY=dev-flask-secret-key-2024
FRONTEND_URL=http://localhost:5173
EOF
```

**Problema: Porta 5000 già in uso**
```bash
# Cambia porta in run.py o usa:
PORT=5001 python run.py
```

### Frontend non si avvia

**Problema: `command not found: npm`**
```bash
# Installa Node.js
# Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Mac:
brew install node

# Verifica installazione
node --version
npm --version
```

**Problema: `ERR! code ENOENT`**
```bash
# Pulisci cache e reinstalla
rm -rf node_modules package-lock.json
npm install
```

**Problema: CORS errors nel browser**
```bash
# Verifica che backend sia avviato su http://localhost:5000
# Verifica .env frontend:
echo "VITE_API_URL=http://localhost:5000/api" > .env
```

**Problema: Login fallisce**
1. Apri Console Browser (F12)
2. Verifica Network tab per errori API
3. Controlla che backend sia avviato
4. Verifica URL API in `.env`

---

## 🔍 Verifica Setup

### Test Backend
```bash
# Health check
curl http://localhost:5000/health

# Swagger docs (apri in browser)
open http://localhost:5000/api/docs

# Registra utente test
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123","nucleo":"Via Capitel"}'
```

### Test Frontend
```bash
# Build di test
npm run build

# Preview build
npm run preview
```

---

## 📊 Monitoring Durante Sviluppo

### Logs Backend
Il server Flask stampa automaticamente:
- Richieste HTTP in arrivo
- Errori SQL
- Warnings

### Logs Frontend
Apri DevTools (F12) > Console:
- Errori Vue
- Chiamate API
- State changes (con Vue DevTools)

### Vue DevTools
Installa estensione browser:
- Chrome: [Vue.js devtools](https://chrome.google.com/webstore/detail/vuejs-devtools)
- Firefox: [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)

---

## 🎯 Prossimi Passi

Dopo aver avviato con successo:

1. **Esplora Swagger**: http://localhost:5000/api/docs
2. **Testa API manualmente** con Swagger UI
3. **Crea primo veicolo** da interfaccia web
4. **Inizia sviluppo** di nuovi moduli

---

## 📝 Script Automatici

### Avvio Completo (Linux/Mac)

Crea file `start.sh`:
```bash
#!/bin/bash

# Avvia backend in background
cd backend
source venv/bin/activate
python run.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Attendi backend
sleep 3

# Avvia frontend
cd ../frontend
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
```

Usa:
```bash
chmod +x start.sh
./start.sh
```

### Avvio Completo (Windows)

Crea file `start.bat`:
```batch
@echo off
start "Backend" cmd /k "cd backend && venv\Scripts\activate && python run.py"
timeout /t 3
start "Frontend" cmd /k "cd frontend && npm run dev"
```

---

## 🆘 Comandi Utili

```bash
# Backend - Resetta database
cd backend
rm instance/fleet_manager.db
python run.py  # Ricrea automaticamente

# Frontend - Pulisci cache
cd frontend
rm -rf node_modules .vite
npm install

# Backend - Vedi dipendenze
pip list

# Frontend - Vedi dipendenze
npm list --depth=0

# Porta occupata? Trova processo
# Linux/Mac:
lsof -i :5000
lsof -i :5173

# Windows:
netstat -ano | findstr :5000
```

---

**Pronto a sviluppare! 🎉**
