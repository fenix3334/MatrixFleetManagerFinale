#!/usr/bin/env python3
"""
Script per LEGGERE gli utenti dal database SQLite LOCALE
Usa questo script per vedere chi è registrato nel database
"""
import os
import sys
import sqlite3

# Path del database SQLite locale
SQLITE_DB_PATH = 'instance/matrix_fleet.db'

print(f"📖 LEGGI UTENTI - Database SQLite LOCALE")
print(f"📁 Database: {SQLITE_DB_PATH}\n")

# Verifica che il database esista
if not os.path.exists(SQLITE_DB_PATH):
    print(f"❌ ERRORE: Database non trovato in {SQLITE_DB_PATH}")
    print(f"\n💡 Assicurati di eseguire questo script nella cartella del progetto")
    print(f"   dove si trova la cartella 'instance'")
    sys.exit(1)

print(f"✅ Database SQLite trovato\n")

try:
    # Connessione al database
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    # Leggi tutti gli utenti
    print("=" * 100)
    print("👥 UTENTI REGISTRATI NEL DATABASE:")
    print("=" * 100)
    cursor.execute("""
        SELECT id, username, nucleo, ruolo, attivo, data_creazione
        FROM users
        ORDER BY id
    """)
    users = cursor.fetchall()

    if not users:
        print("⚠️  Nessun utente trovato nel database!")
        print("\n💡 Il database potrebbe essere vuoto o corrotto")
    else:
        print(f"\nTotale utenti: {len(users)}\n")

        for user in users:
            user_id, username, nucleo, ruolo, attivo, data_creazione = user
            stato = "✅ ATTIVO" if attivo else "❌ DISATTIVO"

            print(f"┌─ UTENTE #{user_id}")
            print(f"│  Username:      {username}")
            print(f"│  Ruolo:         {ruolo.upper() if ruolo else 'N/A'}")
            print(f"│  Nucleo:        {nucleo}")
            print(f"│  Stato:         {stato}")
            print(f"│  Creato il:     {data_creazione if data_creazione else 'N/A'}")
            print(f"└─")
            print()

    print("=" * 100)

    # Statistiche database
    print("\n📊 STATISTICHE DATABASE:")
    print("-" * 100)

    # Conta veicoli
    cursor.execute("SELECT COUNT(*) FROM veicoli")
    num_veicoli = cursor.fetchone()[0]
    print(f"🚗 Veicoli:       {num_veicoli}")

    # Conta fornitori
    cursor.execute("SELECT COUNT(*) FROM fornitori")
    num_fornitori = cursor.fetchone()[0]
    print(f"🏭 Fornitori:     {num_fornitori}")

    # Conta manutenzioni
    cursor.execute("SELECT COUNT(*) FROM manutenzioni")
    num_manutenzioni = cursor.fetchone()[0]
    print(f"🔧 Manutenzioni:  {num_manutenzioni}")

    # Conta scadenze
    cursor.execute("SELECT COUNT(*) FROM scadenze")
    num_scadenze = cursor.fetchone()[0]
    print(f"📅 Scadenze:      {num_scadenze}")

    print("-" * 100)

    # Info database
    db_size = os.path.getsize(SQLITE_DB_PATH)
    db_size_kb = db_size / 1024
    print(f"\n💾 Dimensione database: {db_size_kb:.1f} KB ({db_size:,} bytes)")

    conn.close()

    print("\n✅ Lettura completata!")
    print("\n💡 Per resettare la password di un utente, usa: python reset_password_sqlite.py")

except sqlite3.Error as e:
    print(f"\n❌ ERRORE DATABASE SQLite:")
    print(f"   {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ ERRORE:")
    print(f"   {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
