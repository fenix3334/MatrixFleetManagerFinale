#!/bin/bash

echo "🚀 Avvio Matrix Fleet Manager..."
echo ""

# Colori
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funzione per controllare se un comando esiste
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verifica dipendenze
echo -e "${BLUE}📋 Verifica dipendenze...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python3 non trovato. Installalo prima.${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js non trovato. Installalo prima.${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ NPM non trovato. Installalo prima.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Tutte le dipendenze sono presenti${NC}"
echo ""

# Avvia Backend
echo -e "${BLUE}🔧 Avvio Backend...${NC}"
cd backend

# Crea venv se non esiste
if [ ! -d "venv" ]; then
    echo "Creazione virtual environment..."
    python3 -m venv venv
fi

# Attiva venv e installa dipendenze
source venv/bin/activate
pip install -q -r requirements.txt

# Avvia backend in background
python run.py &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend avviato (PID: $BACKEND_PID)${NC}"
echo ""

# Torna alla root
cd ..

# Attendi che backend sia pronto
echo -e "${BLUE}⏳ Attendo che backend sia pronto...${NC}"
sleep 3

# Test backend
if curl -s http://localhost:5000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend OK${NC}"
else
    echo -e "${RED}❌ Backend non risponde${NC}"
    kill $BACKEND_PID
    exit 1
fi

echo ""

# Avvia Frontend
echo -e "${BLUE}🎨 Avvio Frontend...${NC}"
cd frontend

# Installa dipendenze se necessario
if [ ! -d "node_modules" ]; then
    echo "Installazione dipendenze frontend..."
    npm install
fi

# Avvia frontend
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend avviato (PID: $FRONTEND_PID)${NC}"

cd ..

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ Matrix Fleet Manager è PRONTO! ✨${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}🌐 Apri il browser e vai a:${NC}"
echo -e "   ${GREEN}http://localhost:5173${NC}"
echo ""
echo -e "${BLUE}📚 Swagger API Docs:${NC}"
echo -e "   ${GREEN}http://localhost:5000/api/docs${NC}"
echo ""
echo -e "${RED}⚠️  Premi CTRL+C per fermare tutto${NC}"
echo ""

# Funzione cleanup
cleanup() {
    echo ""
    echo -e "${BLUE}🛑 Arresto servizi...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Tutto arrestato${NC}"
    exit 0
}

# Trap CTRL+C
trap cleanup SIGINT SIGTERM

# Mantieni lo script in esecuzione
wait
