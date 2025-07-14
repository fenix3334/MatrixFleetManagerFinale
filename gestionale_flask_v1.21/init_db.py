#!/usr/bin/env python3
"""
Script di inizializzazione database Matrix Fleet Manager
CON GESTIONE NUCLEI DINAMICI E SEPARAZIONE UTENTI
"""

import os
import sqlite3
from app import create_app
from app.extensions import db
from app.models import Veicolo, Fornitore, Manutenzione, Scadenza, User, Nucleo
from datetime import datetime, date

def clean_field(value):
    """Pulisce i campi opzionali"""
    if value and value.strip():
        return value.strip()
    return None

def add_missing_columns():
    """Aggiunge colonne mancanti al database esistente"""
    try:
        db_path = 'instance/matrix_fleet.db'
        if not os.path.exists(db_path):
            print("Database non trovato, verrà creato nuovo")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Aggiornamento struttura database...")
        
        # Lista colonne da aggiungere (tabella, colonna, tipo, default)
        columns_to_add = [
            ('veicoli', 'carburante_personalizzato', 'VARCHAR(50)', 'NULL'),
            ('veicoli', 'carta_carburante', 'VARCHAR(100)', 'NULL'),
            ('veicoli', 'pin_carburante', 'VARCHAR(20)', 'NULL'),
            ('veicoli', 'societa_noleggio_id', 'INTEGER', 'NULL'),
            ('veicoli', 'nucleo', 'VARCHAR(50)', "'Via Capitel'"),
            
            ('fornitori', 'telefono_2', 'VARCHAR(20)', 'NULL'),
            ('fornitori', 'telefono_3', 'VARCHAR(20)', 'NULL'),
            ('fornitori', 'email_2', 'VARCHAR(100)', 'NULL'),
            ('fornitori', 'email_3', 'VARCHAR(100)', 'NULL'),
            ('fornitori', 'settore_2', 'VARCHAR(100)', 'NULL'),
            ('fornitori', 'settore_3', 'VARCHAR(100)', 'NULL'),
            ('fornitori', 'settore_personalizzato', 'VARCHAR(100)', 'NULL'),
            ('fornitori', 'nucleo', 'VARCHAR(50)', "'Via Capitel'"),
            
            ('manutenzioni', 'stato', 'VARCHAR(20)', "'Da Fare'"),
            ('manutenzioni', 'nucleo', 'VARCHAR(50)', "'Via Capitel'"),
            
            ('scadenze', 'notifica_giorni', 'INTEGER', '30'),
            ('scadenze', 'nucleo', 'VARCHAR(50)', "'Via Capitel'"),
            
            ('users', 'ruolo', 'VARCHAR(20)', "'user'"),  # NUOVO CAMPO RUOLO
        ]
        
        for table, column, col_type, default in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type} DEFAULT {default}")
                print(f"  ✅ Aggiunta colonna {table}.{column}")
            except sqlite3.OperationalError:
                print(f"  ⚠️  Colonna {table}.{column} già presente")
            except Exception as e:
                print(f"  ❌ Errore aggiunta {table}.{column}: {e}")
        
        # Crea tabella nuclei se non esiste
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nuclei (
                id INTEGER PRIMARY KEY,
                nome VARCHAR(100) UNIQUE NOT NULL,
                descrizione VARCHAR(200),
                indirizzo VARCHAR(200),
                telefono VARCHAR(20),
                email VARCHAR(100),
                attivo BOOLEAN DEFAULT 1,
                data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✅ Tabella nuclei verificata/creata")
        
        # Crea tabella users se non esiste
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(120) NOT NULL,
                nucleo VARCHAR(50) DEFAULT 'Via Capitel',
                ruolo VARCHAR(20) DEFAULT 'user',
                attivo BOOLEAN DEFAULT 1,
                data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_accesso DATETIME
            )
        """)
        print("  ✅ Tabella users verificata/creata")
        
        # Imposta nucleo predefinito per dati esistenti
        cursor.execute("UPDATE veicoli SET nucleo = 'Via Capitel' WHERE nucleo IS NULL")
        cursor.execute("UPDATE fornitori SET nucleo = 'Via Capitel' WHERE nucleo IS NULL")
        cursor.execute("UPDATE manutenzioni SET nucleo = 'Via Capitel' WHERE nucleo IS NULL")
        cursor.execute("UPDATE scadenze SET nucleo = 'Via Capitel' WHERE nucleo IS NULL")
        
        # Imposta stato predefinito per manutenzioni esistenti
        cursor.execute("UPDATE manutenzioni SET stato = 'Da Fare' WHERE stato IS NULL")
        
        # Imposta ruolo user per utenti esistenti
        cursor.execute("UPDATE users SET ruolo = 'user' WHERE ruolo IS NULL")
        
        conn.commit()
        conn.close()
        
        print("🎉 Aggiornamento struttura database completato!")
        
    except Exception as e:
        print(f"❌ Errore aggiornamento database: {e}")

def crea_nuclei_default():
    """Crea i nuclei predefiniti se non esistono"""
    nuclei_default = [
        {
            'nome': 'Via Capitel',
            'descrizione': 'Cure Primarie ADI Via del Capitel',
            'indirizzo': 'Via del Capitel, Verona',
            'telefono': '045-123456',
            'email': 'capitel@asl.vr.it'
        },
        {
            'nome': 'Campania',
            'descrizione': 'Cure Primarie ADI Via Campania',
            'indirizzo': 'Via Campania, Verona',
            'telefono': '045-654321',
            'email': 'campania@asl.vr.it'
        }
    ]
    
    for nucleo_data in nuclei_default:
        nucleo_esistente = Nucleo.query.filter_by(nome=nucleo_data['nome']).first()
        if not nucleo_esistente:
            nucleo = Nucleo(**nucleo_data)
            db.session.add(nucleo)
            print(f"  ✅ Nucleo '{nucleo_data['nome']}' creato")
        else:
            print(f"  ⚠️  Nucleo '{nucleo_data['nome']}' già esistente")
    
    db.session.commit()

app = create_app()

with app.app_context():
    # CONTROLLA SE IL DATABASE ESISTE GIÀ
    db_paths = ['instance/matrix_fleet.db', 'matrix_fleet.db', 'fleet_manager.db']
    db_exists = any(os.path.exists(path) for path in db_paths)
    
    if db_exists:
        print("📋 Database esistente trovato!")
        print("🔄 Aggiornamento struttura per separazione nuclei...")
        
        # Aggiorna il database esistente
        add_missing_columns()
        
        # Crea solo tabelle mancanti (non sovrascrive)
        db.create_all()
        
        # CREA NUCLEI PREDEFINITI
        print("\n🏢 Creazione nuclei predefiniti...")
        crea_nuclei_default()
        
        # GESTIONE UTENTE ADMIN
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            # AGGIORNA ADMIN ESISTENTE A RUOLO ADMIN
            if admin_user.ruolo != 'admin':
                admin_user.ruolo = 'admin'
                db.session.commit()
                print("  ✅ Utente admin aggiornato a ruolo amministratore")
            else:
                print("  ✅ Utente admin trovato - password e ruolo mantenuti")
        else:
            # Crea utente admin SOLO se non esiste
            admin = User(
                username='admin',
                nucleo='Via Capitel',
                ruolo='admin',  # IMPORTANTE: ADMIN PUÒ VEDERE TUTTI I NUCLEI
                attivo=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("  ✅ Utente admin creato con ruolo amministratore")
        
        # CREA UTENTI DI ESEMPIO PER I NUCLEI
        utenti_nuclei = [
            {'username': 'capitel', 'nucleo': 'Via Capitel', 'password': 'capitel123'},
            {'username': 'campania', 'nucleo': 'Campania', 'password': 'campania123'}
        ]
        
        for user_data in utenti_nuclei:
            user_esistente = User.query.filter_by(username=user_data['username']).first()
            if not user_esistente:
                user = User(
                    username=user_data['username'],
                    nucleo=user_data['nucleo'],
                    ruolo='user',
                    attivo=True
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"  ✅ Utente '{user_data['username']}' creato per nucleo {user_data['nucleo']}")
            else:
                print(f"  ⚠️  Utente '{user_data['username']}' già esistente")
        
        db.session.commit()
        
        # Verifica dati
        veicoli_count = Veicolo.query.count()
        fornitori_count = Fornitore.query.count()
        manutenzioni_count = Manutenzione.query.count()
        scadenze_count = Scadenza.query.count()
        nuclei_count = Nucleo.query.count()
        users_count = User.query.count()
        
        print(f"\n📊 Database aggiornato con separazione nuclei:")
        print(f"   - Veicoli: {veicoli_count}")
        print(f"   - Fornitori: {fornitori_count}")
        print(f"   - Manutenzioni: {manutenzioni_count}")
        print(f"   - Scadenze: {scadenze_count}")
        print(f"   - Nuclei: {nuclei_count}")
        print(f"   - Utenti: {users_count}")
        
        # Statistiche per nucleo
        for nucleo in Nucleo.query.all():
            v_count = Veicolo.query.filter_by(nucleo=nucleo.nome).count()
            f_count = Fornitore.query.filter_by(nucleo=nucleo.nome).count()
            print(f"   - {nucleo.nome}: {v_count} veicoli, {f_count} fornitori")
        
        print("\n✅ SEPARAZIONE NUCLEI IMPLEMENTATA!")
        print("🆕 Funzionalità aggiunte:")
        print("   - 🏢 Gestione nuclei dinamica")
        print("   - 👤 Ruoli utente (admin/user)")
        print("   - 🔒 Filtri automatici per nucleo")
        print("   - 👑 Admin vede tutti i nuclei")
        print("   - 🆔 Utenti nuclei separati")
        
        print("\n🔑 Credenziali di accesso:")
        print("   - admin/admin123 (vede tutto)")
        print("   - capitel/capitel123 (solo Via Capitel)")
        print("   - campania/campania123 (solo Campania)")
        
    else:
        print("🆕 Primo avvio - Creazione nuovo database...")
        db.create_all()
        
        print("📊 Tabelle create:")
        print("   - Veicoli")
        print("   - Fornitori") 
        print("   - Manutenzioni")
        print("   - Scadenze")
        print("   - Users")
        print("   - Nuclei")  # NUOVA TABELLA
        
        # CREA NUCLEI PREDEFINITI
        print("\n🏢 Creazione nuclei predefiniti...")
        crea_nuclei_default()
        
        # INSERISCI UTENTI CON RUOLI
        print("\n👥 Creazione utenti...")
        
        # Admin
        admin = User(
            username='admin',
            nucleo='Via Capitel',
            ruolo='admin',
            attivo=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Utenti per nuclei
        user_capitel = User(
            username='capitel',
            nucleo='Via Capitel',
            ruolo='user',
            attivo=True
        )
        user_capitel.set_password('capitel123')
        db.session.add(user_capitel)
        
        user_campania = User(
            username='campania',
            nucleo='Campania',
            ruolo='user',
            attivo=True
        )
        user_campania.set_password('campania123')
        db.session.add(user_campania)
        
        db.session.commit()
        
        # INSERISCI DATI DI ESEMPIO CON NUCLEI
        print("\n🔄 Inserimento dati di esempio...")
        
        # Fornitori per Via Capitel
        fornitore1 = Fornitore(
            ragione_sociale="Officina Matrix Auto",
            partita_iva="12345678901",
            citta="Verona",
            cap="37100",
            provincia="VR",
            telefono="045-123456",
            email="info@matrixauto.it",
            settore="Manutenzione auto",
            nucleo="Via Capitel",
            attivo=True
        )
        
        # Fornitori per Campania
        fornitore2 = Fornitore(
            ragione_sociale="Autofficina Centrale",
            partita_iva="09876543210",
            citta="Verona",
            cap="37100",
            provincia="VR",
            telefono="045-654321",
            email="info@centrale.it",
            settore="Riparazione veicoli",
            nucleo="Campania",
            attivo=True
        )
        
        db.session.add_all([fornitore1, fornitore2])
        
        # Veicoli per Via Capitel
        veicolo1 = Veicolo(
            targa="GA302RX",
            marca="Fiat",
            modello="Panda",
            anno_immatricolazione=2020,
            data_immatricolazione=date(2020, 3, 15),
            km_attuali=45000,
            carburante="Benzina",
            cilindrata=1200,
            colore="Bianco",
            nucleo="Via Capitel",
            stato="Attivo"
        )
        
        # Veicoli per Campania
        veicolo2 = Veicolo(
            targa="GH456TY",
            marca="Renault",
            modello="Clio",
            anno_immatricolazione=2019,
            data_immatricolazione=date(2019, 7, 20),
            km_attuali=62000,
            carburante="Diesel",
            cilindrata=1500,
            colore="Grigio",
            nucleo="Campania",
            stato="Attivo"
        )
        
        db.session.add_all([veicolo1, veicolo2])
        db.session.commit()
        
        print("✅ Database creato con separazione nuclei!")
        print("\n🔑 Credenziali di accesso:")
        print("   - admin/admin123 (amministratore - vede tutto)")
        print("   - capitel/capitel123 (utente Via Capitel)")
        print("   - campania/campania123 (utente Campania)")

print("\n🚀 Separazione nuclei completata!")
print("🌐 Avvia il gestionale e testa con utenti diversi")
