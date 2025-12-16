# 🚀 Guida Deploy Online - Matrix Fleet Manager

## Obiettivo
Mettere l'applicazione **ONLINE** su Railway (backend) + Vercel (frontend)

Risultato: **Accessibile da qualsiasi browser, qualsiasi dispositivo, SENZA installare nulla!**

---

## 📋 Cosa Ti Serve (GRATIS)

1. ✅ **Account GitHub** - Hai già il codice qui
2. 🆓 **Account Railway** - https://railway.app (Sign up with GitHub)
3. 🆓 **Account Vercel** - https://vercel.com (Sign up with GitHub)

**NESSUNA CARTA DI CREDITO RICHIESTA** per i piani gratuiti!

---

## 🔧 PARTE 1: Deploy Backend su Railway

### Step 1.1: Crea Account Railway
1. Vai su **https://railway.app**
2. Clicca **"Start a New Project"**
3. Clicca **"Login with GitHub"**
4. Autorizza Railway ad accedere a GitHub

### Step 1.2: Deploy dal Repository
1. Clicca **"New Project"**
2. Seleziona **"Deploy from GitHub repo"**
3. Cerca e seleziona: **MatrixFleetManagerFinale**
4. Railway rileverà automaticamente Python

### Step 1.3: Configura Directory Backend
1. Nel progetto Railway, vai su **Settings**
2. Trova **"Root Directory"**
3. Imposta: `backend`
4. Salva

### Step 1.4: Aggiungi Database PostgreSQL
1. Clicca **"+ New"** nel progetto
2. Seleziona **"Database"** → **"PostgreSQL"**
3. Railway crea automaticamente il database

### Step 1.5: Configura Variabili Ambiente
1. Vai nella sezione **"Variables"** del servizio backend
2. Clicca **"+ Add Variable"**
3. Aggiungi queste variabili:

```
DATABASE_URL = ${{Postgres.DATABASE_URL}}
JWT_SECRET_KEY = prod-jwt-secret-2024-cambiaQuestoValore
SECRET_KEY = prod-flask-secret-2024-cambiaQuestoValore
FLASK_ENV = production
PORT = 5000
```

**IMPORTANTE:** Nella variabile `DATABASE_URL`, clicca sul menu e seleziona "Reference" → "Postgres" → "DATABASE_URL"

### Step 1.6: Deploy!
1. Railway inizia automaticamente il deploy
2. Aspetta 2-3 minuti
3. Quando vedi ✅ "Success", il backend è online!

### Step 1.7: Ottieni URL Backend
1. Vai su **Settings** del servizio
2. Nella sezione **"Networking"**, clicca **"Generate Domain"**
3. Copia l'URL (esempio: `matrix-backend-production.up.railway.app`)
4. **SALVA QUESTO URL** - ti servirà per il frontend!

### Step 1.8: Testa Backend
Apri nel browser:
```
https://il-tuo-url-railway.up.railway.app/health
```

Dovresti vedere:
```json
{"status":"ok","message":"Matrix Fleet Manager API is running"}
```

✅ **Backend ONLINE!**

---

## 🌐 PARTE 2: Deploy Frontend su Vercel

### Step 2.1: Crea Account Vercel
1. Vai su **https://vercel.com**
2. Clicca **"Sign Up"**
3. Scegli **"Continue with GitHub"**
4. Autorizza Vercel

### Step 2.2: Import Progetto
1. Dalla dashboard Vercel, clicca **"Add New..."** → **"Project"**
2. Clicca **"Import Git Repository"**
3. Cerca e seleziona **MatrixFleetManagerFinale**
4. Clicca **"Import"**

### Step 2.3: Configura Build Settings
Nella schermata di configurazione:

1. **Framework Preset:** Vite
2. **Root Directory:** Clicca "Edit" e seleziona `frontend`
3. **Build Command:** `npm run build` (già impostato)
4. **Output Directory:** `dist` (già impostato)

### Step 2.4: Aggiungi Variabili Ambiente
1. Espandi **"Environment Variables"**
2. Aggiungi questa variabile:

```
Name: VITE_API_URL
Value: https://il-tuo-url-railway.up.railway.app/api
```

**IMPORTANTE:** Sostituisci `il-tuo-url-railway.up.railway.app` con l'URL di Railway che hai salvato prima!

### Step 2.5: Deploy!
1. Clicca **"Deploy"**
2. Aspetta 2-3 minuti mentre Vercel:
   - Installa dipendenze
   - Builda il progetto
   - Deploya online
3. Quando vedi ✅ "Deployment Ready", il frontend è online!

### Step 2.6: Apri l'Applicazione
1. Clicca sul pulsante **"Visit"**
2. Si apre il tuo Matrix Fleet Manager ONLINE!
3. L'URL sarà tipo: `https://matrix-fleet-manager.vercel.app`

✅ **Frontend ONLINE!**

---

## 🔗 PARTE 3: Configurazione Finale Backend

### Step 3.1: Aggiorna CORS nel Backend
1. Torna su **Railway**
2. Vai nelle **Variables** del backend
3. Aggiungi/Aggiorna:

```
FRONTEND_URL = https://il-tuo-url-vercel.vercel.app
```

### Step 3.2: Rideploy Backend
1. Vai su **Deployments**
2. Clicca sui 3 puntini dell'ultimo deployment
3. Clicca **"Redeploy"**
4. Aspetta che finisca

---

## 🎉 COMPLETATO!

La tua applicazione è **ONLINE**!

### 🌐 Accedi da qualsiasi dispositivo:
```
https://il-tuo-url-vercel.vercel.app
```

### 📱 Testa su:
- ✅ PC Windows (browser)
- ✅ PC Mac (browser)
- ✅ Smartphone
- ✅ Tablet
- ✅ Qualsiasi dispositivo con browser

### 🔐 Primo Accesso
1. Apri l'URL Vercel nel browser
2. Clicca **"Registrati"**
3. Crea primo utente admin:
   - Username: `admin`
   - Password: `admin123`
   - Nucleo: `Via Capitel`
4. Accedi alla Dashboard!

---

## 📊 Cosa Puoi Fare Ora

- ✅ Gestire veicoli da qualsiasi posto
- ✅ Condividere URL con colleghi
- ✅ Accedere da casa/ufficio/mobile
- ✅ Dati salvati su PostgreSQL cloud
- ✅ ZERO costi (piano gratuito)

---

## 🔧 Limiti Piano Gratuito

**Railway:**
- 500 ore/mese di runtime (più che sufficienti)
- 1GB RAM
- 1GB storage database

**Vercel:**
- 100GB bandwidth/mese
- Unlimited deployments
- Automatic HTTPS

**Entrambi:** Più che sufficienti per un gestionale aziendale!

---

## 🆘 Troubleshooting

### Backend non risponde
1. Vai su Railway → Deployments
2. Clicca sull'ultimo deployment
3. Controlla i **Logs** per errori
4. Verifica che tutte le variabili ambiente siano impostate

### Frontend mostra errori CORS
1. Verifica che `FRONTEND_URL` su Railway sia corretto
2. Rideploy il backend dopo aver aggiunto la variabile

### Database connection error
1. Verifica che `DATABASE_URL` sia collegato al Postgres
2. In Railway, verifica che Postgres sia attivo

### Login non funziona
1. Apri Console Browser (F12)
2. Controlla Network tab per errori
3. Verifica che `VITE_API_URL` su Vercel punti al backend Railway

---

## 📝 URL da Salvare

```
Backend API:     https://_______________.up.railway.app
Frontend Web:    https://_______________.vercel.app
Swagger Docs:    https://_______________.up.railway.app/api/docs
```

---

## 🔄 Aggiornamenti Futuri

Quando aggiorni il codice:

1. **Push su GitHub** (come sempre)
2. **Railway** si aggiorna automaticamente
3. **Vercel** si aggiorna automaticamente

ZERO deploy manuali! 🎉

---

## 🎯 Prossimi Step

- [ ] Deploy completato
- [ ] Primo utente creato
- [ ] Aggiunto primo veicolo
- [ ] Condiviso URL con team
- [ ] (Opzionale) Custom domain

---

**Tutto online e accessibile! 🚀**
