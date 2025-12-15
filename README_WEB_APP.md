# Matrix Fleet Manager - Web App

**Gestionale Parco Auto Aziendale - Versione Moderna Web App**

## 🎯 Architettura

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Frontend (Vue.js 3 + Vite)                        │
│  - Interfaccia moderna e responsive                │
│  - Tailwind CSS per lo styling                     │
│  - Pinia per state management                      │
│  - Vue Router per routing                          │
│                                                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ HTTP/REST + JWT
                   │
┌──────────────────┴──────────────────────────────────┐
│                                                     │
│  Backend API (Flask-RESTX)                         │
│  - REST API con Swagger docs                       │
│  - JWT authentication                              │
│  - SQLAlchemy ORM                                  │
│  - PostgreSQL/SQLite database                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 📁 Struttura Progetto

```
MatrixFleetManagerFinale/
├── backend/                    # Backend API REST
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   └── veicoli.py     # API veicoli
│   │   ├── auth/              # Autenticazione JWT
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── models.py          # Modelli database
│   │   ├── schemas.py         # Marshmallow schemas
│   │   └── __init__.py        # Factory app
│   ├── instance/              # Database SQLite
│   ├── config.py              # Configurazione
│   ├── requirements.txt       # Dipendenze Python
│   ├── .env                   # Variabili ambiente
│   └── run.py                 # Entry point
│
├── frontend/                   # Frontend Vue.js
│   ├── src/
│   │   ├── components/        # Componenti riutilizzabili
│   │   ├── views/             # Pagine principali
│   │   │   ├── Login.vue
│   │   │   ├── Dashboard.vue
│   │   │   └── Veicoli.vue
│   │   ├── stores/            # Pinia stores
│   │   │   ├── auth.js
│   │   │   └── veicoli.js
│   │   ├── services/          # API client
│   │   │   └── api.js
│   │   ├── router/            # Vue Router
│   │   │   └── index.js
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
│
└── app/                        # Vecchia app Flask (mantenuta)
```

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Entra nella directory backend
cd backend

# Crea virtual environment
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# Installa dipendenze
pip install -r requirements.txt

# Avvia server (sviluppo)
python run.py
```

Backend disponibile su: **http://localhost:5000**
Swagger docs: **http://localhost:5000/api/docs**

### 2. Frontend Setup

```bash
# Entra nella directory frontend
cd frontend

# Installa dipendenze
npm install

# Avvia dev server
npm run dev
```

Frontend disponibile su: **http://localhost:5173**

## 🔐 Autenticazione

### Registrazione Primo Utente

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123",
    "nucleo": "Via Capitel",
    "ruolo": "admin"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Risposta:
```json
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "nucleo": "Via Capitel",
    "ruolo": "admin"
  }
}
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login` - Login utente
- `POST /api/auth/register` - Registrazione
- `GET /api/auth/me` - Info utente corrente
- `POST /api/auth/refresh` - Refresh token

### Veicoli
- `GET /api/veicoli` - Lista veicoli
- `POST /api/veicoli` - Crea veicolo
- `GET /api/veicoli/{id}` - Dettagli veicolo
- `PUT /api/veicoli/{id}` - Aggiorna veicolo
- `DELETE /api/veicoli/{id}` - Elimina veicolo
- `GET /api/veicoli/stats` - Statistiche

## 🎨 Frontend

### Store Pinia

**Auth Store** (`stores/auth.js`):
- `login(username, password)` - Login
- `register(username, password, nucleo)` - Registrazione
- `logout()` - Logout
- `fetchCurrentUser()` - Refresh user info
- `isAuthenticated` - Check auth status
- `isAdmin` - Check admin role

**Veicoli Store** (`stores/veicoli.js`):
- `fetchVeicoli(filters)` - Carica lista
- `fetchVeicolo(id)` - Carica dettaglio
- `createVeicolo(data)` - Crea nuovo
- `updateVeicolo(id, data)` - Aggiorna
- `deleteVeicolo(id)` - Elimina
- `fetchStats()` - Carica statistiche

### Routing

- `/login` - Pagina login/registrazione
- `/` - Dashboard principale
- `/veicoli` - Gestione veicoli

## 🔧 Configurazione

### Backend (.env)

```env
DATABASE_URL=sqlite:///instance/fleet_manager.db
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
FLASK_ENV=development
SECRET_KEY=your-flask-secret
FRONTEND_URL=http://localhost:5173
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:5000/api
```

## 📦 Deploy

### Backend (Railway)

```bash
# Crea Procfile
echo "web: python run.py" > backend/Procfile

# Push su Railway
railway up
```

Variabili ambiente:
- `DATABASE_URL` - PostgreSQL URL
- `JWT_SECRET_KEY` - Secret per JWT
- `SECRET_KEY` - Flask secret
- `FRONTEND_URL` - URL frontend

### Frontend (Vercel)

```bash
cd frontend
vercel --prod
```

Variabili ambiente:
- `VITE_API_URL` - URL API backend

## 🗄️ Database

I modelli sono compatibili con il database esistente. Per migrare:

```bash
cd backend
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

## 🛠️ Sviluppo

### Aggiungere nuovo modulo

1. **Backend**: Crea API in `backend/app/api/`
2. **Schema**: Aggiungi schema in `backend/app/schemas.py`
3. **Frontend Store**: Crea store in `frontend/src/stores/`
4. **Frontend View**: Crea vista in `frontend/src/views/`
5. **Router**: Aggiungi route in `frontend/src/router/index.js`

### Esempio: Modulo Manutenzioni

```python
# backend/app/api/manutenzioni.py
from flask_restx import Namespace, Resource

api = Namespace('manutenzioni', description='Manutenzioni')

@api.route('/')
class ManutenzioniList(Resource):
    @jwt_required()
    def get(self):
        # Lista manutenzioni
        pass
```

## 📚 Stack Tecnologico

### Frontend
- **Vue.js 3.5** - Framework progressivo
- **Vite 7** - Build tool ultra-veloce
- **Vue Router 4** - Routing
- **Pinia 2** - State management
- **Axios 1.7** - HTTP client
- **Tailwind CSS 3** - Utility-first CSS

### Backend
- **Flask 3.0** - Micro-framework Python
- **Flask-RESTX 1.3** - REST API + Swagger
- **Flask-JWT-Extended 4.6** - JWT authentication
- **SQLAlchemy 3.1** - ORM
- **Marshmallow 3.20** - Serialization
- **PostgreSQL/SQLite** - Database

## 📝 Note

- Il codice legacy in `/app` è mantenuto per compatibilità
- Database SQLite esistente può essere riutilizzato
- Sistema multi-tenant tramite campo `nucleo`
- JWT con refresh token per sessioni sicure
- CORS configurato per cross-origin requests

## 🔗 Link Utili

- Swagger Docs: http://localhost:5000/api/docs
- Frontend Dev: http://localhost:5173
- Backend API: http://localhost:5000/api

## 📧 Supporto

Per problemi o domande, consulta la documentazione o apri una issue.

---

**Matrix Fleet Manager v1.0** - Gestionale Parco Auto Moderna Web App
